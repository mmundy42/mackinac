from warnings import warn
from os.path import join
import re
from operator import itemgetter

from cobra import Model, Reaction, Metabolite, Gene, DictList

from .workspace import get_workspace_object_meta, get_workspace_object_data, put_workspace_object
from .likelihood import LikelihoodAnnotation
from .SeedClient import handle_server_error, ObjectNotFoundError, ServerError, ObjectTypeError
from .logger import LOGGER

# Regular expression for compartment suffix on ModelSEED IDs
modelseed_suffix_re = re.compile(r'_([a-z])\d*$')

# Regular expression for prefix on PATRIC gene IDs
patric_gene_prefix_re = re.compile(r'^fig\|')


def convert_compartment_id(modelseed_id, format_type):
    """ Convert a compartment ID in ModelSEED source format to another format.

    No conversion is done for unknown format types.

    Parameters
    ----------
    modelseed_id : str
        Compartment ID in ModelSEED source format
    format_type : {'modelseed', 'bigg'}
        Type of format to convert to

    Returns
    -------
    str
        ID in specified format
    """

    if format_type == 'modelseed' or format_type == 'bigg':
        return modelseed_id[0]

    return modelseed_id


def convert_suffix(modelseed_id, format_type):
    """ Convert a string with a compartment suffix from ModelSEED source format to another format.

    No conversion is done for unknown format types.

    Parameters
    ----------
    modelseed_id : str
        ID with compartment suffix in ModelSEED source format
    format_type : {'modelseed', 'bigg'}
        Type of format to convert to

    Returns
    -------
    str
        ID in specified format
    """

    # Remove compartment index number for ModelSEED format. For example, rxn00001_c0 becomes rxn00001_c.
    # ModelSEED always uses compartment index 0 anyway.
    if format_type == 'modelseed':
        compartment = re.search(modelseed_suffix_re, modelseed_id).group(1)
        return re.sub(modelseed_suffix_re, '', modelseed_id) + '_{0}'.format(compartment)

    # Convert to BiGG type format. For example, rxn00001_c0 becomes rxn00001[c].
    elif format_type == 'bigg':
        match = re.search(modelseed_suffix_re, modelseed_id)
        compartment = match.group(1)
        return re.sub(modelseed_suffix_re, '', modelseed_id) + '[{0}]'.format(compartment)

    # No conversion is needed or format_type is unknown.
    return modelseed_id


def remove_suffix(modelseed_string):
    """ Remove a compartment suffix in ModelSEED source format from a string.

    Parameters
    ----------
    modelseed_string : str
        String with compartment suffix in ModelSEED source format

    Returns
    -------
    str
        String with compartment suffix removed
    """

    return re.sub(modelseed_suffix_re, '', modelseed_string)


def _convert_metabolite(modelseed_compound, id_type):
    """ Convert a ModelSEED compound dictionary to a COBRApy Metabolite object.

    Parameters
    ----------
    modelseed_compound : dict
        Compound dictionary from ModelSEED model
    id_type : {'modelseed', 'bigg'}
        Type of metabolite ID

    Returns
    -------
    cobra.core.Metabolite
        Metabolite object created from ModelSEED compound
    """

    # Convert ID and name from ModelSEED format to COBRApy format.
    cobra_id = convert_suffix(modelseed_compound['id'], id_type)
    cobra_compartment = convert_compartment_id(modelseed_compound['modelcompartment_ref'].split('/')[-1], id_type)
    cobra_name = remove_suffix(modelseed_compound['name'])

    # Create the Metabolite object.
    metabolite = Metabolite(id=cobra_id,
                            formula=modelseed_compound['formula'],
                            name=cobra_name,
                            charge=modelseed_compound['charge'],
                            compartment=cobra_compartment)
    return metabolite


