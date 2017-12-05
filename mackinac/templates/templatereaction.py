from six import string_types, iteritems
from operator import attrgetter

from cobra.core import Reaction, Object

from .util import change_compartment, direction_to_bounds

# Required fields in source file for creating a TemplateReaction object.
reaction_fields = {
    'id', 'compartment', 'direction', 'gfdir', 'type', 'base_cost', 'forward_cost',
    'reverse_cost', 'complexes'
}

# Valid values for template reaction type field.
reaction_types = {'universal', 'spontaneous', 'conditional', 'gapfilling'}

# Valid values for template reaction direction field.
reaction_directions = {'=', '>', '<'}


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
    reaction.compartment_ids = fields[names['compartment']]
    reaction.complex_ids = fields[names['complexes']]
    reaction.type = fields[names['type']]
    reaction.direction = fields[names['direction']]
    reaction.gapfill_direction = fields[names['gfdir']]
    reaction.base_cost = float(fields[names['base_cost']])
    reaction.forward_cost = float(fields[names['forward_cost']])
    reaction.reverse_cost = float(fields[names['reverse_cost']])
    return reaction


class TemplateReaction(Object):
    """ A reaction is a chemical process that converts one set of compounds (substrate)
        to another set (products).

    Parameters
    ----------
    id : str
        ID of reaction
        
    Attributes
    ----------
    name : str
        Descriptive name of reaction
    base_cost : float
        Cost to add reaction to a model by gap fill algorithm (encodes all penalties)
    forward_cost : float
        Cost to add reaction in forward direction to a model by gap fill algorithm
    reverse_cost : float
        Cost to add reaction in reverse direction to a model by gap fill algorithm
    _type : {'universal', 'spontaneous', 'conditional', 'gapfilling'}
        Type used when adding reaction to a model
    _direction : {'=', '<', '>'}
        Default direction when added to a model by gene association (bi-directional, reverse, or forward)
    _gapfill_direction : {'<', '>', '?'}
        Direction when directionality is reversed by gap fill algorithm (reverse, forward, unknown)
    _complex_ids : list of str
        List of IDs for complexes that catalyze the reaction
    _compartment_ids : list of str
        List of compartment IDs where reaction can occur
    _metabolites : dict
        Metabolites and their stoichiometric coefficients for the reaction
    """

    def __init__(self, id):
        Object.__init__(self, id)

        self.name = ''
        self.base_cost = 0.0
        self.forward_cost = 0.0
        self.reverse_cost = 0.0
        self._type = 'gapfilling'
        self._direction = '='
        self._gapfill_direction = '='
        self._compartment_ids = list()
        self._complex_ids = list()
        self._metabolites = dict()

    @property
    def type(self):
        return self._type

    @type.setter
    def type(self, new_type):
        if new_type not in reaction_types:
            raise ValueError('Reaction type {0} is not valid for reaction {1}'.format(new_type, self.id))
        if new_type == 'conditional' and len(self.complex_ids) == 0:
            raise ValueError('Conditional reaction {0} must have at least one complex'
                             .format(self.id))
        if new_type == 'gapfilling' and len(self.complex_ids) > 0:
            raise ValueError('Gapfilling reaction {0} must have no complexes'
                             .format(self.id))
        self._type = new_type

    @property
    def direction(self):
        return self._direction

    @direction.setter
    def direction(self, new_direction):
        if new_direction not in reaction_directions:
            raise ValueError('Reaction direction {0} is not valid for reaction {1}'.format(new_direction, self.id))
        self._direction = new_direction

    @property
    def gapfill_direction(self):
        return self._gapfill_direction

    @gapfill_direction.setter
    def gapfill_direction(self, new_direction):
        if new_direction not in reaction_directions:
            raise ValueError('Reaction gapfill direction {0} is not valid for reaction {1}'
                             .format(new_direction, self.id))
        self._gapfill_direction = new_direction

    @property
    def complex_ids(self):
        return self._complex_ids

    @complex_ids.setter
    def complex_ids(self, new_ids):
        if isinstance(new_ids, string_types):
            if new_ids != 'null':
                self._complex_ids = new_ids.split('|')
        elif isinstance(new_ids, list):
            self._complex_ids = new_ids
        else:
            raise TypeError('Complex IDs for a reaction must be a string or a list')

    @property
    def compartment_ids(self):
        return self._compartment_ids

    @compartment_ids.setter
    def compartment_ids(self, new_ids):
        if isinstance(new_ids, string_types):
            if new_ids != 'null':
                self._compartment_ids = new_ids.split('|')
        elif isinstance(new_ids, list):
            self._compartment_ids = new_ids
        else:
            raise TypeError('Compartment IDs for a reaction must be a string or a list')

    @property
    def metabolites(self):
        return self._metabolites.copy()

    @metabolites.setter
    def metabolites(self, new_metabolites):
        self._metabolites = new_metabolites.copy()

    @property
    def reactants(self):
        """ Return a list of reactants for the reaction. """
        return [k for k, v in iteritems(self._metabolites) if v < 0]

    @property
    def products(self):
        """ Return a list of products for the reaction. """
        return [k for k, v in iteritems(self._metabolites) if v >= 0]

    @property
    def reaction_str(self):
        """ Return a human readable reaction string. """

        def format(number):
            return str(number).rstrip(".0") + " "

        reactant_bits = []
        product_bits = []
        for met in sorted(self._metabolites, key=attrgetter("id")):
            coefficient = self._metabolites[met]
            if coefficient >= 0:
                product_bits.append(format(coefficient) + met.id)
            else:
                reactant_bits.append(format(abs(coefficient)) + met.id)

        reaction_string = ' + '.join(reactant_bits)
        if self.gapfill_direction == '=':
            reaction_string += ' <=> '
        elif self.gapfill_direction == '<':
            reaction_string += ' <-- '
        elif self.gapfill_direction == '>':
            reaction_string += ' --> '
        reaction_string += ' + '.join(product_bits)
        return reaction_string

    @property
    def model_id(self):
        # Always use the first compartment ID (no idea why ...)
        return '{0}_{1}'.format(self.id, self._compartment_ids[0])

    def create_model_reaction(self, compartments):
        """ Create a cobra.core.Reaction object for an organism model.
        
        Parameters
        ----------
        compartments : cobra.core.DictList of TemplateCompartment objects
            Compartments in the organism model
            
        Returns
        -------
        cobra.core.Reaction
            Reaction object for an organism model
        """

        # Create a new cobra.core.Reaction object.
        # Note that bounds are set to gap fill direction to enable gap fill.
        bounds = direction_to_bounds(self.gapfill_direction)
        model_reaction = Reaction(id=self.model_id, name=self.name,
                                  lower_bound=bounds[0], upper_bound=bounds[1])

        # Create new cobra.core.Metabolite objects and place them in a specific compartment.
        model_metabolites = dict()
        for metabolite, coefficient in iteritems(self._metabolites):
            model_met = metabolite.copy()
            model_compartment = compartments.get_by_id(model_met.compartment)
            if model_compartment.model_id != self._compartment_ids[int(model_compartment.id)]:
                raise ValueError('Inconsistent order of compartment IDs in template reaction {0}'
                                 .format(self.id))
            change_compartment(model_met, model_compartment.model_id)
            model_metabolites[model_met] = coefficient
        model_reaction.add_metabolites(model_metabolites)

        # Add notes about the template reaction for reference.
        model_reaction.notes['template_id'] = self.id
        model_reaction.notes['direction'] = self.direction
        model_reaction.notes['gapfill_direction'] = self.gapfill_direction
        model_reaction.notes['base_cost'] = self.base_cost
        model_reaction.notes['forward_cost'] = self.forward_cost
        model_reaction.notes['reverse_cost'] = self.reverse_cost

        return model_reaction
