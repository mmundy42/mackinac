from operator import itemgetter
import json
import requests

from .SeedClient import SeedClient, ServerError, handle_server_error

# Workspace service endpoint
workspace_url = 'https://p3.theseed.org/services/Workspace'

# Client for running functions on Workspace web service.
ws_client = SeedClient(workspace_url, 'Workspace')


def shock_download(url, token):
    """ Download data from a Shock node.

    Parameters
    ----------
    url : str
        URL to Shock node
    token : str
        Authentication token for Patric web services

    Returns
    -------
    str
        Data from Shock node
    """

    response = requests.get(url + '?download', headers={'AUTHORIZATION': 'OAuth ' + token})
    if response.status_code != requests.codes.OK:
        response.raise_for_status()
    return response.text


def get_workspace_object_meta(reference):
    """ Get the metadata for an object.

    Parameters
    ----------
    reference : str
        Workspace reference to object

    Returns
    -------
    dict
        ObjectMeta tuple with metadata
    """

    try:
        # The output from get() is a list of tuples.  When asking for metadata only,
        # the list entry is a tuple with only one element.
        metadata_list = ws_client.call('get', {'objects': [reference], 'metadata_only': 1})
        return metadata_list[0][0]
    except ServerError as e:
        handle_server_error(e, [reference])


def get_workspace_object_data(reference, json_data=True):
    """ Get the data for an object.

    Parameters
    ----------
    reference : str
        Workspace reference to object
    json_data : bool, optional
        When True, convert data from returned JSON format

    Returns
    -------
    data
        Object data (can be dict, list, or string)
    """

    data = None
    try:
        # The output from get() is a list of tuples. The first element in the
        # tuple is the metadata which has the url to the Shock node when the
        # data is stored in Shock. Otherwise the data is available in the second
        # element of the tuple.
        object_list = ws_client.call('get', {'objects': [reference]})
        if len(object_list[0][0][11]) > 0:
            data = shock_download(object_list[0][0][11], ws_client.headers['AUTHORIZATION'])
        else:
            data = object_list[0][1]
    except Exception as e:
        handle_server_error(e, [reference])

    if json_data:
        return json.loads(data)
    return data


def list_workspace_objects(folder, sort_key='folder', print_output=False):
    """ List the objects in the specified workspace folder.

    Parameters
    ----------
    folder : str
        Workspace reference to folder
    sort_key : {'folder', 'name', 'date', 'type'}, optional
        Name of field to use as sort key for output
    print_output : bool, optional
        When True, print formatted output instead of returning the list

    Returns
    -------
    list or None
        List of object data for objects in folder or None if printed output
    """

    # Get the list of objects in the specified folder.
    try:
        output = ws_client.call('ls', {'paths': [folder], 'recursive': 1})
    except ServerError as e:
        handle_server_error(e, [folder])

    # See if the folder is in the returned data.
    if folder not in output:
        if print_output:
            print('No data for folder {0} was available'.format(folder))
        return None

    # Sort the objects by the specified key.
    reverse = False
    if sort_key == 'name':
        key = 0
    elif sort_key == 'folder':
        key = 2
    elif sort_key == 'date':
        key = 3
        reverse = True
    elif sort_key == 'type':
        key = 1
    else:
        raise ValueError('Sort key {0} is not supported'.format(sort_key))
    output[folder].sort(key=itemgetter(key), reverse=reverse)

    # Print details on the objects.
    if print_output:
        print('Contents of {0}:'.format(folder))
        for object_data in output[folder]:
            otype = '-'
            if object_data[1] == 'folder' or object_data[8]['is_folder']:
                otype = 'd'
            print('{0}{1}{2} {3:10}\t{4:>10}\t{5}\t{6:12}\t{7}{8}'
                  .format(otype, object_data[9], object_data[10], object_data[5], object_data[6],
                          object_data[3], object_data[1], object_data[2], object_data[0]))
        return None

    return output[folder]
