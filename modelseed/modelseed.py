from __future__ import absolute_import
from time import sleep
from operator import itemgetter
from warnings import warn
from os.path import join
import re

from cobra import Model, Reaction, Metabolite, Gene

from .SeedClient import SeedClient, ServerError, ObjectNotFoundError, JobError, handle_server_error
from .workspace import get_workspace_object_meta, get_workspace_object_data, put_workspace_object

# ModelSEED service endpoint
modelseed_url = 'https://p3.theseed.org/services/ProbModelSEED'

# Client for running functions on ModelSEED web service
ms_client = SeedClient(modelseed_url, 'ProbModelSEED')

# Regular expression for compartment suffix on ModelSEED IDs
modelseed_suffix_re = re.compile(r'_([a-z])\d*$')

# Regular expression for prefix on PATRIC gene IDs
patric_gene_prefix_re = re.compile(r'^fig\|')

# Name of folder where ModelSEED models are stored
model_folder = 'modelseed'


def _make_modelseed_reference(name):
    """ Make a workspace reference to an object.

    Parameters
    ----------
    name : str
        Name of object

    Returns
    -------
    str
        Reference to object in user's model folder
    """

    if ms_client.username is None:
        ms_client.set_authentication_token()
    return '/{0}/{1}/{2}'.format(ms_client.username, model_folder, name)


def delete_modelseed_model(model_id):
    """ Delete a ModelSEED model from the workspace.

    Parameters
    ----------
    model_id : str
        ID of model
    """

    reference = _make_modelseed_reference(model_id)
    try:
        ms_client.call('delete_model', {'model': reference})
    except ServerError as e:
        handle_server_error(e, [reference])

    return


def gapfill_modelseed_model(model_id, media_reference=None, likelihood=False, comprehensive=False, solver=None):
    """ Run gap fill on a ModelSEED model.

    Parameters
    ----------
    model_id : str
        ID of model
    media_reference : str, optional
        Workspace reference to media to gap fill on (default is complete media)
    likelihood : bool, optional
        True to use likelihood-based gap fill
    comprehensive : bool, optional
        True to run a comprehensive gap fill
    solver : str, optional
        Name of LP solver (None to use default solver as configured in web service)

    Returns
    -------
    dict
        Dictionary of current model statistics
    """

    reference = _make_modelseed_reference(model_id)
    params = dict()
    params['model'] = reference
    params['integrate_solution'] = 1
    if media_reference is not None:
        params['media'] = media_reference
    if likelihood:
        params['probanno'] = 1
    else:
        params['probanno'] = 0
    if comprehensive:
        params['comprehensive_gapfill'] = 1
    if solver is not None:
        params['solver'] = solver

    try:
        job_id = ms_client.call('GapfillModel', params)
        _wait_for_job(job_id)
    except ServerError as e:
        references = [reference]
        if media_reference is not None:
            references.append(media_reference)
        handle_server_error(e, references)

    return get_modelseed_model_stats(model_id)


def get_modelseed_fba_solutions(model_id):
    """ Get the list of fba solutions available for a ModelSEED model.

    Parameters
    ----------
    model_id : str
        ID of model

    Returns
    -------
    list
        List of fba solution data structures
    """

    reference = _make_modelseed_reference(model_id)
    try:
        get_modelseed_model_stats(model_id)  # Confirm model exists
        solutions = ms_client.call('list_fba_studies', {'model': reference})
    except ServerError as e:
        handle_server_error(e, [reference])
        return

    # For each solution in the list, get the referenced fba object, and add the
    # details on the flux values to the solution. Note ModelSEED stores the
    # results of each flux balance analysis separately.
    for sol in solutions:
        try:
            solution_data = get_workspace_object_data(sol['ref'])
        except ServerError as e:
            handle_server_error(e, sol['ref'])

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

        # @todo remove original data?

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


