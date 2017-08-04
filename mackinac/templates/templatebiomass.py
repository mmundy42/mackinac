from six import string_types

from cobra.core import Object, DictList, Reaction

from .util import change_compartment

# Required fields in source file for creating a TemplateBiomassComponent object.
biomass_component_fields = {
    'biomass_id', 'id', 'coefficient', 'coefficient_type', 'class', 'linked_compounds', 'compartment'
}

# Required fields in source file for creating a TemplateBiomass object.
biomass_fields = {
    'id', 'name', 'type', 'other', 'dna', 'rna', 'protein', 'lipid', 'cellwall', 'cofactor', 'energy'
}

# Valid values for biomass component class types where dna, rna, protein, and cellwall
# mean the metabolite is required for production of the type, lipid means the metabolite
# is an essential lipid that must be synthesized or imported by the cell for viability,
# cofactor means the metabolite is an essential cofactor that must be continuously
# replenished to support growth and viability, energy means the metabolite is included
# to account for energy required by the cell to grow and divide, and other is magic.
biomass_class_types = {
    'dna', 'rna', 'protein', 'cellwall', 'lipid', 'cofactor', 'energy', 'other'
}

# Valid values for biomass component coefficient types. The coefficient type controls how the
# biomass component contributes to the overall biomass reaction.
biomass_coefficient_types = {
    'MOLFRACTION', 'MOLSPLIT', 'MASSFRACTION', 'MASSSPLIT', 'GC', 'AT', 'EXACT', 'MULTIPLIER'
}


def create_template_biomass_component(fields, names):
    """ Create a TemplateBiomassComponent object from a list of fields.

    Parameters
    ----------
    fields : list of str
        Each element is a field from a text file defining a biomass component
    names : dict
        Dictionary with field name as key and list index number as value

    Returns
    -------
    TemplateBiomassComponent
        Object created from input fields
    """

    component = TemplateBiomassComponent(
        universal_id=fields[names['id']],
        class_type=fields[names['class']],
        biomass_id=fields[names['biomass_id']])
    component.compartment_id = fields[names['compartment']]
    component.coefficient = float(fields[names['coefficient']])
    component.coefficient_type = fields[names['coefficient_type']]
    component.linked_metabolites = fields[names['linked_compounds']]
    return component


class TemplateBiomassComponent(Object):
    """ A biomass component is a metabolite that is a part of a biomass entity.

    Parameters
    ----------
    universal_id : str
        ID of biomass metabolite in universal metabolites
    biomass_id : str
        ID of biomass entity component is a part of 
    class_type : str
        Class of metabolite (valid values in biomass_class_types)
        
    Attributes
    ----------
    compartment_id : str
        ID of compartment for biomass metabolite when added to model
    coefficient : float
        Coefficient value where a negative number indicates a reactant and a positive value indicates a product
    _coefficient_type : str
        Type of coefficient (valid values in biomass_coefficient_types)
    _linked_metabolites : dict
        Dictionary with metabolite ID as key and coefficient as value for linked metabolites
    """

    def __init__(self, universal_id, biomass_id, class_type):
        # Generate a unique ID from the metabolite ID, biomass ID, and class of metabolite so
        # all components can be stored in one DictList in a TemplateBiomass object.
        self._class_type = None
        self.class_type = class_type
        Object.__init__(self, '{0}_{1}_{2}'.format(universal_id, biomass_id, class_type))
        self.universal_id = universal_id
        self.biomass_id = biomass_id
        self._class_type = class_type

        self.compartment_id = 'c'  # @todo This has the side effect of adding metabolites in c compartment to template
        self.coefficient = 1.0
        self._coefficient_type = None
        self._linked_metabolites = dict()
        return

    @property
    def class_type(self):
        return self._class_type

    @class_type.setter
    def class_type(self, new_type):
        if new_type not in biomass_class_types:
            raise ValueError('Component {0} in biomass {1} has class type {2} that is not valid'
                             .format(self.id, self.biomass_id, new_type))
        self._class_type = new_type

    @property
    def coefficient_type(self):
        return self._coefficient_type

    @coefficient_type.setter
    def coefficient_type(self, new_type):
        if new_type not in biomass_coefficient_types:
            raise ValueError('Component {0} in biomass {1} has coefficient type {2} that is not valid'
                             .format(self.id, self.biomass_id, new_type))
        self._coefficient_type = new_type

    @property
    def linked_metabolites(self):
        return self._linked_metabolites

    @linked_metabolites.setter
    def linked_metabolites(self, new_metabolites):
        if isinstance(new_metabolites, string_types):
            if new_metabolites != 'null':
                metabolites = new_metabolites.split('|')
                if len(metabolites) < 1:
                    raise ValueError('Biomass component {0} has invalid linked metabolite field'
                                     .format(self.id))
                for index in range(len(metabolites)):
                    # A linked metabolite is specified with a universal ID and coefficient.
                    parts = metabolites[index].split(':')
                    if len(parts) != 2:
                        raise ValueError('Biomass component {0} has invalid linked compound field'
                                         .format(self.id))
                    self._linked_metabolites[parts[0]] = float(parts[1])
        elif isinstance(new_metabolites, dict):
            self._linked_metabolites = new_metabolites
        else:
            raise TypeError('Linked metabolites for a biomass component must be a string or a dict')


