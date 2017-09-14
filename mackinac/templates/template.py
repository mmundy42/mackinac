from os.path import join
from operator import itemgetter

from .universal import create_universal_metabolite, universal_metabolite_fields
from .universal import create_universal_reaction, universal_reaction_fields, resolve_universal_reactions
from .templatemodel import TemplateModel
from .util import read_source_file
from ..workspace import get_workspace_object_data


def create_mackinac_template_model(universal_folder, template_folder, id, name, type='growth',
                                   domain='Bacteria', verbose=False, validate=False):
    """ Create a template model object from ModelSEED source files.
    
    The universal folder must contain these files: (1) "reactions.tsv", (2)
    "metabolites.tsv", (3) "roles.tsv", and (4) "complexes.tsv". The template
    folder must contain these files: (1) "compartments.tsv", (2) "biomasses.tsv",
    (3) "biomass_components.tsv", (4) "reactions.tsv".
    
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
    universal_metabolites = read_source_file(join(universal_folder, 'Metabolites.tsv'),
                                             universal_metabolite_fields,
                                             create_universal_metabolite)
    universal_reactions = read_source_file(join(universal_folder, 'Reactions.tsv'),
                                           universal_reaction_fields,
                                           create_universal_reaction)
    resolve_universal_reactions(universal_reactions, universal_metabolites, validate)

    # Create an empty template model and initialize it from source files.
    template_model = TemplateModel(id, name, type, domain)
    template_model.init_from_files(
        join(template_folder, 'compartments.tsv'),
        join(template_folder, 'biomasses.tsv'),
        join(template_folder, 'biomasscompounds.tsv'),
        join(template_folder, 'reactions.tsv'),
        join(template_folder, 'complexes.tsv'),
        join(template_folder, 'roles.tsv'),
        universal_metabolites,
        universal_reactions,
        verbose
    )

    return template_model


def save_modelseed_template_model(template_reference, universal_folder, template_folder):
    """ Save a ModelSEED template model to source file format.
    
    Parameters
    ----------
    template_reference : str
        Workspace reference to template model
    universal_folder : str
        Path to folder for storing files with universal data
    template_folder : str
        Path to folder for storing files with template data
    """

    # Get the template model data from the workspace object.
    data = get_workspace_object_data(template_reference)

    # Convert roles to source file format and store in file.
    with open(join(universal_folder, 'Roles.tsv'), 'w') as handle:
        handle.write('\t'.join(['id', 'name', 'source', 'features', 'aliases']) + '\n')
        data['roles'].sort(key=itemgetter('id'))
        lines = list()
        for index in range(len(data['roles'])):
            item = data['roles'][index]
            features = 'null'
            if len(item['features']) > 0:
                features = ';'.join(item['features'])
            aliases = 'null'  # @todo Aliases are messed up
            lines.append('\t'.join([item['id'], item['name'], item['source'], features, aliases]))
        handle.write('\n'.join(lines) + '\n')

    # Convert complexes to source file format and store in file.
    with open(join(template_folder, 'Complexes.tsv'), 'w') as handle:
        handle.write('\t'.join(['id', 'name', 'source', 'reference', 'confidence', 'roles']) + '\n')
        data['complexes'].sort(key=itemgetter('id'))
        lines = list()
        for index in range(len(data['complexes'])):
            item = data['complexes'][index]
            complexrole = 'null'
            if len(item['complexroles']) > 0:
                # Note that second field can also be "involved" but that info is lost when
                # building a template model.
                complexrole = '|'.join([';'.join([r['templaterole_ref'].split('/')[-1], 'triggering',
                                                  str(r['optional']), str(r['triggering'])])
                                       for r in item['complexroles']])
            lines.append('\t'.join([item['id'], item['name'], item['source'], item['reference'],
                                    str(item['confidence']), complexrole]))
        handle.write('\n'.join(lines) + '\n')

    # Convert compartments to source file format and store in file.
    with open(join(template_folder, 'Compartments.tsv'), 'w') as handle:
        handle.write('\t'.join(['index', 'id', 'name', 'hierarchy', 'pH', 'aliases']) + '\n')
        data['compartments'].sort(key=itemgetter('id'))
        lines = list()
        for index in range(len(data['compartments'])):
            item = data['compartments'][index]
            aliases = 'null'
            if len(item['aliases']) > 0:
                aliases = ';'.join(item['aliases'])
            lines.append('\t'.join([item['index'], item['id'], item['name'], str(item['hierarchy']),
                                    str(item['pH']), aliases]))
        handle.write('\n'.join(lines) + '\n')

    # Convert reactions to source file format and store in file.
    with open(join(template_folder, 'Reactions.tsv'), 'w') as handle:
        handle.write('\t'.join(['id', 'compartment', 'direction', 'gfdir', 'type', 'base_cost',
                                'forward_cost', 'reverse_cost', 'complexes']) + '\n')
        data['reactions'].sort(key=itemgetter('id'))
        lines = list()
        for index in range(len(data['reactions'])):
            item = data['reactions'][index]
            compartments = 'c|e'  # No way to recover order of compartments so hard-code the value
            complexes = 'null'
            if len(item['templatecomplex_refs']) > 0:
                complexes = '|'.join([ref.split('/')[-1] for ref in item['templatecomplex_refs']])
            lines.append('\t'.join([item['id'].split('_')[0], compartments, item['direction'],
                                    item['GapfillDirection'], item['type'], str(item['base_cost']),
                                    str(item['forward_penalty']), str(item['reverse_penalty']),
                                    complexes]))
        handle.write('\n'.join(lines) + '\n')

    # Convert biomasses to source file format and store in two files.
    with open(join(template_folder, 'Biomasses.tsv'), 'w') as b_handle:
        with open(join(template_folder, 'BiomassCompounds.tsv'), 'w') as c_handle:
            b_handle.write('\t'.join(['id', 'name', 'type', 'other', 'dna', 'rna', 'protein', 'lipid',
                                      'cellwall', 'cofactor', 'energy']) + '\n')
            c_handle.write('\t'.join(['biomass_id', 'id', 'coefficient', 'coefficient_type', 'class',
                                      'linked_compounds', 'compartment']) + '\n')
            data['biomasses'].sort(key=itemgetter('id'))
            b_lines = list()
            c_lines = list()
            for b_index in range(len(data['biomasses'])):
                item = data['biomasses'][b_index]
                b_lines.append('\t'.join([item['id'], item['name'], item['type'], str(item['other']),
                                          str(item['dna']), str(item['rna']), str(item['protein']),
                                          str(item['lipid']), str(item['cellwall']), str(item['cofactor']),
                                          str(item['energy'])]))
                item['templateBiomassComponents'].sort(key=itemgetter('class'))
                for c_index in range(len(item['templateBiomassComponents'])):
                    c_item = item['templateBiomassComponents'][c_index]
                    parts = c_item['templatecompcompound_ref'].split('/')[-1].split('_')
                    parts[0] += '_0'  # Really should look up compartment ID in parts[1] and use index number
                    linked = 'null'
                    if len(c_item['linked_compound_refs']) > 0:
                        lc = list()
                        for l_index in range(len(c_item['linked_compound_refs'])):
                            lc.append(':'.join([c_item['linked_compound_refs'][l_index].split('/')[-1].split('_')[0] + '_0',
                                                str(c_item['link_coefficients'][l_index])]))
                        linked = '|'.join(lc)
                    c_lines.append('\t'.join([item['id'], parts[0], str(c_item['coefficient']),
                                              c_item['coefficient_type'], c_item['class'], linked, parts[1]]))
            b_handle.write('\n'.join(b_lines) + '\n')
            c_handle.write('\n'.join(c_lines) + '\n')

    return