def get_modelseed_gapfill_solutions(model_id):
    """ Get the list of gap fill solutions for a ModelSEED model.

    Parameters
    ----------
    model_id : str
        ID of model

    Returns
    -------
    list
        List of gap fill solution data structures
    """

    reference = _make_modelseed_reference(model_id)
    try:
        get_modelseed_model_stats(model_id)  # Confirm model exists
        solutions = ms_client.call('list_gapfill_solutions', {'model': reference})
    except ServerError as e:
        handle_server_error(e, [reference])

    # Convert the data about the gap filled reactions from a list to a dictionary
    # keyed by reaction ID.
    for sol in solutions:
        if len(sol['solution_reactions']) > 1:
            warn('Gap fill solution {0} has {1} items in solution_reactions list'
                 .format(sol['id'], len(sol['solution_reactions'])))
        sol['reactions'] = dict()
        if len(sol['solution_reactions']) > 0:  # A gap fill solution can have no reactions
            for reaction in sol['solution_reactions'][0]:
                reaction_id = '{0}_{1}'.format(re.sub(modelseed_suffix_re, '', reaction['reaction'].split('/')[-1]),
                                               reaction['compartment'])
                sol['reactions'][reaction_id] = reaction
        del sol['solution_reactions']

    # Sort so last completed gap fill is first in list.
    solutions.sort(key=itemgetter('rundate'), reverse=True)
    return solutions


def get_modelseed_model_data(model_id):
    """ Get the model data for a ModelSEED model.

    Parameters
    ----------
    model_id : str
        Name of model

    Returns
    -------
    dict
        Dictionary of all model data
    """

    reference = _make_modelseed_reference(model_id)
    try:
        return ms_client.call('get_model', {'model': reference, 'to': 1})
    except ServerError as e:
        handle_server_error(e, [reference])


def get_modelseed_model_stats(model_id):
    """ Get the model statistics for a ModelSEED model.

    Parameters
    ----------
    model_id : str
        ID of model

    Returns
    -------
    dict
        Dictionary of current model statistics
    """

    # The metadata for the model object has the data needed for the dictionary.
    metadata = get_workspace_object_meta(_make_modelseed_reference(model_id))

    # Build the model statistics dictionary.
    stats = dict()
    stats['fba_count'] = int(metadata[7]['fba_count'])
    stats['gapfilled_reactions'] = int(metadata[7]['gapfilled_reactions'])
    stats['gene_associated_reactions'] = int(metadata[7]['gene_associated_reactions'])
    stats['genome_ref'] = metadata[7]['genome_ref']
    stats['id'] = metadata[0]
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


def list_modelseed_models(base_folder=None, print_output=False):
    """ List the ModelSEED models for the user.

    Parameters
    ----------
    base_folder : str
        Workspace reference to folder to search for models
    print_output : bool, optional
        When True, print a summary of the list instead of returning the list

    Returns
    -------
    list or None
        List of model statistics dictionaries or None if printed output
    """

    params = dict()
    if base_folder is not None:
        params['path'] = base_folder

    try:
        output = ms_client.call('list_models', params)
    except ServerError as e:
        handle_server_error(e)
    if not print_output:
        return output
    for model in output:
        print('Model {0} for organism {1} with {2} reactions and {3} metabolites'
              .format(model['ref'], model['name'], model['num_reactions'], model['num_compounds']))
    return None


def _convert_compartment(modelseed_id, format_type):
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


def _convert_suffix(modelseed_id, format_type):
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


def _add_metabolite(modelseed_compound, model, id_type):
    """ Create a COBRApy Metabolite object from a ModelSEED compound dictionary and add it to COBRApy model.

    Parameters
    ----------
    modelseed_compound : dict
        Compound dictionary from ModelSEED model
    model : cobra.Model
        Model object to add metabolite to
    id_type : {'modelseed', 'bigg'}
        Type of metabolite ID

    Returns
    -------
    bool
        True when metabolite is a duplicate
    """

    # Convert from ModelSEED format to COBRApy format.
    cobra_id = _convert_suffix(modelseed_compound['id'], id_type)
    cobra_compartment = _convert_compartment(modelseed_compound['modelcompartment_ref'].split('/')[-1], id_type)
    cobra_name = _convert_suffix(modelseed_compound['name'], id_type)

    # A ModelSEED model usually contains duplicate compounds. Confirm that the duplicate
    # compound is an exact duplicate and ignore it.
    if model.metabolites.has_id(cobra_id):
        metabolite = model.metabolites.get_by_id(cobra_id)
        if metabolite.name != cobra_name:
            warn('Duplicate ModelSEED compound ID {0} has different name, {1} != {2}'
                 .format(cobra_id, metabolite.name, cobra_name))
        if metabolite.formula != modelseed_compound['formula']:
            warn('Duplicate ModelSEED compound ID {0} has different formula, {1} != {2}'
                 .format(cobra_id, metabolite.formula, modelseed_compound['formula']))
        if metabolite.charge != modelseed_compound['charge']:
            warn('Duplicate ModelSEED compound ID {0} has different charge {1} != {2}'
                 .format(cobra_id, metabolite.charge, modelseed_compound['charge']))
        if metabolite.compartment != cobra_compartment:
            warn('Duplicate ModelSEED compound ID {0} has different compartment {1} != {2}'
                 .format(cobra_id, metabolite.compartment, cobra_compartment))
        return True

    # Create the Metabolite object and add it to the model.
    metabolite = Metabolite(id=cobra_id,
                            formula=modelseed_compound['formula'],
                            name=cobra_name,
                            charge=modelseed_compound['charge'],
                            compartment=cobra_compartment)
    model.add_metabolites([metabolite])

    return False


