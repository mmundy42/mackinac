from six import string_types

from cobra.core import Reaction

from .util import change_compartment

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
    _compartment_ids : list of str
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
    _type : {'universal', 'spontaneous', 'conditional', 'gapfilling'}
        Type used when adding reaction to a model
    _complex_ids : list of str
        List of IDs for complexes that catalyze the reaction
    """

    def __init__(self, id=None, name=''):
        Reaction.__init__(self, id, name)

        self._compartment_ids = list()
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

    def make_model_id(self):
        return '{0}_{1}'.format(self.id, self.compartment_ids[0])

    def create_model_reaction(self, compartments, genes):
        """ Create a cobra.core.Reaction object for an organism model.
        
        Parameters
        ----------
        genes : list of str
            List of gene IDs for reaction
        """

        # Create the Reaction object and add all of the metabolites.
        # Tack the first compartment ID on the end of the reaction ID
        reaction = Reaction(id=self.make_model_id(),
                            name=self.name,
                            lower_bound=self.lower_bound,
                            upper_bound=self.upper_bound)
        # Need to put metabolites in compartments
        model_metabolites = dict()
        for met in self.metabolites:
            mm = met.copy()
            mc = compartments.get_by_id(mm.compartment)
            if mc.model_id != self._compartment_ids[int(mc.id)]:
                raise ValueError('Inconsistent compartment IDs')

            change_compartment(mm, mc.model_id) # need to index here
            model_metabolites[mm] = self.metabolites[met]
        reaction.add_metabolites(model_metabolites)

        # If features are associated with the reaction, add the GPR.
        if genes is not None:
            reaction.gene_reaction_rule = '('+' or '.join([f.id for f in genes])+')'

        return reaction
