from time import sleep
from os.path import join

from .SeedClient import SeedClient, handle_server_error, ServerError, JobError
from .modelutil import get_model_statistics, create_cobra_model, calculate_likelihoods
from .workspace import delete_workspace_object
from .logger import LOGGER

# PATRIC app service endpoint
patric_app_url = 'https://p3.theseed.org/services/app_service'

# Client for running functions on PATRIC app service
patric_client = SeedClient(patric_app_url, 'AppService')


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


def create_patric_model(genome_id, model_id, output_folder=None, media_reference=None, template_reference=None):
    """ Reconstruct and gap fill a PATRIC model for an organism.

    Parameters
    ----------
    genome_id : str
        Genome ID for organism
    model_id : str
        ID of output model
    template_reference : str, optional
        Workspace reference to template model
    output_folder : str, optional
        Workspace reference to folder for storing model

    Returns
    -------
    dict
        Dictionary of current model statistics
    """

    # Set input parameters for method.
    params = dict()
    params['genome'] = 'PATRICSOLR:' + genome_id
    params['output_file'] = model_id
    params['fulldb'] = 0
    if template_reference is not None:
        params['template_model'] = template_reference
    folder_reference = _make_patric_folder_reference()
    if output_folder is None:
        params['output_path'] = folder_reference
    else:
        params['output_path'] = output_folder

    # Run the server method.
    LOGGER.info('Started model reconstruction using app service for "%s"', params['genome'])
    try:
        task = patric_client.call('start_app', ['ModelReconstruction', params, params['output_path']])
    except ServerError as e:
        references = None
        if template_reference is not None:
            references = [template_reference]
        handle_server_error(e, references)
    LOGGER.info('Started task %s to run model reconstruction for "%s"', task['id'], params['genome'])
    _wait_for_task(task['id'])

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
    object_reference = join(_make_patric_folder_reference(), model_id)
    LOGGER.info('Started delete model using web service for "%s"', folder_reference)
    try:
        delete_workspace_object(folder_reference, force=True)
        delete_workspace_object(object_reference)
    except ServerError as e:
        handle_server_error(e, [folder_reference, object_reference])
    LOGGER.info('Finished delete model using web service for "%s"', folder_reference)

    return


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


def _make_patric_folder_reference():
    """ Make a workspace reference to user's PATRIC model folder.

    Returns
    -------
    str
        Reference to user's model folder
    """

    if patric_client.username is None:
        patric_client.set_authentication_token()
    return '/{0}/home/models'.format(patric_client.username)


def _make_patric_model_reference(model_id):
    """ Make a workspace reference to a PATRIC model.

    Parameters
    ----------
    model_id : str
        ID of model

    Returns
    -------
    str
        Reference to model in user's model folder
    """

    return '{0}/.{1}'.format(_make_patric_folder_reference(), model_id)


def _wait_for_task(task_id):
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