def _add_reaction(modelseed_reaction, model, id_type, likelihoods):
    """ Create a COBRApy Reaction object from a ModelSEED reaction dictionary and add it to COBRApy model.

    Parameters
    ----------
    modelseed_reaction : dict
        Reaction dictionary from ModelSEED model
    model : cobra.Model
        Model object to add reaction to
    id_type : str
        Type of reaction ID
    likelihoods : dict
        Dictionary with reaction likelihoods from ModelSEED model
    """

    # Set upper and lower bounds based directionality. Switch reverse reactions to forward reactions (ModelSEED
    # does this when exporting to SBML).
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
    reaction = Reaction(id=_convert_suffix(modelseed_reaction['id'], id_type),
                        name=re.sub(modelseed_suffix_re, '', modelseed_reaction['name']),
                        lower_bound=lower_bound,
                        upper_bound=upper_bound)

    # Create dictionary of metabolites and add them to the reaction.
    metabolites = dict()
    for reagent in modelseed_reaction['modelReactionReagents']:
        cobra_metabolite_id = _convert_suffix(reagent['modelcompound_ref'].split('/')[-1], id_type)
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
                    feature_list.append(gene_id)

                #  Join multiple features using an OR relationship.
                if len(feature_list) > 1:
                    subunit_list.append('( {0} )'.format(' or '.join(feature_list)))
                else:
                    subunit_list.append(feature_list[0])

            # Join multiple protein subunits using an AND relationship.
            if len(subunit_list) > 0:
                if len(subunit_list) > 1:
                    protein_list.append('( {0} )'.format(' and '.join(subunit_list)))
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

    # Add a note with gap fill details. ModelSEED gap fill data is a dictionary where the key is the
    # gap fill solution ID and the value indicates if the reaction was added or reversed and the
    # direction of the reaction. For example: {u'gf.0': u'added:>'}
    if len(modelseed_reaction['gapfill_data']) > 0:
        reaction.notes['gapfill_data'] = modelseed_reaction['gapfill_data']

    # Add a note with likelihood value if available.
    if modelseed_reaction['id'] in likelihoods:
        reaction.notes['likelihood'] = likelihoods[modelseed_reaction['id']]
        reaction.notes['likelihood_str'] = '{0:.6f}'.format(reaction.notes['likelihood'])
    else:
        reaction.notes['likelihood_str'] = 'unknown'

    # Finally, add the reaction to the model.
    model.add_reaction(reaction)

    return


