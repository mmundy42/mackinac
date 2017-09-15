import cobra
import re
import logging
from warnings import warn

from .genome import get_genome_summary, get_genome_features
from .likelihood import LikelihoodAnnotation

# Logger for this module
LOGGER = logging.getLogger(__name__)


def reconstruct_model_from_patric(genome_id, template, biomass_id, search_program_path,
                                  search_db_path, fid_role_path, solver=None, work_folder=None):
    """ Reconstruct a model for an organism from a PATRIC genome.

    Parameters
    ----------
    genome_id : str
        ID of genome for organism in PATRIC
    template : TemplateModel
        Template model for type of organism
    biomass_id : str
        ID of biomass entity in template model used to create biomass objective
    search_program_path : str
        Path to search program executable
    search_db_path : str
        Path to search database file
    fid_role_path : str
        Path to feature ID to role ID mapping file
    solver : str
        Name of solver (must be supported by optlang and installed on your system)
    work_folder : str, optional
        Path to folder for storing intermediate files

    Returns
    -------
    cobra.core.Model
        Model reconstructed from organism's genome
    """

    # Get the genome summary and features from PATRIC.
    LOGGER.info('Started download of summary and features for genome %s', genome_id)
    summary = get_genome_summary(genome_id)
    features = get_genome_features(genome_id, 'PATRIC')
    try:
        gc_content = summary['gc_content']
        if gc_content > 1.0:
            gc_content /= 100.0
    except KeyError:
        gc_content = 0.5
        LOGGER.warn('GC content not found in genome summary, using default value of {0}'
                    .format(gc_content))
    LOGGER.info('Finished download of %d features for genome %s', len(features), genome_id)


def reconstruct_model(model_id, model_name, features, gc_content, template, biomass_id, search_program_path,
                      search_db_path, fid_role_path, work_folder):
    """ Reconstruct a model for an organism.

    Parameters
    ----------
    model_id : str
        ID of model
    model_name : str
        Name of model
    features : list
        List of genome features from organism
    gc_content : float
        Percent GC content in genome of organism
    template : TemplateModel
        Template model for type of organism
    biomass_id : str
        ID of biomass entity in template model used to create biomass objective
    search_program_path : str
        Path to search program executable
    search_db_path : str
        Path to search database file
    fid_role_path : str
        Path to feature ID to role ID mapping file
    work_folder : str
        Path to folder for storing intermediate files
    """

    # Build a draft model for the organism.
    model = template.reconstruct(model_id, features, biomass_id,
                                 model_name=model_name,
                                 gc_content=gc_content,
                                 annotation='PATRIC')
    LOGGER.info('Reconstructed draft model with %d reactions, %d metabolites, %d genes',
                len(model.reactions), len(model.metabolites), len(model.genes))

    # Generate likelihood-based gene annotation for the organism.
    LOGGER.info('Started likelihood-based annotation')
    likelihood = LikelihoodAnnotation(search_program_path, search_db_path, fid_role_path, work_folder)
    reaction_likelihoods = likelihood.calculate(model_id, features, template.complexes_to_roles,
                                                template.reactions_to_complexes)
    LOGGER.info('Finished likelihood-based annotation')

    # Update model with reaction likelihoods. Do this after gap fill?
    more_reactions = list()
    not_found = 0
    for rxn_id in reaction_likelihoods:
        template_reaction = template.reactions.get_by_id(rxn_id)
        try:
            reaction = model.reactions.get_by_id(template_reaction.model_id)
            reaction.notes['likelihood'] = reaction_likelihoods[rxn_id]['likelihood']
            reaction.notes['likelihood_str'] = '{0}'.format(reaction.notes['likelihood'])
        except KeyError:
            not_found += 1
        if reaction_likelihoods[rxn_id]['likelihood'] >= 0.5 and not model.reactions.has_id(template_reaction.model_id):
            more_reactions.append(template_reaction.create_model_reaction(template.compartments))
    model.add_reactions(more_reactions)

    return model


