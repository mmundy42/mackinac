from __future__ import absolute_import
from time import sleep
from operator import itemgetter
from warnings import warn
import re
import logging

from cobra import Model, Reaction, Metabolite

from .SeedClient import SeedClient, ServerError, ObjectNotFoundError, JobError, handle_server_error
from .workspace import get_workspace_object_meta, get_workspace_object_data, put_workspace_object
from .modelutil import create_cobra_model, convert_compartment_id, convert_suffix, modelseed_suffix_re, \
    calculate_likelihoods, get_model_statistics

# ModelSEED service endpoint
modelseed_url = 'http://p3c.theseed.org/dev1/services/ProbModelSEED'

# Former ModelSEED production service endpoint
prod_modelseed_url = 'https://p3.theseed.org/services/ProbModelSEED'

# Client for running functions on ModelSEED web service
ms_client = SeedClient(modelseed_url, 'ProbModelSEED')

# Name of folder where ModelSEED models are stored
model_folder = 'modelseed'

# Logger for this module
LOGGER = logging.getLogger(__name__)


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


def calculate_modelseed_likelihoods(model_id, search_program_path, search_db_path, fid_role_path, work_folder):
    """ Calculate reaction likelihoods for a ModelSEED model.

    Reaction likelihood calculation is done locally and results are stored in the
    model's folder in workspace. Caller must run download_data_files() function
    before running this function to prepare for local calculation of likelihoods.

    Parameters
    ----------
    model_id : str
        ID of model
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

    return calculate_likelihoods(_make_modelseed_reference(model_id), search_program_path, search_db_path,
                                 fid_role_path, work_folder)


def delete_modelseed_model(model_id):
    """ Delete a ModelSEED model from the workspace.

    Parameters
    ----------
    model_id : str
        ID of model
    """

    reference = _make_modelseed_reference(model_id)
    LOGGER.info('Started delete model using web service for "%s"', reference)
    try:
        ms_client.call('delete_model', {'model': reference})
    except ServerError as e:
        handle_server_error(e, [reference])
    LOGGER.info('Finished delete model using web service for "%s"', reference)

    return


def gapfill_modelseed_model(model_id, media_reference=None, likelihood=False, comprehensive=False, solver=None):
    """ Run gap fill on a ModelSEED model.

    The ModelSEED model is updated with the reactions identified by gap fill that
    make the model feasible.

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

    LOGGER.info('Started gapfill model using web service for "%s"', reference)
    try:
        job_id = ms_client.call('GapfillModel', params)
        LOGGER.info('Started job %s to run gapfill model for "%s"', job_id, reference)
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
    LOGGER.info('Started get fba solutions using web service for "%s"', reference)
    try:
        get_modelseed_model_stats(model_id)  # Confirm model exists
        solutions = ms_client.call('list_fba_studies', {'model': reference})
    except ServerError as e:
        handle_server_error(e, [reference])
        return
    LOGGER.info('Finished get fba solutions using web service for "%s"', reference)

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


def get_modelseed_gapfill_solutions(model_id, id_type='modelseed'):
    """ Get the list of gap fill solutions for a ModelSEED model.

    Parameters
    ----------
    model_id : str
        ID of model
    id_type : {'modelseed', 'bigg'}
        Type of IDs ('modelseed' for _c or 'bigg' for '[c])

    Returns
    -------
    list
        List of gap fill solution data structures
    """

    reference = _make_modelseed_reference(model_id)
    LOGGER.info('Started get gapfill solutions using web service for "%s"', reference)
    try:
        get_modelseed_model_stats(model_id)  # Confirm model exists
        solutions = ms_client.call('list_gapfill_solutions', {'model': reference})
    except ServerError as e:
        handle_server_error(e, [reference])
    LOGGER.info('Finished get gapfill solutions using web service for "%s"', reference)

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
    LOGGER.info('Started get model data using web service for "%s"', reference)
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

    return get_model_statistics(_make_modelseed_reference(model_id))