def _convert_reaction(modelseed_reaction, model, id_type, likelihoods):
    """ Convert a ModelSEED reaction dictionary to a COBRApy Reaction object.

    Parameters
    ----------
    modelseed_reaction : dict
        Reaction dictionary from ModelSEED model
    model : cobra.core.Model
        Model object with metabolites
    id_type : {'modelseed', 'bigg'}
        Type of reaction ID
    likelihoods : dict
        Dictionary with reaction likelihoods from ModelSEED model

    Returns
    -------
    cobra.core.Reaction
        Reaction object created from ModelSEED compound
    """

    # Set upper and lower bounds based directionality. Switch reverse reactions to
    # forward reactions (ModelSEED does this when exporting to SBML).
    reverse = 1.0
    if modelseed_reaction['direction'] == '=':
        lower_bound = -1000.0
        upper_bound = 1000.0
    elif modelseed_reaction['direction'] == '>':
        lower_bound = 0.0
        upper_bound = 1000.0
    elif modelseed_reaction['direction'] == '<':
        lower_bound = 0.0
        upper_bound = 1000.0
        reverse = -1.0
    else:
        warn('Reaction direction {0} assumed to be reversible for reaction {1}'
             .format(modelseed_reaction['direction'], modelseed_reaction['id']))
        lower_bound = -1000.0
        upper_bound = 1000.0

    # Create the Reaction object.
    reaction = Reaction(id=convert_suffix(modelseed_reaction['id'], id_type),
                        name=re.sub(modelseed_suffix_re, '', modelseed_reaction['name']),
                        lower_bound=lower_bound,
                        upper_bound=upper_bound)

    # Create dictionary of metabolites and add them to the reaction.
    metabolites = dict()
    for reagent in modelseed_reaction['modelReactionReagents']:
        cobra_metabolite_id = convert_suffix(reagent['modelcompound_ref'].split('/')[-1], id_type)
        metabolite = model.metabolites.get_by_id(cobra_metabolite_id)
        metabolites[metabolite] = float(reagent['coefficient']) * reverse
    reaction.add_metabolites(metabolites)

    # If there are proteins associated with the reaction, build the gene reaction rule and
    # add corresponding Gene objects to the model.
    if len(modelseed_reaction['modelReactionProteins']) > 0:
        # Build a list of proteins associated with the reaction.
        protein_list = list()
        for protein in modelseed_reaction['modelReactionProteins']:
            # Spontaneous and universal reactions can have an entry in the list of proteins
            # that does not have any protein subunits.
            if len(protein['modelReactionProteinSubunits']) == 0:
                continue

            # Build a list of protein subunits in this protein.
            subunit_list = list()
            for subunit in protein['modelReactionProteinSubunits']:
                # A protein with multiple subunits can have a subunit that is not linked
                # to a feature in the genome of the organism.
                if len(subunit['feature_refs']) == 0:
                    continue

                # Build a list of features in this protein subunit.
                feature_list = list()
                for feature in subunit['feature_refs']:
                    # Extract the gene ID from the reference to the feature in the genome and
                    # remove the "fig|" prefix.
                    gene_id = re.sub(patric_gene_prefix_re, '', feature.split('/')[-1])
                    if not model.genes.has_id(gene_id):
                        gene = Gene(gene_id, subunit['role'])  # Use the role name as the Gene name
                        model.genes.append(gene)
                    # TODO: If a different subunit role is found, should name of gene be updated
                    #       to include it (with separator)?
                    # else:
                    #     gene = model.genes.get_by_id(gene_id)
                    #     if gene.name != subunit['role']:
                    #         print('{0}: {1} vs {2}'.format(gene.id, gene.name, subunit['role']))
                    feature_list.append(gene_id)

                # Join multiple features using an OR relationship.
                if len(feature_list) > 1:
                    subunit_list.append('( {0} )'.format(' or '.join(sorted(feature_list))))
                else:
                    subunit_list.append(feature_list[0])

            # Join multiple protein subunits using an AND relationship.
            if len(subunit_list) > 0:
                if len(subunit_list) > 1:
                    protein_list.append('( {0} )'.format(' and '.join(sorted(subunit_list))))
                else:
                    protein_list.append(subunit_list[0])

        # If there is an association to a feature, add the rule to the reaction.
        if len(protein_list) > 0:
            # Join multiple proteins using an OR relationship.
            if len(protein_list) > 1:
                gpr_rule = '( {0} )'.format(' or '.join(protein_list))
            else:
                gpr_rule = protein_list[0]

            reaction.gene_reaction_rule = gpr_rule

    # Add a note with gap fill details. ModelSEED gap fill data is a dictionary
    # where the key is the gap fill solution ID and the value indicates if the
    # reaction was added or reversed and the direction of the reaction. For
    # example: {u'gf.0': u'added:>'}
    if len(modelseed_reaction['gapfill_data']) > 0:
        reaction.notes['gapfill_data'] = modelseed_reaction['gapfill_data']

    # Add a note with likelihood value if available.
    if modelseed_reaction['id'] in likelihoods:
        reaction.notes['likelihood'] = likelihoods[modelseed_reaction['id']]
        reaction.notes['likelihood_str'] = '{0:.6f}'.format(reaction.notes['likelihood'])
    else:
        reaction.notes['likelihood_str'] = 'unknown'

    return reaction