def create_cobra_model_from_modelseed_model(model_id, id_type='modelseed', validate=False):
    """ Create a COBRA model from a ModelSEED model.

    Parameters
    ----------
    model_id : str
        ID of model
    id_type : {'modelseed', 'bigg'}
        Type of IDs ('modelseed' for _c or 'bigg' for '[c])
    validate : bool
        When True, check for common problems

    Returns
    -------
    cobra.Model
        Model object
    """

    # Validate the id_type parameter.
    if id_type == 'modelseed':
        cytosol_suffix = '_c'
    elif id_type == 'bigg':
        cytosol_suffix = '[c]'
    else:
        raise ValueError('id_type {0} is not supported'.format(id_type))

    # Get the ModelSEED model data.
    data = get_modelseed_model_data(model_id)
    reference = _make_modelseed_reference(model_id)

    # Get the workspace object with the likelihoods and put the likelihood values in a dictionary
    # keyed by reaction ID. Calculating likelihoods is optional so the object may not exist.
    try:
        likelihood_data = get_workspace_object_data(join(reference, 'rxnprobs'))
        likelihoods = {r[0]: r[1] for r in likelihood_data['reaction_probabilities']}
    except ObjectNotFoundError:
        likelihoods = dict()

    # Create a new COBRApy Model object.
    model = Model(data['id'], name=data['name'])

    # Add compartments to the COBRApy model.
    for index in range(len(data['modelcompartments'])):
        modelseed_compartment = data['modelcompartments'][index]
        cobra_id = _convert_compartment(modelseed_compartment['id'], id_type)
        model.compartments[cobra_id] = modelseed_compartment['label'][:-2]  # Strip _0 suffix from label

    # Create Metabolite objects for all of the compounds in the ModelSEED model.
    num_duplicates = 0
    for index in range(len(data['modelcompounds'])):
        duplicate = _add_metabolite(data['modelcompounds'][index], model, id_type=id_type)
        if duplicate:
            num_duplicates += 1

    # Report the number of duplicate metabolites.
    if num_duplicates > 0:
        warn('{0} duplicate metabolites were removed from model {1} of {2}'
             .format(num_duplicates, model.id, model.name))

    # Add all of the reactions to the COBRApy model.
    for index in range(len(data['modelreactions'])):
        _add_reaction(data['modelreactions'][index], model, id_type, likelihoods)

    # Add exchange reactions for metabolites in extracellular compartment.
    for index in range(len(model.metabolites)):
        metabolite = model.metabolites[index]
        if metabolite.compartment.startswith('e'):
            # Single reactant metabolite makes a system boundary reaction.
            reaction = Reaction(id='EX_' + metabolite.id,
                                name=metabolite.name + ' exchange',
                                lower_bound=-1000.0,
                                upper_bound=1000.0)
            reaction.add_metabolites({metabolite: -1.0})
            reaction.notes['likelihood_str'] = 'n/a'
            model.add_reaction(reaction)

    # A ModelSEED model must have an exchange reaction for the special biomass metabolite.
    metabolite = model.metabolites.get_by_id('cpd11416'+cytosol_suffix)
    reaction = Reaction(id='EX_' + metabolite.id,
                        name=metabolite.name,
                        lower_bound=-1000.0,
                        upper_bound=1000.0)
    reaction.add_metabolites({metabolite: -1.0})
    model.add_reaction(reaction)

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
    # model.add_reaction(reaction)
    #
    # metabolite = model.metabolites.get_by_id('cpd15302'+cytosol_suffix)
    # reaction = Reaction(id='EX_' + metabolite.id,
    #                     name=metabolite.name,
    #                     lower_bound=-1000.0,
    #                     upper_bound=1000.0)
    # reaction.add_metabolites({metabolite: -1.0})
    # model.add_reaction(reaction)

    # Add the biomass reactions to the COBRApy model. ModelSEED models can have more than one biomass reaction
    # but the model does not identify which one to use as the objective so always use the first one.
    if len(data['biomasses']) > 1:
        warn('Found {0} biomass reactions and selected {1} as the objective'
             .format(len(data['biomasses']), data['biomasses'][0]['id']))
    for index in range(len(data['biomasses'])):
        biomass = data['biomasses'][index]
        biomass_metabolites = dict()
        for biomass_compound in biomass['biomasscompounds']:
            cobra_id = _convert_suffix(biomass_compound['modelcompound_ref'].split('/')[-1], id_type)
            metabolite = model.metabolites.get_by_id(cobra_id)
            biomass_metabolites[metabolite] = biomass_compound['coefficient']
        reaction = Reaction(id=biomass['id'],
                            name=biomass['name'],
                            lower_bound=0.0,
                            upper_bound=1000.0)
        reaction.add_metabolites(biomass_metabolites)
        if index == 0:
            reaction.objective_coefficient = 1.
        model.add_reaction(reaction)

    # If requested, validate the COBRApy model.
    if validate:
        # See if all of the reactions are mass balanced.
        num_unbalanced = 0
        for r in model.reactions:
            if not r.id.startswith('EX_'):  # Skip exchange reactions
                unbalanced = r.check_mass_balance()
                if len(unbalanced) > 0:
                    warn('Reaction {0} is unbalanced because {1}\n    {2}'
                         .format(r.id, unbalanced, r.build_reaction_string(use_metabolite_names=True)))
                    num_unbalanced += 1
        if num_unbalanced > 0:
            warn('Model {0} has {1} unbalanced reactions'.format(model.id, num_unbalanced))

    return model


