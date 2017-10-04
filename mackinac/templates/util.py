from warnings import warn
import re
import json
import jsonschema

from cobra.core import DictList, Reaction


# Regular expression for compartment suffix on a universal metabolite ID
universal_compartment_suffix_re = re.compile(r'_([\d]+)$')

# Regular expression to match EC number notation
ec_number_re = re.compile(r'\(EC ([\d\-]+\.[\d\-]+\.[\d\-]+\.[\d\-]+)\)')

# Regular expression to match TC number notation
tc_number_re = re.compile(r'\(TC ([\d\-]+\.[\w]+\.[\d\-]+\.[\d\-]+\.[\d\-]+)\)')

# Regular expression to match "NAD(P)" string (details below)
nadp_re = re.compile(r'NAD\(P\)')

# Regular expression to remove whitespace
whitespace_re = re.compile(r'\s')

# Regular expression to remove comments
comment_re = re.compile(r'#.*$')

# Regular expression to remove special characters
special_chars_re = re.compile(r'[-;:()\[\]\',>]*')


class DuplicateError(Exception):
    """ Exception raised when a duplicate ID is found in a source file. """
    pass


def validate_header(fields, required):
    """ Validate the header line in a source file. 
    
    Parameters
    ----------
    fields : list of str
        Each element is the name of a field from a header line
    required : set of str
        Each element is the name of a required field
        
    Returns
    -------
    dict
        Dictionary with field name as key and list index number as value
    """

    # Map field names to column numbers.
    names = {fields[index]: index for index in range(len(fields))}

    # Confirm that required field names are in the header line.
    for req in required:
        if req not in names:
            raise ValueError('Required field {0} is missing from header line'.format(req))

    return names


def read_json_file(file_name, schema, creator):
    """ Read a JSON file that defines a collection of objects.

    Each element in the JSON file is an object with an ID property and properties
    that define the object. The JSON data is validated against the provided schema.

    The creator function must accept one input parameter: (1) a dictionary that
    maps object attributes to their values.

    Parameters
    ----------
    file_name : str
        Path to JSON file
    schema : dict
        JSON schema to validate data from file
    creator : function
        Function that creates an object defined in the file

    Returns
    -------
    cobra.core.DictList
        Each entry in the list is an object created by the creator function
    """

    # Load the JSON file and confirm that it matches the schema.
    object_data = json.load(open(file_name, 'r'))
    jsonschema.validate(object_data, schema)

    # Get the object attributes and create the corresponding object.
    object_list = DictList()
    skipped = 0
    for object_id in object_data:
        if object_list.has_id(object_id):
            raise DuplicateError('Object with ID {0} is a duplicate'.format(object_id))
        new_object = creator(object_data[object_id])
        if new_object is not None:
            object_list.append(new_object)
        else:
            skipped += 1

    if skipped > 0:
        warn('{0} objects in "{1}" were skipped because object could not be created'.format(skipped, file_name))
    return object_list


def read_source_file(filename, required, creator):
    """ Read a source file that defines a list of objects.
    
    There is one object per line in the file with fields separated by tabs.
    The first line of the file is a header with the field names.

    The creator function must accept two input parameters: (1) a list of the
    fields from a line in the file and (2) a dict that maps field names to
    positions in the list of fields. The creator function returns either an 
    object when successful or None when the source data is invalid.
    
    Parameters
    ----------
    filename : str
        Path to source file
    required : set of str
        Each element is the name of a required field
    creator : function
        Function that creates an object defined in the file
        
    Returns
    -------
    cobra.core.DictList
        Each entry in the list is an object created by the creator function
    """

    object_list = DictList()
    skipped = 0
    with open(filename, 'r') as handle:
        # The first line has the header with the field names (which can be in any order).
        names = validate_header(handle.readline().strip().split('\t'), required)

        # There is one object per line in the file.
        linenum = 1
        for line in handle:
            # Get the object data and create the corresponding object.
            linenum += 1
            fields = line.strip().split('\t')
            if len(fields) < len(names):
                warn('Skipped object on line {0} because missing one or more fields: {1}'
                     .format(linenum, fields))
                skipped += 1
                continue
            if object_list.has_id(fields[names['id']]):
                raise DuplicateError('Object with ID {0} on line {1} is a duplicate'
                                     .format(fields[names['id']], linenum))
            new_object = creator(fields, names)
            if new_object is not None:
                object_list.append(new_object)
            else:
                skipped += 1

    if skipped > 0:
        warn('{0} lines in "{1}" were skipped because object could not be created'.format(skipped, filename))
    return object_list


def change_compartment(metabolite, new_compartment):
    """ Change the compartment of a universal metabolite. 
    
    Parameters
    ----------
    metabolite : cobra.core.Metabolite
        Metabolite object to be changed
    new_compartment : str
        ID of new compartment for metabolite
        
    Returns
    -------
    cobra.core.Metabolite
        Updated Metabolite object
    """

    metabolite.compartment = new_compartment
    stripped_id = re.sub(universal_compartment_suffix_re, '', metabolite.id)
    metabolite.id = '{0}_{1}'.format(stripped_id, new_compartment)
    return metabolite