def create_cobra_model(reference, id_type='modelseed', validate=False):
    """ Create a COBRA model from a ModelSEED model.

    Parameters
    ----------
    reference : str
        Workspace reference to model
    id_type : {'modelseed', 'bigg'}
        Type of IDs ('modelseed' for _c or 'bigg' for '[c])
    validate : bool
        When True, check for common problems

    Returns
    -------
    cobra.core.Model
        Model object
    """

    # Validate the id_type parameter.
    if id_type == 'modelseed':
        cytosol_suffix = '_c'
    elif id_type == 'bigg':
        cytosol_suffix = '[c]'
    else:
        raise ValueError('id_type {0} is not supported'.format(id_type))

    # Get the model data.
    data = get_workspace_object_data(join(reference, 'model'))

    # Get the workspace object with the likelihoods and put the likelihood values in a dictionary
    # keyed by reaction ID. Calculating likelihoods is optional so the object may not exist.
    try:
        likelihood_data = get_workspace_object_data(join(reference, 'rxnprobs'))
        likelihoods = {r[0]: r[1] for r in likelihood_data['reaction_probabilities']}
    except ObjectNotFoundError:
        likelihoods = dict()

    # Create a new COBRApy Model object.
    model = Model(data['id'], name=data['name'])
    if model.id[0] == '.':
        model.id = model.id[1:]

    # Add compartments to the COBRApy model.
    LOGGER.info('Started adding %d compartments from source model', len(data['modelcompartments']))
    compartments = dict()
    for index in range(len(data['modelcompartments'])):
        source_compartment = data['modelcompartments'][index]
        cobra_id = convert_compartment_id(source_compartment['id'], id_type)
        compartments[cobra_id] = source_compartment['label'][:-2]  # Strip _0 suffix from label
    model.compartments = compartments
    LOGGER.info('Finished adding %d compartments to model', len(model.compartments))

    # Add all of the metabolites (or compounds) to the COBRApy model.
    LOGGER.info('Started adding %d metabolites from source model', len(data['modelcompounds']))
    num_duplicates = 0
    metabolite_list = DictList()
    for index in range(len(data['modelcompounds'])):
        metabolite = _convert_metabolite(data['modelcompounds'][index], id_type=id_type)
        try:
            metabolite_list.append(metabolite)
        except ValueError:
            # A ModelSEED model can contain duplicate compounds. Confirm that
            # the duplicate compound is an exact duplicate and ignore it.
            duplicate = metabolite_list.get_by_id(metabolite.id)
            if metabolite.name != duplicate.name:
                LOGGER.warning('Duplicate ModelSEED compound ID {0} has different name, {1} != {2}'
                               .format(metabolite.id, metabolite.name, duplicate.name))
            if metabolite.formula != duplicate.formula:
                LOGGER.warning('Duplicate ModelSEED compound ID {0} has different formula, {1} != {2}'
                               .format(metabolite.id, metabolite.formula, duplicate.formula))
            if metabolite.charge != duplicate.charge:
                LOGGER.warning('Duplicate ModelSEED compound ID {0} has different charge {1} != {2}'
                               .format(metabolite.id, metabolite.charge, duplicate.charge))
            if metabolite.compartment != duplicate.compartment:
                LOGGER.warning('Duplicate ModelSEED compound ID {0} has different compartment {1} != {2}'
                               .format(metabolite.id, metabolite.compartment, duplicate.compartment))
            num_duplicates += 1
    model.add_metabolites(metabolite_list)
    LOGGER.info('Finished adding %d metabolites to model, found %d duplicate metabolites',
                len(model.metabolites), num_duplicates)

    # Report the number of duplicate metabolites.
    if validate and num_duplicates > 0:
        warn('{0} duplicate metabolites were removed from model {1} of {2}'
             .format(num_duplicates, model.id, model.name))

    # Add all of the reactions to the COBRApy model.
    LOGGER.info('Started adding %d reactions from source model', len(data['modelreactions']))
    reaction_list = DictList()
    for index in range(len(data['modelreactions'])):
        reaction_list.append(_convert_reaction(data['modelreactions'][index], model, id_type, likelihoods))
    model.add_reactions(reaction_list)
    LOGGER.info('Finished adding %d reactions to model', len(model.reactions))

    # Add exchange reactions for metabolites in extracellular compartment.
    exchange_list = DictList()
    extracellular_metabolites = model.metabolites.query(lambda x: x == 'e', 'compartment')
    LOGGER.info('Started adding %d exchange reactions for extracellular metabolites',
                len(extracellular_metabolites))
    for metabolite in extracellular_metabolites:
        # Single reactant metabolite makes a system boundary reaction.
        reaction = Reaction(id='EX_' + metabolite.id,
                            name=metabolite.name + ' exchange',
                            lower_bound=-1000.0,
                            upper_bound=1000.0)
        reaction.add_metabolites({metabolite: -1.0})
        reaction.notes['likelihood_str'] = 'unknown'
        exchange_list.append(reaction)
    model.add_reactions(exchange_list)
    LOGGER.info('Finished adding %d exchange reactions to model', len(exchange_list))

    # A ModelSEED model must have a sink reaction for the special biomass metabolite.
    metabolite = model.metabolites.get_by_id('cpd11416'+cytosol_suffix)
    reaction = Reaction(id='SK_' + metabolite.id,
                        name=metabolite.name + ' sink',
                        lower_bound=-1000.0,
                        upper_bound=1000.0)
    reaction.add_metabolites({metabolite: -1.0})
    model.add_reactions([reaction])

    # Note that when ModelSEED exports to SBML, it includes exchange reactions for
    # cpd15302_c0 "Glycogen(n-1)" and cpd08636_c0 "4-5-dihydroxy-2-3-pentanedione".
    # No idea why exchange reactions for metabolites in the cytosol compartment are
    # added to the SBML file.
    # metabolite = model.metabolites.get_by_id('cpd08636'+cytosol_suffix)
    # reaction = Reaction(id='EX_' + metabolite.id,
    #                     name=metabolite.name,
    #                     lower_bound=-1000.0,
    #                     upper_bound=1000.0)
    # reaction.add_metabolites({metabolite: -1.0})
    # model.add_reactions([reaction])
    #
    # metabolite = model.metabolites.get_by_id('cpd15302'+cytosol_suffix)
    # reaction = Reaction(id='EX_' + metabolite.id,
    #                     name=metabolite.name,
    #                     lower_bound=-1000.0,
    #                     upper_bound=1000.0)
    # reaction.add_metabolites({metabolite: -1.0})
    # model.add_reactions([reaction])

    # Add the biomass reactions to the COBRApy model. ModelSEED models can have more
    # than one biomass reaction but the model does not identify which one to use as
    # the objective so always use the first one.
    if len(data['biomasses']) > 1:
        warn('Found {0} biomass reactions and selected {1} as the objective'
             .format(len(data['biomasses']), data['biomasses'][0]['id']))
    for index in range(len(data['biomasses'])):
        biomass = data['biomasses'][index]
        biomass_metabolites = dict()
        for biomass_compound in biomass['biomasscompounds']:
            cobra_id = convert_suffix(biomass_compound['modelcompound_ref'].split('/')[-1], id_type)
            metabolite = model.metabolites.get_by_id(cobra_id)
            biomass_metabolites[metabolite] = biomass_compound['coefficient']
        reaction = Reaction(id=biomass['id'],
                            name=biomass['name'],
                            lower_bound=0.0,
                            upper_bound=1000.0)
        reaction.add_metabolites(biomass_metabolites)
        model.add_reactions([reaction])
        if index == 0:
            reaction.objective_coefficient = 1.

    # If requested, validate the COBRApy model.
    if validate:
        validate_model(model)

    LOGGER.info('Created %s model with %d reactions, %d metabolites, %d compartments',
                model.id, len(model.reactions), len(model.metabolites), len(model.compartments))
    return model


