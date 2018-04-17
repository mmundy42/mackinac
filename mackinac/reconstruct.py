from warnings import warn
from os.path import join

from cobra.core import Model
from cobra.flux_analysis.gapfilling import GapFiller

from .likelihood import LikelihoodAnnotation
from .templates.util import read_json_file, create_boundary
from .templates.universal import create_universal_metabolite, metabolite_json_schema, \
    create_universal_reaction, reaction_json_schema, resolve_universal_reactions
from .templates.templatemodel import TemplateModel, TemplateError
from .logger import LOGGER


def create_template_model(universal_folder, template_folder, template_id, name, type='growth',
                          domain='Bacteria', exclude=None, verbose=False, validate=False):
    """ Create a template model object from ModelSEED source files.

    The universal folder must contain these files: (1) "metabolites.json", (2) "reactions.json".

    The template folder must contain these files: (1) "biomass_metabolites.tsv",
    (2) "biomasses.tsv", (3) "compartments.tsv" , (4) "complexes.tsv", (5) "reactions.tsv",
    (6) "roles.tsv". Each file has required fields that are needed to create a template
    model.

    Parameters
    ----------
    universal_folder : str
        Path to folder containing files with universal data
    template_folder : str
        Path to folder containing files with template data
    template_id : str
        ID of template model
    name : str
        Name of template model
    type : str, optional
        Type of template model (usually "growth")
    domain : str, optional
        Domain of organisms represented by template model
    exclude : set of str, {"pseudo", "status"}, optional
        Types of reactions to exclude from template, where "pseudo" means to exclude
        reactions with no metabolites, "status" means to exclude reactions where
        reaction status is not OK
    verbose : bool, optional
        When True, show all warning messages
    validate : bool, optional
        When True, check for common problems with universal reactions

    Returns
    -------
    TemplateModel
         Template model created from source files
    """

    # Get the universal metabolites and reactions by processing the source files.
    # Note that metabolites and reactions marked as obsolete are not included.
    universal_metabolites = read_json_file(join(universal_folder, 'metabolites.json'),
                                           metabolite_json_schema,
                                           create_universal_metabolite)
    universal_reactions = read_json_file(join(universal_folder, 'reactions.json'),
                                         reaction_json_schema,
                                         create_universal_reaction)
    resolve_universal_reactions(universal_reactions, universal_metabolites, validate)

    # Create an empty template model and initialize it from source files.
    template_model = TemplateModel(template_id, name, type, domain)
    template_model.init_from_files(
        join(template_folder, 'compartments.tsv'),
        join(template_folder, 'biomasses.tsv'),
        join(template_folder, 'biomass_metabolites.tsv'),
        join(template_folder, 'reactions.tsv'),
        join(template_folder, 'complexes.tsv'),
        join(template_folder, 'roles.tsv'),
        universal_metabolites,
        universal_reactions,
        exclude,
        verbose
    )

    return template_model


def calculate_likelihoods(genome_id, features, template, search_program_path='usearch',
                          search_db_path='protein.udb', fid_role_path='otu_fid_role.tsv',
                          work_folder='.'):
    """ Calculate reaction likelihoods for an organism using annotated features and a template model.

    Parameters
    ----------
    genome_id : str
        ID of genome (just for naming temporary files)
    features : list
        List of genome features from organism
    template : TemplateModel
        Template model for type of organism
    search_program_path : str, optional
        Path to search program executable
    search_db_path : str, optional
        Path to search database file
    fid_role_path : str, optional
        Path to feature ID to role ID mapping file
    work_folder : str, optional
        Path to folder for storing intermediate files

    Returns
    -------
    LikelihoodAnnotation
        Likelihood-based gene annotation for organism
    """

    LOGGER.info('Started likelihood-based annotation for %s', genome_id)
    likelihoods = LikelihoodAnnotation(search_program_path, search_db_path, fid_role_path, work_folder)
    likelihoods.calculate(genome_id, features, template.complexes_to_roles, template.reactions_to_complexes)
    LOGGER.info('Finished likelihood-based annotation for %s', genome_id)
    return likelihoods


def reconstruct_model_from_features(features, template, model_id, biomass_id, model_name=None, gc_content=0.5):
    """ Reconstruct a model for an organism using annotated features and a template model.

    Parameters
    ----------
    features : list
        List of genome features from organism
    template : TemplateModel
        Template model for type of organism
    model_id : str
        ID for model
    biomass_id : str
        ID of biomass entity in template model used to create biomass objective
    model_name : str, optional
        Name for model
    gc_content : float, optional
        Percent GC content in genome of organism (value between 0 and 1)

    Returns
    -------
    cobra.core.Model
        Model reconstructed from organism's annotated features
    """

    # Build a draft model for the organism.
    LOGGER.info('Started reconstruction of draft model for %s', model_name)
    model = template.reconstruct(model_id, features, biomass_id, model_name=model_name,
                                 gc_content=gc_content, annotation='PATRIC')
    LOGGER.info('Finished reconstruction of draft model with %d reactions, %d metabolites, %d genes',
                len(model.reactions), len(model.metabolites), len(model.genes))
    return model