def list_modelseed_models(base_folder=None, sort_key='rundate', print_output=False):
    """ List the ModelSEED models for the user.

    Parameters
    ----------
    base_folder : str
        Workspace reference to folder to search for models
    sort_key : {'rundate', 'id', 'name'}, optional
        Name of field to use as sort key for output
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

    LOGGER.info('Started list models using web service')
    try:
        output = ms_client.call('list_models', params)
    except ServerError as e:
        handle_server_error(e)
    LOGGER.info('Finished list models using web service')
    reverse = False
    if sort_key == 'rundate':
        reverse = True
    output.sort(key=itemgetter(sort_key), reverse=reverse)
    if not print_output:
        return output
    for model in output:
        print('Model {0} for organism {1} with {2} reactions and {3} metabolites'
              .format(model['ref'], model['name'], model['num_reactions'], model['num_compounds']))
    return None


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
    cobra.core.Model
        Model object
    """

    return create_cobra_model(_make_modelseed_reference(model_id), id_type=id_type, validate=validate)


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
    cobra.core.Model
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
    LOGGER.info('Started adding %d compartments from template model', len(data['compartments']))
    for index in range(len(data['compartments'])):
        modelseed_compartment = data['compartments'][index]
        model.compartments[modelseed_compartment['id']] = modelseed_compartment['name']
    LOGGER.info('Finished adding %d compartments to model', len(model.compartments))

    # Create Metabolite objects for all of the compounds in the template model. Metabolite
    # data is split between the "compcompounds" (compounds in a compartment) and the
    # "compounds" lists.
    LOGGER.info('Started adding %d metabolites from template model', len(data['compcompounds']))
    all_metabolites = list()
    for compcompound in data['compcompounds']:
        compound = data['compounds'][compound_index[compcompound['templatecompound_ref']]]
        cobra_id = convert_suffix(compcompound['id'], id_type)
        metabolite = Metabolite(id=cobra_id,
                                formula=compound['formula'],
                                name=compound['name'],
                                charge=compcompound['charge'],
                                compartment=compcompound['templatecompartment_ref'].split('/')[-1])
        all_metabolites.append(metabolite)
    model.add_metabolites(all_metabolites)
    LOGGER.info('Finished adding %d metabolites to model', len(model.metabolites))

    # Create Reaction objects for all of the reactions in the template model.
    LOGGER.info('Started adding %d reactions from template model', len(data['reactions']))
    all_reactions = list()
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
        reaction = Reaction(id=convert_suffix(template_reaction['id'], id_type),
                            name=template_reaction['name'],
                            lower_bound=lower_bound,
                            upper_bound=upper_bound)

        # Create dictionary of metabolites and add them to the reaction.
        metabolites = dict()
        for reagent in template_reaction['templateReactionReagents']:
            cobra_metabolite_id = convert_suffix(reagent['templatecompcompound_ref'].split('/')[-1], id_type)
            metabolite = model.metabolites.get_by_id(cobra_metabolite_id)
            metabolites[metabolite] = float(reagent['coefficient']) * reverse
        reaction.add_metabolites(metabolites)

        # Add a note with the ModelSEED reaction type (universal, spontaneous, conditional, or gapfilling).
        reaction.notes['type'] = template_reaction['type']
        all_reactions.append(reaction)

    # Finally, add all of the reactions to the model.
    model.add_reactions(all_reactions)
    LOGGER.info('Finished adding %d reactions to model', len(model.reactions))

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
    LOGGER.info('Started flux balance analysis using web service for "%s"', reference)
    try:
        job_id = ms_client.call('FluxBalanceAnalysis', params)
        LOGGER.info('Started job %s to run flux balance analysis for "%s"', job_id, reference)
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
        LOGGER.info('Created modelseed folder in workspace for "%s"', ms_client.username)

    # Run the server method.
    LOGGER.info('Started model reconstruction using web service for "%s"', params['genome'])
    try:
        job_id = ms_client.call('ModelReconstruction', params)
    except ServerError as e:
        references = None
        if template_reference is not None:
            references = [template_reference]
        handle_server_error(e, references)
    LOGGER.info('Started job %s to run model reconstruction for "%s"', job_id, params['genome'])

    # The task structure has the workspace where the model is stored but not the name of the model.
    _wait_for_job(job_id)

    # Get the model statistics for the model.
    stats = get_modelseed_model_stats(model_id)
    if stats['num_genes'] == 0:  # ModelSEED does not return an error if the genome ID is invalid
        warn('Model for genome ID {0} has no genes, verify genome ID is valid'.format(genome_id))
    return stats


def _wait_for_job(job_id):
    """ Wait for a job submitted to the ModelSEED app service to end.

    Parameters
    ----------
    job_id : str
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

    LOGGER.info('Started to wait for job %s', job_id)
    task = None
    done = False
    while not done:
        jobs = ms_client.call('CheckJobs', {})
        if job_id in jobs:
            task = jobs[job_id]
            if task['status'] == 'failed':
                if 'error' in task:
                    raise ServerError(task['error'])
                raise ServerError('Job submitted to ModelSEED app service failed, no details provided in response')
            elif task['status'] == 'completed':
                LOGGER.info('Job %s completed successfully', job_id)
                done = True
            else:
                sleep(3)
        else:
            raise JobError('Job {0} was not found'.format(job_id))
    return task