def validate_model(model):
    """ Validate a model by checking for common issues.

    Parameters
    ----------
    model : cobra.core.Model
        Model to validate
    """

    # See if all of the non-boundary reactions are mass balanced.
    num_unbalanced = 0
    reaction_list = model.reactions.query(lambda x: not x, 'boundary')
    for reaction in reaction_list:
        unbalanced = reaction.check_mass_balance()
        if len(unbalanced) > 0:
            warn('Reaction {0} is unbalanced because {1}\n    {2}'
                 .format(reaction.id, unbalanced, reaction.build_reaction_string(use_metabolite_names=True)))
            num_unbalanced += 1
    if num_unbalanced > 0:
        warn('Model {0} has {1} unbalanced reactions'.format(model.id, num_unbalanced))

    # See if there is a way for exchange reaction metabolites to make it into the cell.
    # Note these assumptions: (1) exchange reaction IDs start with 'EX_' (2) cytosol
    # compartment ID is 'c' (3) extracellular compartment ID is 'e' (4) exchange
    # reactions are defined with a single reactant.
    exchange_reactions = model.reactions.query(lambda x: x.startswith('EX_'), 'id')
    for reaction in exchange_reactions:
        num_transport = 0
        rxn_list = reaction.reactants[0].reactions
        for rxn in rxn_list:
            if 'c' in rxn.compartments and 'e' in rxn.compartments:
                num_transport += 1
        if num_transport == 0:
            warn('There are no transport reactions for boundary metabolite {0}'
                 .format(reaction.reactants[0].id))
        if num_transport > 1:
            LOGGER.info('There are %d transport reactions for boundary metabolite %s',
                        num_transport, reaction.reactants[0].id)

    return