def reconstruct_model_from_likelihoods(likelihoods, template, model_id, biomass_id,
                                       model_name=None, gc_content=0.5, cutoff=0.1):
    """ Reconstruct a model for an organism using annotated features and a template model.

    Parameters
    ----------
    likelihoods : LikelihoodAnnotation
        Likelihood-based gene annotation for organism
    template : TemplateModel
        Template model for type of organism
    model_id : str
        ID for model
    biomass_id : str
        ID of biomass entity in template model used to create biomass objective
    model_name : str, optional
        Name for model
    gc_content : float, optional
        Percent GC content in genome of organism (value between 0 and 1)
    cutoff : float, optional
        Add reactions with a likelihood value greater than or equal to the
        cutoff (value should be greater than 0 and less than 1).

    Returns
    -------
    cobra.core.Model
        Model reconstructed from organism's likelihood-based annotation
    """

    # Create a new cobra.core.Model object.
    model = Model(model_id, name=model_name)

    # Find all of the reactions that have a likelihood value greater than the cutoff.
    reaction_list = list()
    reaction_likelihoods = likelihoods.reaction_values
    for rxn_id in reaction_likelihoods:
        if reaction_likelihoods[rxn_id]['likelihood'] >= cutoff:
            template_reaction = template.reactions.get_by_id(rxn_id)
            model_reaction = template_reaction.create_model_reaction(template.compartments)
            model_reaction.notes['likelihood'] = reaction_likelihoods[rxn_id]['likelihood']
            model_reaction.notes['likelihood_str'] = '{0}'.format(model_reaction.notes['likelihood'])
            reaction_list.append(model_reaction)
    if len(reaction_list) == 0:
        raise ValueError('There are no reactions with a likelihood greater than cutoff of {}'.format(cutoff))
    model.add_reactions(reaction_list)

    # Add exchange reactions for all metabolites in the extracellular compartment.
    LOGGER.info('Started adding exchange reactions to model')
    extracellular = model.metabolites.query(lambda x: x == 'e', 'compartment')
    exchanges = [create_boundary(met) for met in extracellular]
    model.add_reactions(exchanges)
    LOGGER.info('Finished adding %d exchange reactions to model', len(exchanges))

    # Add a magic exchange reaction for the special biomass metabolite which seems to be
    # required for ModelSEED models and which we know has id "cpd11416_c".
    # @todo Move this since it is specific to ModelSEED?
    model.add_reactions([create_boundary(template.metabolites.get_by_id('cpd11416_c'), type='sink')])

    # Create a biomass reaction, add it to the model, and make it the objective.
    LOGGER.info('Started adding biomass reaction')
    try:
        biomass_reaction = template.biomasses.get_by_id(biomass_id).create_objective(gc_content)
    except KeyError:
        raise TemplateError('Biomass "{0}" does not exist in template model'.format(biomass_id))
    model.add_reactions([biomass_reaction])
    biomass_reaction.objective_coefficient = 1.0
    LOGGER.info('Finished adding biomass reaction {0} as objective'.format(biomass_reaction.id))

    # Add compartments to the model (this is fixed in a future version of cobra).
    for compartment in template.compartments:
        model.compartments[compartment.model_id] = compartment.name

    return model


def gapfill_model(model, template, method='default', penalties=None, demand_reactions=True,
                  exchange_reactions=False, likelihoods=None):

    # Convert template to a COBRA model to use as universal model with reactions
    # that can be used to complete the model.
    LOGGER.info('Started gap fill for model "%s"', model.id)
    universal_model = template.to_cobra_model()

    # Set reaction specific costs for reactions that have likelihoods.
    if penalties is None:
        penalties = {'universal': 1, 'exchange': 100, 'demand': 1}
    if likelihoods is not None:
        reaction_likelihoods = likelihoods.reaction_values
        for rxn_id in reaction_likelihoods:
            likelihood = reaction_likelihoods[rxn_id]['likelihood']
            penalties[rxn_id] = max(0, 1 - likelihood) * (penalties[rxn_id] if rxn_id in penalties else 1)

    # Run the gap fill method.
    if method == 'default':
        gapfiller = GapFiller(model, universal=universal_model, lower_bound=0.05,
                              penalties=penalties, demand_reactions=demand_reactions,
                              exchange_reactions=exchange_reactions, integer_threshold=1e-12)
        solution = gapfiller.fill()
    # elif method == 'psamm':
        # export to model psamm
        # export template to psamm
        # call psamm method
    else:
        raise ValueError('Gap fill method {0} is not valid'.format(method))
    LOGGER.info('Finished gap fill for model "%s"', model.id)
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
