import logging
from warnings import warn

from .genome import get_genome_summary, get_genome_features
from .likelihood import LikelihoodAnnotation

# Logger for this module
LOGGER = logging.getLogger(__name__)


def reconstruct_model_from_patric(genome_id, template, biomass_id, **kwargs):
    """ Download a PATRIC genome for an organism and reconstruct a model from a template.

    Parameters
    ----------
    genome_id : str
        ID of genome for organism in PATRIC
    template : TemplateModel
        Template model for type of organism
    biomass_id : str
        ID of biomass entity in template model used to create biomass objective
    kwargs : dict
        Keyword arguments to pass along to reconstruct_model()

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
        kwargs['gc_content'] = summary['gc_content']
        if kwargs['gc_content'] > 1.0:
            kwargs['gc_content'] /= 100.0
    except KeyError:
        kwargs['gc_content'] = 0.5
        LOGGER.warn('GC content not found in genome summary, using default value of {0}'
                    .format(kwargs['gc_content']))
    LOGGER.info('Finished download of %d features for genome %s', len(features), genome_id)

    # Reconstruct a model for the organism.
    model_id = genome_id
    if 'model_id' in kwargs:
        model_id = kwargs['model_id']
    return reconstruct_model(model_id, features, template, biomass_id, kwargs)


def reconstruct_model(model_id, features, template, biomass_id, model_name=None,
                      gc_content=0.5, search_program_path='usearch',
                      search_db_path='protein.udb', fid_role_path='otu_fid_role.tsv',
                      work_folder=".", cutoff=None):
    """ Reconstruct a model for an organism from a template model.

    Parameters
    ----------
    model_id : str
        ID for model
    features : list
        List of genome features from organism
    template : TemplateModel
        Template model for type of organism
    biomass_id : str
        ID of biomass entity in template model used to create biomass objective
    model_name : str, optional
        Name for model
    gc_content : float, optional
        Percent GC content in genome of organism (value between 0 and 1)
    search_program_path : str, optional
        Path to search program executable
    search_db_path : str, optional
        Path to search database file
    fid_role_path : str, optional
        Path to feature ID to role ID mapping file
    work_folder : str, optional
        Path to folder for storing intermediate files
    cutoff : float, optional
        Add reactions with a likelihood value greater than or equal to the
        cutoff (value should be greater than 0 and less than 1).
    """

    # Build a draft model for the organism.
    LOGGER.info('Started reconstruction of draft model for %s', model_name)
    model = template.reconstruct(model_id, features, biomass_id, model_name=model_name,
                                 gc_content=gc_content, annotation='PATRIC')
    LOGGER.info('Finished reconstruction of draft model with %d reactions, %d metabolites, %d genes',
                len(model.reactions), len(model.metabolites), len(model.genes))

    # Generate likelihood-based gene annotation for the organism.
    LOGGER.info('Started likelihood-based annotation')
    likelihood = LikelihoodAnnotation(search_program_path, search_db_path, fid_role_path, work_folder)
    reaction_likelihoods = likelihood.calculate(model_id, features, template.complexes_to_roles,
                                                template.reactions_to_complexes)
    LOGGER.info('Finished likelihood-based annotation')

    # Update model with reaction likelihoods. Reaction IDs in returned dictionary
    # are in template model format.
    num_set = 0
    num_added = 0
    more_reactions = list()
    num_not_found = 0
    for rxn_id in reaction_likelihoods:
        template_reaction = template.reactions.get_by_id(rxn_id)
        try:
            reaction = model.reactions.get_by_id(template_reaction.model_id)
            reaction.notes['likelihood'] = reaction_likelihoods[rxn_id]['likelihood']
            reaction.notes['likelihood_str'] = '{0}'.format(reaction.notes['likelihood'])
            num_set += 1
        except KeyError:
            if cutoff is not None and reaction_likelihoods[rxn_id]['likelihood'] >= cutoff:
                more_reactions.append(template_reaction.create_model_reaction(template.compartments))
                num_added += 1
            else:
                num_not_found += 1
    if len(more_reactions) > 0:
        model.add_reactions(more_reactions)
    LOGGER.info('Set likelihood for %d reactions, added %d reactions, %d reactions not set',
                num_set, num_added, num_not_found)
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
                warn('Exchange reaction {0} for metabolite {1} has invalid bounds {2}'
                     .format(rxn.id, met.name, rxn.bounds))
        except KeyError:
            warn('Exchange reaction missing for metabolite {0} ({1})'.format(met.id, met.name))
        transport = False
        for rxn in met.reactions:
            if len(rxn.compartments) > 1:
                if extracellular in rxn.compartments and to_compartment in rxn.compartments:
                    transport = True
                    if rxn.lower_bound == 0. or rxn.upper_bound == 0.:
                        warn('Transport reaction {0} for metabolite {1} has invalid bounds {2}'
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