def calculate_likelihoods(reference, search_program_path, search_db_path, fid_role_path, work_folder):
    """ Calculate reaction likelihoods for a ModelSEED model.

    Reaction likelihood calculation is done locally and results are stored in the
    model's folder in workspace. Caller must run download_data_files() function
    before running this function to prepare for local calculation of likelihoods.

    Parameters
    ----------
    reference : str
        Workspace reference to model
    search_program_path : str
        Path to search program executable
    search_db_path : str
        Path to search database file
    fid_role_path : str
        Path to feature ID to role ID mapping file
    work_folder : str
        Path to folder for storing intermediate files

    Returns
    -------
    dict
        Dictionary keyed by reaction ID of calculated likelihoods and statistics

    """

    # Get the model statistics to confirm the model exists and get workspace reference.
    stats = get_model_statistics(reference)

    # Get the genome object stored with the model.
    genome = get_workspace_object_data(join(stats['ref'], 'genome'))

    # Get the model template object used to build the model.
    template = get_workspace_object_data(stats['template_ref'])

    # Create a dictionary to map a complex ID to a list of role IDs as defined in the template.
    complexes_to_roles = dict()
    for index in range(len(template['complexes'])):
        complx = template['complexes'][index]
        complex_id = complx['id']
        if len(complx['complexroles']) > 0:
            complexes_to_roles[complex_id] = list()
            for crindex in range(len(complx['complexroles'])):
                # A complex has a list of complexroles and each complexrole has a reference
                # to a role. Role ID is last element in reference.
                role_id = complx['complexroles'][crindex]['templaterole_ref'].split('/')[-1]
                complexes_to_roles[complex_id].append(role_id)

    # Create a dictionary to map a reaction ID to a list of complex IDs as defined in the template.
    reactions_to_complexes = dict()
    for index in range(len(template['reactions'])):
        reaction_id = template['reactions'][index]['id']
        if len(template['reactions'][index]['templatecomplex_refs']) > 0:
            reactions_to_complexes[reaction_id] = list()
            for complex_ref in template['reactions'][index]['templatecomplex_refs']:
                # Complex ID is last element in reference.
                reactions_to_complexes[reaction_id].append(complex_ref.split('/')[-1])

    # Generate likelihood-based gene annotation for the organism.
    LOGGER.info('Started likelihood-based annotation')
    likelihood = LikelihoodAnnotation(search_program_path, search_db_path, fid_role_path, work_folder)
    likelihood.calculate(stats['id'], genome['features'], complexes_to_roles, reactions_to_complexes)
    LOGGER.info('Finished likelihood-based annotation')

    # Store reaction likelihoods with the model.
    reaction_likelihoods = likelihood.reaction_values
    reaction_list = list()
    for reaction_id in sorted(reaction_likelihoods):
        value = reaction_likelihoods[reaction_id]
        reaction_list.append((reaction_id, value['likelihood'], value['type'], value['complex_string'], value['gpr']))
    put_workspace_object(join(stats['ref'], 'rxnprobs'), 'rxnprobs',
                         {'reaction_probabilities': reaction_list}, overwrite=True)
    return reaction_likelihoods


