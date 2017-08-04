import cobra
import re
import logging

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

    # Build a draft model for the organism.
    model = template.reconstruct(summary['genome_id'], features, biomass_id,
                                 model_name=summary['organism_name'],
                                 gc_content=gc_content,
                                 annotation='PATRIC')
    LOGGER.info('Reconstructed draft model with %d reactions, %d metabolites, %d genes',
                len(model.reactions), len(model.metabolites), len(model.genes))

    # Generate likelihood-based gene annotation for the organism.
    LOGGER.info('Started likelihood-based annotation')
    likelihood = LikelihoodAnnotation(search_program_path, search_db_path, fid_role_path, work_folder)
    reaction_likelihoods = likelihood.calculate(genome_id, features, template)
    LOGGER.info('Finished likelihood-based annotation')

    # Update model with reaction likelihoods.
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
    # print(not_found)
    # print(model.slim_optimize())

    # Gap fill the draft model.
    # LOGGER.info('Started building universal model from template for gap fill')
    # universal = template.to_model()
    # LOGGER.info('Finished building universal model from template')
    #
    # LOGGER.info('Started gap fill optimization')
    # if solver is not None:
    #     model.solver = solver
    # x = cobra.flux_analysis.gapfill(model, universal)
    # print(x)
    # LOGGER.info('Finished gap fill optimization')
    # x = likelihood_gapfill(model, universal, rxn_likes, clean_exchange_rxns=True)
    # Just dump the gapfill code here or make a function?

    return model


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


# Need a function to analyze genome annotation vs. hits in template roles.
# Fuzzy match and EC number hits.
