from warnings import warn
import re

from cobra.core import DictList


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
            if len(fields) < len(required):
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
