from os.path import join
import json
from time import sleep

from .SeedClient import SeedClient, handle_server_error, ServerError, JobError
from .modelutil import get_model_statistics, create_cobra_model, calculate_likelihoods, \
    convert_gapfill_solutions, convert_fba_solutions, metadata_to_statistics
from .workspace import delete_workspace_object, list_workspace_objects, get_workspace_object_meta, \
    get_workspace_object_data
from .genome import get_genome_summary
from .logger import LOGGER

# PATRIC app service endpoint
patric_app_url = 'https://p3.theseed.org/services/app_service'

# Client for running functions on PATRIC app service
patric_client = SeedClient(patric_app_url, 'AppService')

# Name of home folder for a PATRIC user
home_folder = 'home'

# Name of folder where PATRIC models are stored
model_folder = 'models'


def check_patric_app_service():
    """ Check the status of the PATRIC app service.

    Returns
    -------
    bool
        True when app service job submission is enabled
    """

    status = patric_client.call('service_status', {})
    if status[0] == '1':
        return True
    raise ServerError('PATRIC app service at {0} is not available: {1}'
                      .format(patric_app_url, status[1]))


def list_patric_apps():
    """ Get a list of apps currently available through app service.

    Returns
    -------
    list of dict
        List of App dictionaries with details on available apps
    """

    return patric_client.call('enumerate_apps', {})


def calculate_patric_likelihoods(model_id, search_program_path, search_db_path, fid_role_path, work_folder):
    """ Calculate reaction likelihoods for a PATRIC model.

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

    return calculate_likelihoods(_make_patric_model_reference(model_id), search_program_path, search_db_path,
                                 fid_role_path, work_folder)


def create_patric_model(genome_id, model_id, media_reference=None, template_reference=None, output_folder=None):
    """ Reconstruct, gap fill, and optimize a PATRIC model for an organism.

    Parameters
    ----------
    genome_id : str
        Genome ID for organism
    model_id : str
        ID of output model
    media_reference: str, optional
        Workspace reference to media to gap fill on (default is complete media)
    template_reference : str, optional
        Workspace reference to template model
    output_folder : str, optional
        Workspace reference to folder for storing model

    Returns
    -------
    dict
        Dictionary of current model statistics
    """

    # Confirm genome ID is available in PATRIC.
    get_genome_summary(genome_id)

    # Set input parameters for method.
    params = dict()
    params['genome'] = 'PATRICSOLR:' + genome_id
    params['output_file'] = model_id
    params['fulldb'] = 0
    if template_reference is not None:
        get_workspace_object_meta(template_reference)  # Confirm template object exists
        params['template_model'] = template_reference
    if media_reference is not None:
        get_workspace_object_meta(media_reference)  # Confirm media object exists
        params['media'] = media_reference
    if output_folder is None:
        params['output_path'] = _make_patric_model_folder_reference()
    else:
        params['output_path'] = output_folder

    # Run the server method.
    try:
        task = patric_client.call('start_app', ['ModelReconstruction', params, params['output_path']])
        LOGGER.info('Started task %s to run model reconstruction for "%s"', task['id'], params['genome'])
        _wait_for_patric_task(task['id'])
    except ServerError as e:
        references = None
        if template_reference is not None:
            references = [template_reference]
        raise handle_server_error(e, references)

    return get_patric_model_stats(model_id)


def create_cobra_model_from_patric_model(model_id, id_type='modelseed', validate=False):
    """ Create a COBRA model from a PATRIC model.

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

    return create_cobra_model(_make_patric_model_reference(model_id), id_type=id_type, validate=validate)


def delete_patric_model(model_id):
    """ Delete a PATRIC model from the workspace.

    Parameters
    ----------
    model_id : str
        ID of model
    """

    # A PATRIC model has both a folder and a model object in the user's model
    # folder so both need to be deleted.
    folder_reference = _make_patric_model_reference(model_id)
    object_reference = join(_make_patric_model_folder_reference(), model_id)
    LOGGER.info('Started delete model using web service for "%s"', folder_reference)
    try:
        delete_workspace_object(folder_reference, force=True)
        delete_workspace_object(object_reference)
    except ServerError as e:
        raise handle_server_error(e, [folder_reference, object_reference])
    LOGGER.info('Finished delete model using web service for "%s"', folder_reference)

    return


def get_patric_fba_solutions(model_id):
    """ Get the list of fba solutions available for a PATRIC model.

    Parameters
    ----------
    model_id : str
        ID of model

    Returns
    -------
    list
        List of fba solution data structures
    """

    # Get the list of fba objects in the model's fba folder.
    reference = _make_patric_model_reference(model_id)
    LOGGER.info('Started get list of fba solution objects using web service for "%s"', reference)
    get_model_statistics(reference)  # Confirm model exists
    objects = list_workspace_objects(join(reference, 'fba'), sort_key='name', recursive=False,
                                     print_output=False, query={'type': ['fba']})
    LOGGER.info('Finished get list of fba solution objects using web service for "%s", found %d solutions',
                reference, len(objects))

    # Build a list of fba solutions in same format as returned by ModelSEED list_fba_studies method.
    solutions = list()
    for obj in objects:
        # For some reason, metadata for a fba object is not set in the output
        # returned by list_workspace_objects().
        meta = get_workspace_object_meta(join(obj[2], obj[0]))
        sol = dict()
        sol['id'] = meta[0]
        sol['media_ref'] = meta[7]['media']
        sol['objective'] = meta[8]['objectiveValue']
        sol['objective_function'] = meta[8]['objective_function']
        sol['ref'] = join(meta[2], meta[0])
        sol['rundate'] = meta[3]
        solutions.append(sol)
    return convert_fba_solutions(solutions)


