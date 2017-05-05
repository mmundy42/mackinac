from os.path import join
from warnings import warn

from .universal import create_universal_metabolite, universal_metabolite_fields
from .universal import create_universal_reaction, universal_reaction_fields, resolve_universal_reactions
from .templatecompartment import create_template_compartment, compartment_fields
from .templaterole import create_template_role, role_fields
from .templatecomplex import create_template_complex, complex_fields
from .templatemodel import TemplateModel
from .util import read_source_file, validate_header


# How about parameter with universal folder, parameter with template folder, check for all of the files
# Make TemplateReaction inherit from cobra.core.Reaction
# Just keep universal elements in DictLists and put into TemplateModel
# Read universal reactions into TemplateReaction objects
# Then just this one function to create a template model and way fewer parameters
# Then template model has just the info needed

# def create_template_model_from_source(reactions_filename, compartments_filename, biomass_filename,
#                                       biomass_components_filename, complexes_filename, roles_filename,
#                                       universal_model, id, name, type='Growth', domain='Bacteria',
#                                       verbose=False):
def create_template_model(universal_folder, template_folder, id, name, type='growth',
                          domain='Bacteria', verbose=False, validate=False):

    """ Create a template model from ModelSEED source files.
    
    Parameters
    ----------
    universal_folder : str
        Path to folder with files for universal things
    template_folder : str
        Path to folder with files for template things
    id : str
        ID of template model
    name : str
        Name of template model
    type : str, optional
        Type of template model (usually "growth")
    domain : str, optional
        Domain of organisms represented by template model
    verbose : bool, optional
        When True, more messages
    validate : bool, optional
        When True, validate things
    
    Returns
    -------
    TemplateModel
         Template model created from source files
    """

    # Get the universal metabolites and reactions by processing the source files.
    # Note that metabolites and reactions marked as obsolete are not included.
    universal_metabolites = read_source_file(join(universal_folder, 'Metabolites.tsv'),
                                             universal_metabolite_fields,
                                             create_universal_metabolite)
    universal_reactions = read_source_file(join(universal_folder, 'Reactions.tsv'),
                                           universal_reaction_fields,
                                           create_universal_reaction)
    resolve_universal_reactions(universal_reactions, universal_metabolites, validate)

    # Get the universal complexes and roles by processing the source files.
    universal_complexes = read_source_file(join(universal_folder, 'Complexes.tsv'),
                                           complex_fields, create_template_complex)
    universal_roles = read_source_file(join(universal_folder, 'Roles.tsv'),
                                       role_fields, create_template_role)

    # Create an empty template model.
    template_model = TemplateModel(id, name, type, domain)

    # Get the compartments by processing the source file.
    template_model.add_compartments(join(template_folder, 'Compartments.tsv'))

    # Get the biomasses by processing the source files for biomass entities and
    # for biomass components. All biomass components must include a metabolite that is
    # available in the universal metabolites.
    template_model.add_biomasses(join(template_folder, 'Biomasses.tsv'),
                                 join(template_folder, 'BiomassCompounds.tsv'),
                                 universal_metabolites)

    template_model.add_reactions(join(template_folder, 'Reactions.tsv'),
                                 universal_reactions,
                                 universal_metabolites,
                                 universal_complexes,
                                 universal_roles)
    return template_model
