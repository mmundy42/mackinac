from six import string_types

from cobra.core import Object

# Required fields in source file for creating a TemplateComplex object.
complex_fields = {'id', 'name', 'source', 'reference', 'confidence', 'roles'}


def create_template_complex(fields, names):
    """ Create a TemplateComplex object from a list of fields.

    Parameters
    ----------
    fields : list of str
        Each element is a field from a text file defining a complex
    names : dict
        Dictionary with field name as key and list index number as value

    Returns
    -------
    TemplateComplex
        Object created from input fields
    """

    complx = TemplateComplex(
        id=fields[names['id']],
        name=fields[names['name']],
        source=fields[names['source']],
        reference=fields[names['reference']],
        confidence=float(fields[names['confidence']]))
    complx.roles = fields[names['roles']]
    return complx


class TemplateComplex(Object):
    """ A complex is a set of chemical reactions that act in concert to effect a role.

    A role dictionary has four keys: (1) 'role_id' (str), (2) 'type' (str), 
    {3} 'optional' flag (int), (4) 'triggering' flag (int).
    
    Parameters
    ----------
    id : str
        ID of complex
    name : str, optional
        Descriptive name of complex
    source : str, optional
        Source of complex
    reference : str, optional
        Reference to where complex came from
    confidence : float, optional
        Confidence in complex (value between 0 and 1)
        
    Attributes
    ----------
    _roles : list of dict, optional
        List of roles that trigger the complex
    reaction_ids : set of str
        IDs of reactions that are catalyzed by the complex
    """

    def __init__(self, id, name='', source='', reference='', confidence=1.0):
        Object.__init__(self, id, name)
        self.source = source
        if reference == 'null':
            reference = ''
        self.reference = reference
        self.confidence = confidence

        self._roles = list()
        self.reaction_ids = set()
        return

    @property
    def roles(self):
        return self._roles

    @roles.setter
    def roles(self, new_roles):
        if isinstance(new_roles, string_types):
            if new_roles != 'null':
                for role in new_roles.split('|'):
                    fields = role.split(';')
                    self.roles.append({'role_id': fields[0],
                                       'type': fields[1],
                                       'optional': int(fields[2]),
                                       'triggering': int(fields[3])})
        elif isinstance(new_roles, list):
            self._roles = new_roles
        else:
            raise TypeError('Roles for a complex must be a string or a list')
