from six import string_types

from cobra.core import Object

# Required fields in source file for creating a TemplateCompartment object.
compartment_fields = {'id', 'name', 'index'}


def create_template_compartment(fields, names):
    """ Create a TemplateCompartment object from a list of fields.
    
    Parameters
    ----------
    fields : list of str
        Each element is a field from a text file defining a compartment
    names : dict
        Dictionary with field name as key and list index number as value
        
    Returns
    -------
    TemplateCompartment
        Object created from input fields
    """

    compartment = TemplateCompartment(
        id=fields[names['index']],
        model_id=fields[names['id']],
        name=fields[names['name']])
    if 'hierarchy' in names:
        compartment.hierarchy = int(fields[names['hierarchy']])
    if 'pH' in names:
        compartment.pH = float(fields[names['pH']])
    if 'aliases' in names:
        compartment.aliases = fields[names['aliases']]
    return compartment


class TemplateCompartment(Object):
    """ A compartment is a region in a cell of an organism.
    
    In a template model, compartment IDs must correspond to the index numbers
    that identify the compartment in a reaction stoichiometry. See the
    resolve_universal_reactions() function for details.
    
    Parameters
    ----------
    id : str
        ID of compartment
    model_id : str
        ID of compartment when added to an organism model
    name : str
        Descriptive name of compartment
    hierarchy : int, optional
        Number describing where compartment is in the hierarchy (unused)
    pH : float, optional
        Value of pH of compartment (unused)
        
    Attributes
    ----------
    _aliases : list of str
        Alternative names of compartment
    """

    def __init__(self, id, model_id, name, hierarchy=1, pH=7.0):
        Object.__init__(self, id, name)
        self.model_id = model_id
        self.hierarchy = hierarchy
        self.pH = pH

        self._aliases = list()
        return

    @property
    def aliases(self):
        return self._aliases

    @aliases.setter
    def aliases(self, new_aliases):
        if isinstance(new_aliases, string_types):
            if new_aliases != 'null':
                self._aliases = new_aliases.split(';')
        elif isinstance(new_aliases, list):
            self._aliases = new_aliases
        else:
            raise TypeError('Aliases for a compartment must be a string or a list')