def create_template_biomass(fields, names):
    """ Create a TemplateBiomass object from a list of fields.

    Parameters
    ----------
    fields : list of str
        Each element is a field from a text file defining a biomass
    names : dict
        Dictionary with field name as key and list index number as value

    Returns
    -------
    TemplateBiomass
        Object created from input fields
    """

    return TemplateBiomass(
        id=fields[names['id']],
        name=fields[names['name']],
        type=fields[names['type']],
        cellwall=float(fields[names['cellwall']]),
        dna=float(fields[names['dna']]),
        rna=float(fields[names['rna']]),
        lipid=float(fields[names['lipid']]),
        protein=float(fields[names['protein']]),
        other=float(fields[names['other']]),
        energy=float(fields[names['energy']]),
        cofactor=float(fields[names['cofactor']]))


class TemplateBiomass(Object):
    """ A biomass entity is a collection of metabolites in a specific ratio and in specific
        compartments that are necessary for a cell to function properly. The prediction
        of biomass is key to the functioning of a metabolic model.

    Parameters
    ----------
    id : str, optional
        ID of biomass
    name : str, optional
        Name of biomass
    type : str, optional
        Type of biomass (usually 'growth')
    cellwall : float, optional
        Amount of cellwall in moles
    dna : float, optional
        Amount of dna in moles
    rna : float, optional
        Amount of rna in moles
    lipid : float, optional
        Amount of lipid in moles
    protein : float, optional
        Amount of protein in moles
    other : float, optional
        Amount of other components in moles
    energy : float, optional
        Amount of energy in moles
    cofactor : float, optional
        Amount of cofactors in moles
        
    Attributes
    ----------
    components : cobra.core.DictList
        List of TemplateBiomassComponent objects
    _metabolites : cobra.core.DictList
        List of cobra.core.Metabolite objects for metabolites used in biomass components
    """

    def __init__(self, id=None, name=None, type='', cellwall=0.0, dna=0.0, rna=0.0, lipid=0.0,
                 protein=0.0, other=0.0, energy=0.0, cofactor=0.0):
        Object.__init__(self, id, name)
        self.type = type
        self.cellwall = cellwall
        self.dna = dna
        self.rna = rna
        self.lipid = lipid
        self.protein = protein
        self.other = other
        self.energy = energy
        self.cofactor = cofactor

        self.components = DictList()
        self._metabolites = dict()
        return

    def get_metabolites(self):
        """ Get the cobra.core.Metabolite objects for metabolites used in components.
        
        Returns
        -------
        list
            List of cobra.core.Metabolite objects
        """
        return self._metabolites.values()

    def add_components(self, more_components, universal_metabolites):
        """ Add biomass components to the biomass entity.
        
        Parameters
        ----------
        more_components : iterable
            TemplateBiomassComponent objects to add
        universal_metabolites : cobra.core.DictList
            List of cobra.core.Metabolite objects available for template model
        """

        # Metabolites used in a component must be available in the universal metabolites
        # and depending on the coefficient type must have a non-zero mass.
        for component in more_components:
            if component.universal_id not in self._metabolites:
                # Find the universal metabolite and make a copy.
                try:
                    metabolite = universal_metabolites.get_by_id(component.universal_id).copy()
                except KeyError:
                    raise ValueError('Biomass "{0}" uses metabolite {1} which is not available'
                                     .format(self.id, component.universal_id))
                # Make sure a metabolite with a mass coefficient type refers to a
                # metabolite with non-zero mass.
                if component.coefficient_type == 'MASSFRACTION' and metabolite.notes['mass'] == 0.0:
                    raise ValueError('Metabolite {0} ({1}) in biomass "{2}" has coefficient type'
                                     'MASSFRACTION and a mass of zero'
                                     .format(metabolite.id, metabolite.name, self.id))
                if component.coefficient_type == 'MASSSPLIT' and metabolite.notes['mass'] == 0.0:
                    raise ValueError('Metabolite {0} ({1}) in biomass "{2}" has coefficient type'
                                     'MASSSPLIT and a mass of zero'
                                     .format(metabolite.id, metabolite.name, self.id))
                change_compartment(metabolite, component.compartment_id)
                self._metabolites[component.universal_id] = metabolite

            if len(component.linked_metabolites) > 0:
                for universal_id in component.linked_metabolites:
                    if universal_id not in self._metabolites:
                        # Make a copy of the universal metabolite and put it in the specified compartment.
                        try:
                            metabolite = universal_metabolites.get_by_id(universal_id).copy()
                        except:
                            raise ValueError('Biomass "{0}" uses metabolite {1} which is not available'
                                             .format(self.id, universal_id))
                        change_compartment(metabolite, component.compartment_id)
                        self._metabolites[universal_id] = metabolite

        # Add the additional components to the list.
        self.components.extend(more_components)
        return

    def create_objective(self, gc_content):
        """ Create a reaction that is used as the objective function for a model.

        Some biomass components refer to metabolites that have a mass of zero. For 
        example, DNA replication (cpd13783) has a mass of 0.0.

        Parameters
        ----------
        gc_content : float
            Percent GC content in genome of organism in range from 0.0 to 1.0

        Returns
        -------
        cobra.core.Reaction
            Biomass reaction for organism
        """

        # Each one of these dictionaries is initialized with keys for all of the valid class types.
        mole_fraction = dict()  # Accumulate mole fractions by class type
        molecular_weight = dict()  # Accumulate molecular weight by class type
        mass_fraction = dict()  # Accumulate mass fractions by class type
        mole_split_count = dict()  # Accumulate number of mole splits by class type
        mole_split_weight = dict()  # Accumulate molecular weight of mole splits by class type
        mass_split_count = dict()  # Accumulate number of mass splits by class type
        mass_split_moles = dict()  # Accumulate moles of mass splits by class type
        moles = dict()  # Accumulate moles by class type
        for type in biomass_class_types:
            mole_fraction[type] = float(0)
            molecular_weight[type] = float(0)
            mass_fraction[type] = float(0)
            mole_split_count[type] = float(0)
            mole_split_weight[type] = float(0)
            mass_split_count[type] = float(0)
            mass_split_moles[type] = float(0)
            moles[type] = float(0)

        # Keep track of class types of biomass components included in this biomass entity.
        included_class_types = dict()

        # Identify included class types and add up components and mass in each class type.
        for component in self.components:
            # Use the mass as specified in the ModelSEED source files to be consistent
            # with ModelSEED server. Could consider switching to formula weight from
            # Metabolite object which appears to be more precise.
            mass = self._metabolites[component.universal_id].notes['mass']
            included_class_types[component.class_type] = 1

            if component.coefficient_type == 'MOLFRACTION':
                mole_fraction[component.class_type] += -1.0 * component.coefficient
                if mass > 0.0:
                    molecular_weight[component.class_type] += -1.0 * mass * component.coefficient

            elif component.coefficient_type == 'MASSFRACTION':
                mass_fraction[component.class_type] += -1.0 * component.coefficient

            elif component.coefficient_type == 'AT':
                mole_fraction[component.class_type] += (1.0 - gc_content) / 2.0
                if mass > 0.0:
                    molecular_weight[component.class_type] += mass * (1.0 - gc_content) / 2.0

            elif component.coefficient_type == 'GC':
                mole_fraction[component.class_type] += gc_content / 2.0
                if mass > 0.0:
                    molecular_weight[component.class_type] += mass * gc_content / 2.0

            elif component.coefficient_type == 'MOLSPLIT':
                mole_split_count[component.class_type] += 1
                if mass > 0.0:
                    mole_split_weight[component.class_type] += mass

            elif component.coefficient_type == 'MASSSPLIT':
                mass_split_count[component.class_type] += 1
                mass_split_moles[component.class_type] += getattr(self, component.class_type) / mass

        # Used later for calculating coefficients.
        mass_split_fraction = dict()
        mole_split_fraction = dict()

        # Calculate the moles of each included class type.
        for type in included_class_types:
            total_split = mole_split_count[type] + mass_split_count[type]
            mass = (1.0 - mass_fraction[type]) * getattr(self, type)
            if mass > 0.0:
                remaining_mole_fraction = 1.0 - mole_fraction[type]
                if total_split > 0:
                    mass_split_mole_fraction = remaining_mole_fraction * mass_split_count[type] / total_split
                    mole_split_mole_fraction = remaining_mole_fraction * mole_split_count[type] / total_split
                    molecular_weight[type] += (mole_split_mole_fraction
                                               * mole_split_weight[type]
                                               / mole_split_count[type])
                    if mass_split_count[type] > 0.0:
                        molecular_weight[type] += (mass_split_mole_fraction
                                                   * getattr(self, type)
                                                   / (mass_split_moles[type] / mass_split_count[type]))
                    mass_split_fraction[type] = mass_split_mole_fraction
                    mole_split_fraction[type] = mole_split_mole_fraction
                if molecular_weight[type] > 0.0:
                    moles[type] = mass / molecular_weight[type]
                else:
                    moles[type] = 1

        # Compute coefficients for each metabolite.
        metabolite_coefficients = dict()  # Key is metabolite ID, value is calculated coefficient
        for component in self.components:
            type = component.class_type
            if component.coefficient_type == 'MOLFRACTION':
                coefficient = component.coefficient * moles[type] * 1000.0

            elif component.coefficient_type == 'MASSFRACTION':
                mass = self._metabolites[component.universal_id].notes['mass']
                coefficient = component.coefficient * getattr(self, type) / mass * 1000.0

            elif component.coefficient_type == 'AT':
                coefficient = component.coefficient * moles[type] * (1.0 - gc_content) / 2.0 * 1000.0

            elif component.coefficient_type == 'GC':
                coefficient = component.coefficient * gc_content * moles[type] / 2.0 * 1000.0

            elif component.coefficient_type == 'MULTIPLIER':
                coefficient = component.coefficient * getattr(self, type)

            elif component.coefficient_type == 'EXACT':
                coefficient = component.coefficient

            elif component.coefficient_type == 'MOLSPLIT':
                coefficient = (component.coefficient
                               * moles[type]
                               * mole_split_fraction[type]
                               * 1000.0
                               / mole_split_count[type])

            elif component.coefficient_type == 'MASSSPLIT':
                mass = self._metabolites[component.universal_id].notes['mass']
                coefficient = (component.coefficient
                               * getattr(self, type)
                               * mass_split_fraction[type]
                               / mass_split_count[type]
                               / mass
                               * 1000.0)

            else:
                coefficient = float(0)

            # Add this coefficient to the total for the metabolite.
            try:
                metabolite_coefficients[component.universal_id] += coefficient
            except KeyError:
                metabolite_coefficients[component.universal_id] = coefficient

            # Add coefficients for linked metabolites to the total for the metabolite.
            for metabolite_id in component.linked_metabolites:
                link_coefficient = coefficient * component.linked_metabolites[metabolite_id]
                try:
                    metabolite_coefficients[metabolite_id] += link_coefficient
                except KeyError:
                    metabolite_coefficients[metabolite_id] = link_coefficient

        # Create a Reaction object for the generated biomass reaction.
        biomass_reaction = Reaction(self.id, name='{0} ({1})'.format(self.name, self.type))
        biomass_metabolites = dict()
        for metabolite_id in metabolite_coefficients:
            if metabolite_coefficients[metabolite_id] != float(0):
                metabolite = self._metabolites[metabolite_id]
                biomass_metabolites[metabolite] = metabolite_coefficients[metabolite_id]
        biomass_reaction.add_metabolites(biomass_metabolites)

        return biomass_reaction
