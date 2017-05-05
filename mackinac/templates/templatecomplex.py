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
    if fields[names['roles']] != 'null':
        complx.roles = fields[names['roles']]
    return complx


class TemplateComplex(Object):
    """ A complex is a set of chemical reactions that act in concert to effect a role.

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
    roles : list of dict, optional
        List of roles that trigger the complex
    reaction_ids : list of str
        IDs of reactions that do something to the complex
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
        # Link the complex to one or more roles.
        links = new_roles.split('|')
        for index in range(len(links)):
            values = links[index].split(';')
            self.roles.append({'role_id': values[0],
                               'type': values[1],
                               'optional': int(values[2]),
                               'triggering': int(values[3])})
