import re
from six import string_types

from cobra.core import Object

from .util import make_search_name, ec_number_re, tc_number_re

# Required fields in source file for creating a TemplateRole object.
role_fields = {'id', 'name', 'source', 'features', 'aliases'}


def create_template_role(fields, names):
    """ Create a TemplateRole object from a list of fields.

    Parameters
    ----------
    fields : list of str
        Each element is a field from a text file defining a role
    names : dict
        Dictionary with field name as key and list index number as value

    Returns
    -------
    TemplateRole
        Object created from input fields
    """

    role = TemplateRole(
        id=fields[names['id']],
        name=fields[names['name']],
        source=fields[names['source']])
    if fields[names['features']] != 'null':
        role.features = fields[names['features']]
    if fields[names['aliases']] != 'null':
        role.aliases = fields[names['aliases']]
    return role


class TemplateRole(Object):
    """ A role is a biological function fulfilled by a feature.
    
    Most roles are effected by the construction of proteins. Some, however, 
    deal with functional regulation and message transmission.
        
    Parameters
    ----------
    id : str
        ID of role
    name : str, optional
        Descriptive name of role
    source : str, optional
        Source of role (e.g. "ModelSEED", "KEGG")
        
    Attributes
    ----------
    _features : str or list
        Features associated with role
    _aliases : str or list
        Alternate names or IDs for role
    complex_ids : set
        IDs of complexes that trigger the role
    ec_numbers : list of str
        EC (Enzyme Commission) numbers from name of role
    tc_numbers : list of str
        TC (Transporter Classification) numbers from name of role
    search_name : list of str
        Search name of role
    """

    def __init__(self, id, name='', source=''):
        Object.__init__(self, id, name)
        self.source = source

        self._features = list()
        self._aliases = list()
        self.complex_ids = set()

        # Extract EC (Enzyme Commission) numbers from the name.
        self.ec_numbers = re.findall(ec_number_re, self.name)

        # Extract the TC (Transporter Classification) number if it is specified in the name.
        self.tc_numbers = re.findall(tc_number_re, self.name)

        # Generate primary search name for the role.
        self.search_name = [make_search_name(self.name)]
        return

    @property
    def features(self):
        return self._features

    @features.setter
    def features(self, new_features):
        if isinstance(new_features, string_types):
            self._features = new_features.split(';')
        elif isinstance(new_features, list):
            self._features = new_features
        else:
            raise TypeError('Features for a role must be a string or a list')

    @property
    def aliases(self):
        return self._aliases

    @aliases.setter
    def aliases(self, new_aliases):
        if isinstance(new_aliases, string_types):
            self._aliases = new_aliases.split(';')
        elif isinstance(new_aliases, list):
            self._aliases = new_aliases
        else:
            raise TypeError('Aliases for a role must be a string or a list')