def make_search_name(name):
    """ Make a search name from a name.

    A search name is created by removing special characters, whitespace,
    comments, EC numbers, and TC numbers from a name.
    
    Parameters
    ----------
    name : str
        Name to convert to a search name
        
    Returns
    -------
    str
        Search name string
    """

    search_name = name
    # Remove EC number
    search_name = re.sub(ec_number_re, '', search_name)
    # Remove TC number
    search_name = re.sub(tc_number_re, '', search_name)
    # Switch parenthesis to curly brace so other parenthesis can be removed
    search_name = re.sub(nadp_re, 'NAD{P}', search_name)
    # Lower case everything
    search_name = search_name.lower()
    # Remove whitespace
    search_name = re.sub(whitespace_re, '', search_name)
    # Remove comments from the end
    search_name = re.sub(comment_re, '', search_name)
    # Remove special characters
    search_name = re.sub(special_chars_re, '', search_name)
    return search_name


def print_reaction_to_roles(output):
    """ Print output from TemplateModel.reaction_to_role() method.

    Parameters
    ----------
    output : dict
        Dictionary keyed by reaction ID with details on each role linked to reaction
    """

    for reaction_id in sorted(output):
        print('{0} "{1}" links to {2} roles'
              .format(reaction_id, output[reaction_id]['name'], len(output[reaction_id]['roles'])))
        for role_id in sorted(output[reaction_id]['roles']):
            data = output[reaction_id]['roles'][role_id]
            print('    {0} "{1}" from complex {2}'.format(role_id, data['name'], data['complex_id']))
    return


def print_role_to_reactions(output):
    """ Print output from TemplateModel.role_to_reaction() method.
    
    Parameters
    ----------
    output : dict
        Dictionary keyed by role ID with details on each reaction linked to role
    """

    for role_id in sorted(output):
        print('{0} "{1}" links to {2} reactions'
              .format(role_id, output[role_id]['name'], len(output[role_id]['reactions'])))
        for reaction_id in sorted(output[role_id]['reactions']):
            data = output[role_id]['reactions'][reaction_id]
            print('    {0} "{1}" from complex {2}'.format(reaction_id, data['name'], data['complex_id']))
    return


def create_boundary(metabolite, type="exchange", reaction_id=None, lb=None, ub=1000.0):
    """ Create a boundary reaction for a given metabolite.

    Note this function is adapted from cobra.core.Model.add_boundary() method
    by modifying it to only create the reaction and not add it to a model.

    There are three different types of pre-defined boundary reactions:
    exchange, demand, and sink reactions.
    An exchange reaction is a reversible, imbalanced reaction that adds
    to or removes an extracellular metabolite from the extracellular
    compartment.
    A demand reaction is an irreversible reaction that consumes an
    intracellular metabolite.
    A sink is similar to an exchange but specifically for intracellular
    metabolites.

    If you set the reaction `type` to something else, you must specify the
    desired identifier of the created reaction along with its upper and
    lower bound. The name will be given by the metabolite name and the
    given `type`.

    Parameters
    ----------
    metabolite : cobra.core.Metabolite
        Any given metabolite. The compartment is not checked but you are
        encouraged to stick to the definition of exchanges and sinks.
    type : str, {"exchange", "demand", "sink"}
        Using one of the pre-defined reaction types is easiest. If you
        want to create your own kind of boundary reaction choose
        any other string, e.g., 'my-boundary'.
    reaction_id : str, optional
        The ID of the resulting reaction. Only used for custom reactions.
    lb : float, optional
        The lower bound of the resulting reaction. Only used for custom
        reactions.
    ub : float, optional
        The upper bound of the resulting reaction. For the pre-defined
        reactions this default value determines all bounds.

    Returns
    -------
    cobra.core.Reaction
        The created boundary reaction
    """

    types = dict(exchange=("EX", -ub, ub), demand=("DM", 0, ub), sink=("SK", -ub, ub))
    if type in types:
        prefix, lb, ub = types[type]
        reaction_id = "{}_{}".format(prefix, metabolite.id)
    name = "{} {}".format(metabolite.name, type)
    rxn = Reaction(id=reaction_id, name=name, lower_bound=lb, upper_bound=ub)
    rxn.add_metabolites({metabolite: -1})
    return rxn


def direction_to_bounds(direction):
    """ Convert reaction direction to upper and lower bounds.

    Parameters
    ----------
    direction : {'=', '<', '>'}
        Reaction direction symbol from source file

    Returns
    -------
    tuple
        Lower bound and upper bound
    """

    if direction == '=':
        return -1000.0, 1000.0
    elif direction == '>':
        return 0.0, 1000.0
    elif direction == '<':
        return -1000.0, 0.0
    else:
        raise ValueError('Direction {0} is not valid'.format(direction))