def create_universal_model(template_reference, id_type='modelseed'):
    """ Create a universal model from a ModelSEED template model.

        A template model has all of the reactions and metabolites that are available for
        inclusion in a model. There are different template models for different types
        of organisms (e.g. gram negative bacteria). Use an universal model as input to
        one of the gap fill functions.

    Parameters
    ----------
    template_reference : str
        Workspace reference to template model
    id_type : {'modelseed', 'bigg'}, optional
        Type of IDs ('modelseed' for _c or 'bigg' for '[c])

    Returns
    -------
    cobra.Model
        Model object with all reactions for models of a type of organism
    """

    # Get the template model data from the workspace object.
    data = get_workspace_object_data(template_reference)

    # Create a dict to look up compounds.
    compound_index = dict()
    for index in range(len(data['compounds'])):
        key = '~/compounds/id/{0}'.format(data['compounds'][index]['id'])
        compound_index[key] = index

    # Create a new COBRApy Model object.
    model = Model(data['id'], name=data['name'])

    # Add template compartments to the universal model.
    for index in range(len(data['compartments'])):
        modelseed_compartment = data['compartments'][index]
        model.compartments[modelseed_compartment['id']] = modelseed_compartment['name']

    # Create Metabolite objects for all of the compounds in the template model. Metabolite
    # data is split between the "compcompounds" (compounds in a compartment) and the
    # "compounds" lists.
    for compcompound in data['compcompounds']:
        compound = data['compounds'][compound_index[compcompound['templatecompound_ref']]]
        cobra_id = _convert_suffix(compcompound['id'], id_type)
        metabolite = Metabolite(id=cobra_id,
                                formula=compound['formula'],
                                name=compound['name'],
                                charge=compcompound['charge'],
                                compartment=compcompound['templatecompartment_ref'].split('/')[-1])
        model.add_metabolites([metabolite])

    # Create Reaction objects for all of the reactions in the template model.
    for template_reaction in data['reactions']:
        # Set upper and lower bounds based directionality. Switch reverse reactions to
        # forward reactions.
        reverse = 1.0
        if template_reaction['direction'] == '=':
            lower_bound = -1000.0
            upper_bound = 1000.0
        elif template_reaction['direction'] == '>':
            lower_bound = 0.0
            upper_bound = 1000.0
        elif template_reaction['direction'] == '<':
            lower_bound = 0.0
            upper_bound = 1000.0
            reverse = -1.0
        else:
            warn('Reaction direction {0} assumed to be reversible for reaction {1}'
                 .format(template_reaction['direction'], template_reaction['id']))
            lower_bound = -1000.0
            upper_bound = 1000.0

        # Create the Reaction object.
        reaction = Reaction(id=_convert_suffix(template_reaction['id'], id_type),
                            name=template_reaction['name'],
                            lower_bound=lower_bound,
                            upper_bound=upper_bound)

        # Create dictionary of metabolites and add them to the reaction.
        metabolites = dict()
        for reagent in template_reaction['templateReactionReagents']:
            cobra_metabolite_id = _convert_suffix(reagent['templatecompcompound_ref'].split('/')[-1], id_type)
            metabolite = model.metabolites.get_by_id(cobra_metabolite_id)
            metabolites[metabolite] = float(reagent['coefficient']) * reverse
        reaction.add_metabolites(metabolites)

        # Add a note with the ModelSEED reaction type (universal, spontaneous, conditional, or gapfilling).
        reaction.notes['type'] = template_reaction['type']

        # Finally, add the reaction to the model.
        model.add_reaction(reaction)

    return model


