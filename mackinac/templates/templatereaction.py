from cobra.core import Reaction

# Required fields in source file for creating a TemplateReaction object.
reaction_fields = {
    'id', 'compartment', 'direction', 'gfdir', 'type', 'base_cost', 'forward_cost',
    'reverse_cost', 'complexes'
}

# Valid values for template reaction type field.
reaction_types = {'universal', 'spontaneous', 'conditional', 'gapfilling'}


def create_template_reaction(fields, names):
    """ Create a TemplateReaction object from a list of fields.

    Parameters
    ----------
    fields : list of str
        Each element is a field from a text file defining a reaction
    names : dict
        Dictionary with field name as key and list index number as value

    Returns
    -------
    TemplateReaction
        Object created from input fields
    """

    reaction = TemplateReaction(id=fields[names['id']])
    reaction.compartments = fields[names['compartment']]
    if fields[names['complexes']] != 'null':
        reaction.complex_ids = fields[names['complexes']]
    reaction.type = fields[names['type']]
    reaction.direction = fields[names['direction']]
    reaction.gapfill_direction = fields[names['gfdir']]
    reaction.base_cost = float(fields[names['base_cost']])
    reaction.forward_cost = float(fields[names['forward_cost']])
    reaction.reverse_cost = float(fields[names['reverse_cost']])
    return reaction


class TemplateReaction(Reaction):
    """ A reaction is a chemical process that converts one set of compounds (substrate)
        to another set (products).

    Parameters
    ----------
    id : str, optional
        ID of reaction
    name : str, optional
        Name of reaction
        
    Attributes
    ----------
    compartments : list of str, optional
        List of compartment IDs where reaction can occur
    base_cost : float
        Cost to add reaction to a model by gap fill algorithm (encodes all penalties)
    forward_cost : float
        Cost to add reaction in forward direction to a model by gap fill algorithm
    reverse_cost : float
        Cost to add reaction in reverse direction to a model by gap fill algorithm
    universal_direction : {'=', '<', '>'}
        Universal direction (bi-directional, reverse, or forward)
    universal_reversibility : {'=', '<', '>', '?'}
        Universal reversibility (bi-directional, reverse, forward, or unknown)
    direction : {'=', '<', '>'}
        Default direction when added to a model by gene association (bi-directional, reverse, or forward)
    gapfill_direction : {'<', '>', '?'}
        Direction when directionality is reversed by gap fill algorithm (reverse, forward, unknown)
    type : {'universal', 'spontaneous', 'conditional', 'gapfilling'}
        Type used when adding reaction to a model
    complex_ids : list of str
        List of IDs for complexes that catalyze the reaction
    """

    def __init__(self, id=None, name=''):
        Reaction.__init__(self, id, name)

        self._compartments = list()
        self.base_cost = 0.0
        self.forward_cost = 0.0
        self.reverse_cost = 0.0
        self.universal_direction = None
        self.universal_reversibility = None
        self.direction = None
        self.gapfill_direction = None
        self._type = None
        self._complex_ids = list()

    @property
    def type(self):
        return self._type

    @type.setter
    def type(self, new_type):
        if new_type not in reaction_types:
            raise ValueError('Reaction type {0} is not valid', new_type)
        if new_type == 'conditional' and len(self.complex_ids) == 0:
            raise ValueError('Conditional reaction {0} must have at least one complex'
                             .format(self.id))
        if new_type == 'gapfilling' and len(self.complex_ids) > 0:
            raise ValueError('Gapfilling reaction {0} must have no complexes'
                             .format(self.id))
        self._type = new_type

    @property
    def complex_ids(self):
        return self._complex_ids

    @complex_ids.setter
    def complex_ids(self, new_ids):
        # @todo Be clever and distinguish between list and string
        if new_ids != 'null':
            self._complex_ids = new_ids.split('|')

    @property
    def compartments(self):
        return self._compartments

    @compartments.setter
    def compartments(self, new_compartments):
        # @todo Be clever and distinguish between list and string
        if new_compartments != 'null':
            self._compartments = new_compartments.split('|')