def get_model_statistics(reference):
    """ Get statistics for a model object in the workspace.

    Parameters
    ----------
    reference : str
        Workspace reference to model

    Returns
    -------
    dict
        Dictionary of current model statistics
    """

    # Build the model statistics dictionary using the object metadata.
    LOGGER.info('Started get model stats using web service for "%s"', reference)
    metadata = get_workspace_object_meta(reference)
    LOGGER.info('Finished get model stats using web service for "%s"', reference)

    return metadata_to_statistics(metadata)


def metadata_to_statistics(metadata):
    """ Convert metadata for a model object to statistics dictionary.

    Parameters
    ----------
    metadata : tuple
        Workspace object metadata

    Returns
    -------
    dict
        Dictionary of current model statistics
    """

    if len(metadata) == 0:
        raise ObjectTypeError('Model metadata not available', None)
    stats = dict()
    stats['fba_count'] = int(metadata[7]['fba_count'])
    stats['gapfilled_reactions'] = int(metadata[7]['gapfilled_reactions'])
    stats['gene_associated_reactions'] = int(metadata[7]['gene_associated_reactions'])
    stats['genome_ref'] = metadata[7]['genome_ref']
    stats['id'] = metadata[0][1:] if metadata[0][0] == '.' else metadata[0]
    stats['integrated_gapfills'] = int(metadata[7]['integrated_gapfills'])
    stats['name'] = metadata[7]['name']
    stats['num_biomass_compounds'] = int(metadata[7]['num_biomass_compounds'])
    stats['num_biomasses'] = int(metadata[7]['num_biomasses'])
    stats['num_compartments'] = int(metadata[7]['num_compartments'])
    stats['num_compounds'] = int(metadata[7]['num_compounds'])
    stats['num_genes'] = int(metadata[7]['num_genes'])
    stats['num_reactions'] = int(metadata[7]['num_reactions'])
    stats['ref'] = metadata[7]['ref']
    stats['rundate'] = metadata[3]
    stats['source'] = metadata[7]['source']
    stats['source_id'] = metadata[7]['source_id']
    stats['template_ref'] = metadata[7]['template_ref']
    stats['type'] = metadata[7]['type']
    stats['unintegrated_gapfills'] = int(metadata[7]['unintegrated_gapfills'])
    return stats