def optimize_modelseed_model(model_id, media_reference=None):
    """ Run flux balance analysis on a ModelSEED model.

    Parameters
    ----------
    model_id : str
        ID of model
    media_reference : str
        Workspace reference to media to optimize on (default is complete media)

    Returns
    -------
    float
        Objective value
    """

    # Get the current list of fba solutions which is the only way to tell if this
    # optimization is successful because fba_count is not updated in the metadata.
    fba_count = len(get_modelseed_fba_solutions(model_id))

    # Set input parameters for method.
    reference = _make_modelseed_reference(model_id)
    params = dict()
    params['model'] = reference
    params['predict_essentiality'] = 1
    if media_reference is not None:
        params['media'] = media_reference

    # Run the server method.
    try:
        job_id = ms_client.call('FluxBalanceAnalysis', params)
        _wait_for_job(job_id)
    except ServerError as e:
        references = [reference]
        if media_reference is not None:
            references.append(media_reference)
        handle_server_error(e, references)

    # The completed job does not have the reference to the fba object that
    # was just created so get the list of solutions. Last completed
    # solution is first in the list.
    solutions = get_modelseed_fba_solutions(model_id)
    if fba_count == len(solutions):
        warn('Optimization for {0} did not return a solution'.format(model_id))
        return 0.0
    return float(solutions[0]['objective'])


def reconstruct_modelseed_model(genome_id, source='patric', template_reference=None, likelihood=False, model_id=None):
    """ Reconstruct a draft ModelSEED model for an organism.

    Parameters
    ----------
    genome_id : str
        Genome ID or workspace reference to genome
    source : {'patric', 'rast', 'workspace'}, optional
        Source of genome
    template_reference : str, optional
        Workspace reference to template model
    likelihood : bool, optional
        True to generate reaction likelihoods
    model_id : str, optional
        ID of output model (default is genome ID)

    Returns
    -------
    dict
        Dictionary of current model statistics
    """

    # Set input parameters for method.
    params = dict()
    if source == 'patric':
        params['genome'] = 'PATRIC:' + genome_id
    elif source == 'rast':
        params['genome'] = 'RAST:' + genome_id
    elif source == 'workspace':
        params['genome'] = genome_id
    else:
        raise ValueError('Source type {0} is not supported'.format(source))
    if model_id is None:
        model_id = genome_id
    params['output_file'] = model_id
    if template_reference is not None:
        params['template_model'] = template_reference
    if likelihood:
        params['probanno'] = 1
    else:
        params['probanno'] = 0
    params['gapfill'] = 0
    params['predict_essentiality'] = 0

    # Workaround for ModelSEED workspace bug. The user's modelseed folder must exist before saving
    # the model. Otherwise the type of the folder created for the model is not "modelfolder" and
    # subsequent operations on the model will fail.
    if ms_client.username is None:
        ms_client.set_authentication_token()
    folder_reference = '/{0}/{1}'.format(ms_client.username, model_folder)
    try:
        get_workspace_object_meta(folder_reference)
    except ObjectNotFoundError:
        put_workspace_object(folder_reference, 'folder')

    # Run the server method.
    try:
        job_id = ms_client.call('ModelReconstruction', params)
    except ServerError as e:
        references = None
        if template_reference is not None:
            references = [template_reference]
        handle_server_error(e, references)

    # The task structure has the workspace where the model is stored but not the name of the model.
    _wait_for_job(job_id)

    # Get the model statistics for the model.
    stats = get_modelseed_model_stats(model_id)
    if stats['num_genes'] == 0:  # ModelSEED does not return an error if the genome ID is invalid
        warn('Model for genome ID {0} has no genes, verify genome ID is valid'.format(genome_id))
    return stats


def _wait_for_job(jobid):
    """ Wait for a job submitted to the ModelSEED app service to end.

    Parameters
    ----------
    jobid : str
        ID of submitted job

    Returns
    -------
    dict
        Task structure with status of job

    Raises
    ------
    JobError
        When a job with the specified ID was not found
    """

    task = None
    done = False
    while not done:
        jobs = ms_client.call('CheckJobs', {})
        if jobid in jobs:
            task = jobs[jobid]
            if task['status'] == 'failed':
                raise ServerError(task['error'])
            elif task['status'] == 'completed':
                done = True
            else:
                sleep(3)
        else:
            raise JobError('Job {0} was not found'.format(jobid))
    return task