def get_patric_gapfill_solutions(model_id, id_type='modelseed'):
    """ Get the list of gap fill solutions for a PATRIC model.

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

    # Get the list of fba objects in the model's fba folder.
    reference = _make_patric_model_reference(model_id)
    LOGGER.info('Started get list of gapfill solution objects using web service for "%s"', reference)
    get_model_statistics(reference)  # Confirm model exists
    objects = list_workspace_objects(join(reference, 'gapfilling'), sort_key='name', recursive=False,
                                     print_output=False, query={'type': ['fba']})
    LOGGER.info('Finished get list of gapfill solution objects using web service for "%s", found %d solutions',
                reference, len(objects))

    # Build a list of gapfill solutions in same format as returned by ModelSEED list_gapfill_solutions method.
    # Note that only the first element in the solutiondata list is used. Never understood how there
    # could be more than one.
    solutions = list()
    for obj in objects:
        sol = dict()
        sol['id'] = obj[0]
        sol['integrated'] = obj[7]['integrated']
        sol['integrated_solution'] = obj[7]['integrated_solution']
        sol['media_ref'] = obj[7]['media']
        sol['ref'] = join(obj[2], obj[0])
        sol['rundate'] = obj[3]
        reactions = list()
        data = json.loads(obj[7]['solutiondata'])
        for rxn in data[0]:
            compartment = '{0}{1}'.format(rxn['compartment_ref'].split('/')[-1], rxn['compartmentIndex'])
            reactions.append({
                'reaction': rxn['reaction_ref'],
                'direction': rxn['direction'],
                'compartment': compartment
            })
        sol['solution_reactions'] = list()
        sol['solution_reactions'].append(reactions)
        solutions.append(sol)
    return convert_gapfill_solutions(solutions, id_type)


def get_patric_model_data(model_id):
    """ Get the model data for a PATRIC model.

    Parameters
    ----------
    model_id : str
        ID of model

    Returns
    -------
    dict
        Dictionary of all model data
    """

    reference = join(_make_patric_model_reference(model_id), 'model')
    LOGGER.info('Started get model data using web service for "%s"', reference)
    try:
        return get_workspace_object_data(reference)
    except ServerError as e:
        raise handle_server_error(e, [reference])


def get_patric_model_stats(model_id):
    """ Get the model statistics for a PATRIC model.

    Parameters
    ----------
    model_id : str
        ID of model

    Returns
    -------
    dict
        Dictionary of current model statistics
    """

    return get_model_statistics(_make_patric_model_reference(model_id))


def list_patric_models(sort_key='date', print_output=False):
    """ List the PATRIC models for the user.

    Parameters
    ----------
    sort_key : {'date', 'id', 'name'}, optional
        Name of field to use as sort key for output
    print_output : bool, optional
        When True, print a summary of the list instead of returning the list

    Returns
    -------
    list or None
        List of model statistics dictionaries or None if printed output
    """

    # Get the list of model objects in the model folder.
    objects = list_workspace_objects(_make_patric_model_folder_reference(), sort_key=sort_key, recursive=False,
                                     print_output=False, query={'type': ['model']})
    if objects is None:
        if print_output:
            print('There are no models available.')
        return None

    # Convert object metadata to model statistics dictionary.
    output = list()
    for metadata in objects:
        output.append(metadata_to_statistics(metadata))

    # Return the list if not printing the output.
    if not print_output:
        return output

    # Print a summary of models in the model folder.
    for model in output:
        print('Model "{0}" for organism "{1}" with {2} reactions and {3} metabolites'
              .format(model['id'], model['name'], model['num_reactions'], model['num_compounds']))
    return None


def _make_patric_home_folder_reference():
    """ Make a workspace reference to user's home folder.

    Returns
    -------
    str
        Reference to user's home folder
    """

    if patric_client.username is None:
        patric_client.set_authentication_token()
    return '/{0}/{1}'.format(patric_client.username, home_folder)


def _make_patric_model_folder_reference():
    """ Make a workspace reference to user's PATRIC model folder.

    Returns
    -------
    str
        Reference to user's model folder
    """

    return '{0}/{1}'.format(_make_patric_home_folder_reference(), model_folder)


def _make_patric_model_reference(model_id):
    """ Make a workspace reference to a specific PATRIC model's folder.

    Parameters
    ----------
    model_id : str
        ID of model

    Returns
    -------
    str
        Reference to model in user's model folder
    """

    return '{0}/.{1}'.format(_make_patric_model_folder_reference(), model_id)


def _wait_for_patric_task(task_id):
    """ Wait for a task submitted to the PATRIC app service to end.

    Parameters
    ----------
    task_id : str
        ID of submitted task

    Returns
    -------
    dict
        Task structure which includes status of job

    Raises
    ------
    JobError
        When a task with the specified ID was not found
    """

    LOGGER.info('Started to wait for task %s', task_id)
    task = None
    done = False
    while not done:
        tasks = patric_client.call('query_tasks', [[task_id]])
        if task_id in tasks:
            task = tasks[task_id]
            if task['status'] == 'failed':
                LOGGER.info('Task %s failed', task_id)
                if 'error' in task:
                    raise ServerError(task['error'])
                raise ServerError('Task submitted to PATRIC app service failed, no details provided in response')
            elif task['status'] == 'completed':
                LOGGER.info('Task %s completed successfully', task_id)
                done = True
            else:
                sleep(3)
        else:
            raise JobError('Task {0} was not found'.format(task_id))
    return task
