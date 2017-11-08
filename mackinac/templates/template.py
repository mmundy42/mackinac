from os.path import join
from operator import itemgetter

from .universal import create_universal_metabolite, metabolite_json_schema, create_universal_reaction, \
    reaction_json_schema, resolve_universal_reactions
from .templatemodel import TemplateModel
from .util import read_json_file
from ..workspace import get_workspace_object_data


def create_mackinac_template_model(universal_folder, template_folder, id, name, type='growth',
                                   domain='Bacteria', verbose=False, validate=False):
    """ Create a template model object from ModelSEED source files.
    
    The universal folder must contain these files: (1) "metabolites.tsv", (2) "reactions.tsv".
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
    id : str
        ID of template model
    name : str
        Name of template model
    type : str, optional
        Type of template model (usually "growth")
    domain : str, optional
        Domain of organisms represented by template model
    verbose : bool, optional
        When True, show all warning messages
    validate : bool, optional
        When True, check for common problems 
    
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
    template_model = TemplateModel(id, name, type, domain)
    template_model.init_from_files(
        join(template_folder, 'compartments.tsv'),
        join(template_folder, 'biomasses.tsv'),
        join(template_folder, 'biomass_metabolites.tsv'),
        join(template_folder, 'reactions.tsv'),
        join(template_folder, 'complexes.tsv'),
        join(template_folder, 'roles.tsv'),
        universal_metabolites,
        universal_reactions,
        verbose
    )

    return template_model