def check_boundary_metabolites(model, extracellular='e', to_compartment='c'):
    """ Check that all boundary metabolites have a path from the boundary to a specific compartment.

    Parameters
    ----------
    model : cobra.core.Model
        Model to check
    extracellular : str, optional
        ID of extracellular compartment (the compartment at the boundary)
    to_compartment : str, optional
        ID of specific compartment (typically cytosol)
    """

    # Get the list of metabolites in the extracellular compartment.
    metabolites = model.metabolites.query(lambda x: x == extracellular, 'compartment')

    # Look for reactions that move a metabolite from the boundary to the
    # specified compartment.
    num_valid = 0
    for met in metabolites:
        exchange_id = 'EX_{}'.format(met.id)  # Assume standard naming convention
        try:
            rxn = model.reactions.get_by_id(exchange_id)
            if not rxn.boundary:
                warn('Reaction {0} for metabolite {1} is not an exchange reaction'
                     .format(rxn.id, met.name))
            if rxn.lower_bound == 0. or rxn.upper_bound == 0.:
                warn('Reaction {0} for metabolite {1} has invalid bounds {2}'
                     .format(rxn.id, met.name, rxn.bounds))
        except KeyError:
            warn('Exchange reaction missing for metabolite {0} ({1})'.format(met.id, met.name))
        transport = False
        for rxn in met.reactions:
            if len(rxn.compartments) > 1:
                if extracellular in rxn.compartments and to_compartment in rxn.compartments:
                    transport = True
                    if rxn.lower_bound == 0. or rxn.upper_bound == 0.:
                        warn('Reaction {0} for metabolite {1} has invalid bounds {2}'
                             .format(rxn.id, met.name, rxn.bounds))
        if not transport:
            warn('Metabolite {0} ({1}) has no transport reaction to compartment {2}'
                 .format(met.id, met.name, to_compartment))
        else:
            num_valid += 1

    if len(metabolites) - num_valid != 0:
        warn('{0} metabolites do not have a path from boundary to comparment {1}'
             .format(len(metabolites) - num_valid, to_compartment))
    return num_valid


def likelihood_gapfill(model, universal_model, reaction_probabilities, clean_exchange_rxns=True,
                       default_penalties=None, dm_rxns=False, ex_rxns=False, **solver_parameters):
    """
    Gapfill a model using probabilistic weights
    :param default_penalties:
    :param model: cobra Model object, the model to be gapfilled
    :param universal_model: cobra Model object representing the database of reactions to choose from
    :param reaction_probabilities: reaction_probabilities dictionary
    :return:
    """
    universal_model = universal_model.copy()
    model = clean_exchange_reactions(model) if clean_exchange_rxns else model.copy()
    if default_penalties is None:
        default_penalties = {'Universal': 1, 'Exchange': 100, 'Demand': 1, 'Reverse': 75}
    penalties = default_penalties
    reactions_to_remove = []
    for r in universal_model.reactions:
        if model.reactions.has_id(r.id):
            reactions_to_remove.append(r)
            penalties[r.id] = 0  # In the model
        elif r.id in reaction_probabilities:
            penalties[r.id] = max(0, 1 - reaction_probabilities[r.id]) * \
                              (penalties[r.id] if r.id in penalties else 1)
    universal_model.remove_reactions(reactions_to_remove)
    return cobra.flux_analysis.gapfill(model, universal_model, penalties=penalties, demand_reactions=dm_rxns,
                                       exchange_reactions=ex_rxns, **solver_parameters)


def clean_exchange_reactions(model, regex='.*_e([0-9]*)$'):
    model = model.copy()
    compound_regex = re.compile(regex)
    mets_to_clean = [m for m in model.metabolites if compound_regex.match(m.id)]
    for m in mets_to_clean:
        m.remove_from_model()
    return model