def convert_fba_solutions(solutions):
    """ Convert a list of fba solutions to a more usable format.

    Parameters
    ----------
    solutions : list of dict
        List of fba solution summary dictionaries as returned by ModelSEED list_fba_studies method

    Returns
    -------
    list
        List of fba solution data structures
    """

    # For each solution in the list, get the referenced fba object, and add the
    # details on the flux values to the solution. Note ModelSEED stores the
    # results of each flux balance analysis separately.
    for sol in solutions:
        try:
            solution_data = get_workspace_object_data(sol['ref'])
        except ServerError as e:
            raise handle_server_error(e, sol['ref'])

        # A ModelSEED model does not have exchange reactions so instead the results of a flux
        # balance analysis reports flux values on metabolites in the extracellular compartment.
        # For ModelSEED, a positive flux means the metabolite is consumed and a negative flux
        # means the metabolite is produced.
        # @todo Should the fluxes be flipped to match COBRA models?
        sol['exchanges'] = dict()
        for flux in solution_data['FBACompoundVariables']:
            exchange_id = flux['modelcompound_ref'].split('/')[-1]
            sol['exchanges'][exchange_id] = {
                'x': flux['value'],
                'lower_bound': flux['lowerBound'],
                'upper_bound': flux['upperBound']}

        # Flux values for all of the reactions are reported separately.
        sol['reactions'] = dict()
        for flux in solution_data['FBAReactionVariables']:
            reaction_id = flux['modelreaction_ref'].split('/')[-1]
            sol['reactions'][reaction_id] = {
                'x': flux['value'],
                'lower_bound': flux['lowerBound'],
                'upper_bound': flux['upperBound']}

    solutions.sort(key=itemgetter('rundate'), reverse=True)  # Sort so last completed fba is first in list
    return solutions


def convert_gapfill_solutions(solutions, id_type='modelseed'):
    """ Convert a list of gap fill solutions to a more usable format.

    Parameters
    ----------
    solutions : list of dict
        List of gap fill solution dictionaries as returned by ModelSEED list_gapfill_solutions method
    id_type : {'modelseed', 'bigg'}
        Type of IDs ('modelseed' for _c or 'bigg' for '[c])

    Returns
    -------
    list
        List of converted gap fill solution dictionaries
    """

    # Convert the data about the gap filled reactions from a list to a dictionary
    # keyed by reaction ID.
    for sol in solutions:
        if len(sol['solution_reactions']) > 1:
            warn('Gap fill solution {0} has {1} items in solution_reactions list'
                 .format(sol['id'], len(sol['solution_reactions'])))
        sol['reactions'] = dict()
        if len(sol['solution_reactions']) > 0:  # A gap fill solution can have no reactions
            for reaction in sol['solution_reactions'][0]:
                reaction['compartment'] = convert_compartment_id(reaction['compartment'], id_type)
                reaction_id = '{0}_{1}'.format(re.sub(modelseed_suffix_re, '', reaction['reaction'].split('/')[-1]),
                                               reaction['compartment'])
                sol['reactions'][reaction_id] = reaction
        del sol['solution_reactions']

    # Sort so last completed gap fill is first in list.
    solutions.sort(key=itemgetter('rundate'), reverse=True)
    return solutions
