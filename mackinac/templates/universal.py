from warnings import warn

from cobra.core import Metabolite, Reaction

# Required fields in source file for creating a universal metabolite.
universal_metabolite_fields = {
    'id', 'formula', 'name', 'charge', 'abbreviation', 'source', 'structure',
    'pka', 'pkb', 'mass', 'deltag', 'deltagerr', 'aliases', 'is_core',
    'is_cofactor', 'is_obsolete', 'linked_compound'
}

# Schema for metabolite JSON file.
metabolite_json_schema = {
    "$schema": "http://json-schema.org/draft-04/schema#",
    "title": "Universal metabolites",
    "description": "JSON representation of universal metabolites from ModelSEED",
    "type": "object",
    "properties": {
        "id": {
            "type": "object",
            "properties": {
                "abbreviation": {"type": "string"},
                "abstract_compound": {"type": "string"},
                "aliases": {"type": "string"},
                "charge": {"type": "string"},
                "comprised_of": {"type": "string"},
                "deltag": {"type": "string"},
                "deltagerr": {"type": "string"},
                "formula": {"type": "string"},
                "id": {"type": "string"},
                "is_cofactor": {"type": "integer"},
                "is_core": {"type": "integer"},
                "is_obsolete": {"type": "integer"},
                "linked_compound": {"type": "string"},
                "mass": {"type": "string"},
                "name": {"type": "string"},
                "pka": {"type": "string"},
                "pkb": {"type": "string"},
                "source": {"type": "string"},
                "structure": {"type": "string"}
            }
        }
    }
}

# Required fields in source file for creating a universal reaction.
universal_reaction_fields = {
    'id', 'name', 'abbreviation', 'code', 'stoichiometry', 'direction', 'reversibility', 'status',
    'deltag', 'deltagerr', 'aliases', 'linked_reaction', 'is_obsolete', 'is_transport'
}

# Schema for reaction JSON file.
reaction_json_schema = {
    "$schema": "http://json-schema.org/draft-04/schema#",
    "title": "Universal metabolites",
    "description": "JSON representation of universal metabolites from ModelSEED",
    "type": "object",
    "properties": {
        "id": {
            "type": "object",
            "properties": {
                "abbreviation": {"type": "string"},
                "abstract_reaction": {"type": "string"},
                "aliases": {"type": "string"},
                "code": {"type": "string"},
                "comprised_of": {"type": "string"},
                "compound_ids": {"type": "string"},
                "definition": {"type": "string"},
                "deltag": {"type": "string"},
                "deltagerr": {"type": "string"},
                "direction": {"type": "string"},
                "ec_numbers": {"type": "string"},
                "equation": {"type": "string"},
                "id": {"type": "string"},
                "is_obsolete": {"type": "integer"},
                "is_transport": {"type": "integer"},
                "linked_reaction": {"type": "string"},
                "name": {"type": "string"},
                "notes": {"type": "string"},
                "pathways": {"type": "string"},
                "reversibility": {"type": "string"},
                "status": {"type": "string"},
                "stoichiometry": {"type": "string"}
            }
        }
    }
}

# Default compartment ID for universal metabolites.
default_compartment_id = '0'


def create_universal_metabolite(attrs):
    """ Create a cobra.core.Metabolite object from a dictionary of attributes for a universal metabolite.

    Parameters
    ----------
    attrs : dict
        Dictionary where key is attribute name and value is attribute value

    Returns
    -------
    cobra.core.Metabolite
        Object created from input attributes
    """

    # If metabolite is marked as obsolete, skip it.
    if int(attrs['is_obsolete']) == 1:
        return None

    # Create a Metabolite object. All metabolites are placed in the default compartment.
    metabolite = Metabolite(id=attrs['id'] + '_0',
                            name=attrs['name'],
                            charge=float(attrs['charge']),
                            compartment=default_compartment_id)
    if attrs['formula'] != 'null':
        metabolite.formula = attrs['formula']

    # Add extended information as notes.
    metabolite.notes['abbreviation'] = attrs['abbreviation']
    metabolite.notes['source'] = attrs['source']
    metabolite.notes['structure'] = attrs['structure']
    if attrs['pka'] != 'null' and attrs['pka'] != '':
        metabolite.notes['pka'] = dict()
        pka_list = attrs['pka'].split(';')
        for pka in pka_list:
            parts = pka.split(':')
            try:
                metabolite.notes['pka'][parts[0]] = float(parts[1])
            except IndexError:
                warn('Metabolite {0} has an invalid pka field: {1}'.format(metabolite.id, attrs['pka']))
    if attrs['pkb'] != 'null' and attrs['pkb'] != '':
        metabolite.notes['pkb'] = dict()
        pkb_list = attrs['pkb'].split(';')
        for pkb in pkb_list:
            parts = pkb.split(':')
            try:
                metabolite.notes['pkb'][parts[0]] = float(parts[1])
            except IndexError:
                warn('Metabolite {0} has an invalid pkb field: {1}'.format(metabolite.id, attrs['pkb']))
    if attrs['mass'] != 'null':
        metabolite.notes['mass'] = float(attrs['mass'])
    if attrs['deltag'] != 'null' and attrs['deltag'] != '10000000':
        metabolite.notes['deltag'] = float(attrs['deltag'])
    if attrs['deltagerr'] != 'null' and attrs['deltagerr'] != '10000000':
        metabolite.notes['deltagerr'] = float(attrs['deltagerr'])
    if attrs['aliases'] != 'null':
        metabolite.notes['aliases'] = dict()
        alias_list = attrs['aliases'].split(';')
        for alias in alias_list:
            parts = alias.split(':')
            metabolite.notes['aliases'][parts[0]] = parts[1]
    if attrs['linked_compound'] != 'null':
        metabolite.notes['linked_ids'] = attrs['linked_compound'].split(';')
    else:
        metabolite.notes['linked_ids'] = None
    metabolite.notes['is_core'] = True if int(attrs['is_core']) == 1 else False
    metabolite.notes['is_cofactor'] = True if int(attrs['is_cofactor']) == 1 else False
    return metabolite


def create_universal_metabolite_from_fields(fields, field_names):
    """ Create a cobra.core.Metabolite object from a list of fields for a universal metabolite.

    Parameters
    ----------
    fields : list of str
        Each element is a field from a text file defining a universal metabolite
    field_names : dict
        Dictionary with field name as key and list index number as value

    Returns
    -------
    cobra.core.Metabolite
        Object created from input fields
    """

    metabolite_dict = dict()
    for name in field_names:
        metabolite_dict[name] = fields[field_names[name]]
    return create_universal_metabolite(metabolite_dict)


def create_universal_reaction(attrs):
    """ Create a cobra.core.Reaction object from a list of fields for a universal reaction.

    Parameters
    ----------
    attrs : dict
        Dictionary where key is attribute name and value is attribute value

    Returns
    -------
    cobra.core.Reaction
        Object created from input attributes
    """

    # If reaction has no metabolites, skip it.
    if attrs['status'] == 'EMPTY':
        return None

    # Create a cobra.core.Reaction object. Note that lower bound, upper bound, and
    # metabolites need to be set later using the data stored in the "stoichiometry"
    # note and the complete list of universal metabolites.
    reaction = Reaction(id=attrs['id'], name=attrs['name'])

    # Add extended information as notes.
    reaction.notes['is_obsolete'] = True if int(attrs['is_obsolete']) == 1 else False
    reaction.notes['universal_direction'] = attrs['direction']
    reaction.notes['universal_reversibility'] = attrs['reversibility']
    reaction.notes['abbreviation'] = attrs['abbreviation']
    reaction.notes['code'] = attrs['code']
    reaction.notes['stoichiometry'] = attrs['stoichiometry']
    reaction.notes['status'] = attrs['status']
    if attrs['deltag'] != 'null':
        reaction.notes['deltag'] = float(attrs['deltag'])
    if attrs['deltagerr'] != 'null':
        reaction.notes['deltagerr'] = float(attrs['deltagerr'])
    if attrs['aliases'] != 'null':
        reaction.notes['aliases'] = dict()
        alias_list = attrs['aliases'].split(';')
        for alias in alias_list:
            parts = alias.split(':')
            reaction.notes['aliases'][parts[0]] = parts[1]
    if attrs['linked_reaction'] != 'null':
        reaction.notes['linked_ids'] = attrs['linked_reaction'].split(';')
    else:
        reaction.notes['linked_ids'] = None
    reaction.notes['is_transport'] = True if int(attrs['is_transport']) == 1 else False

    return reaction


def create_universal_reaction_from_fields(fields, field_names):
    """ Create a cobra.core.Reaction object from a list of fields for a universal reaction.

    Parameters
    ----------
    fields : list of str
        Each element is a field from a text file defining a universal reaction
    field_names : dict
        Dictionary with field name as key and list index number as value

    Returns
    -------
    cobra.core.Reaction
        Object created from input fields
    """

    reaction_dict = dict()
    for name in field_names:
        reaction_dict[name] = fields[field_names[name]]
    return create_universal_reaction(reaction_dict)


def resolve_universal_reactions(reactions, metabolites, validate=False, verbose=False):
    """ Resolve metabolites for universal reactions.

    In the ModelSEED universal reaction source file, each metabolite in the reaction 
    stoichiometry is expressed in this format:

        n:ID:m:i:"NAME"

    where "n" is the metabolite coefficient and a negative number indicates a reactant
    and a positive number indicates a product, "ID" is the metabolite ID, "m" is the
    compartment index number, "i" is the community index number, and "NAME" is the 
    metabolite name. Metabolites are separated by semicolon. The coefficient, ID, and
    compartment index number are used to resolve the metabolites.

    Metabolites for additional compartments may be added to the list metabolites.
    
    Parameters
    ----------
    reactions : cobra.core.DictList
        List of TemplateReaction objects for universal reactions
    metabolites : cobra.core.DictList
        List of cobra.core.Metabolite objects
    validate : bool, optional
        When True, check for common problems
    verbose : bool, optional
        When True, show all warning messages

    """

    # Parse the reaction stoichiometry to set the metabolites, lower bound, and upper bound.
    for rxn in reactions:
        # Set upper and lower bounds based on directionality.
        if rxn.notes['universal_direction'] == '=':
            lower_bound = -1000.0
            upper_bound = 1000.0
        elif rxn.notes['universal_direction'] == '>':
            lower_bound = 0.0
            upper_bound = 1000.0
        elif rxn.notes['universal_direction'] == '<':
            lower_bound = -1000.0
            upper_bound = 0.0
        else:
            warn('Reaction direction {0} assumed to be reversible for reaction {1}'
                 .format(rxn.notes['universal_direction'], rxn.id))
            lower_bound = -1000.0
            upper_bound = 1000.0
        rxn.bounds = (lower_bound, upper_bound)

        # Parse the "stoichiometry" note to set the metabolites. Add metabolites
        # that are in compartments other than the default compartment. See description
        # of stoichiometry format above.
        reaction_metabolites = dict()
        metabolite_list = rxn.notes['stoichiometry'].split(';')
        for met in metabolite_list:
            fields = met.split(':')
            metabolite_id = '{0}_{1}'.format(fields[1], fields[2])
            try:
                model_metabolite = metabolites.get_by_id(metabolite_id)
            except KeyError:
                model_metabolite = metabolites.get_by_id(fields[1] + '_0').copy()
                model_metabolite.id = '{0}_{1}'.format(fields[1], fields[2])
                model_metabolite.compartment = fields[2]
                metabolites.append(model_metabolite)
            reaction_metabolites[model_metabolite] = float(fields[0])
        rxn.add_metabolites(reaction_metabolites)

        # Find the reaction that an obsolete reaction was replaced by.
        if rxn.notes['is_obsolete']:
            if rxn.notes['linked_ids']:
                replaced_by = None
                for linked_id in rxn.notes['linked_ids']:
                    try:
                        linked_rxn = reactions.get_by_id(linked_id)
                        if not linked_rxn.notes['is_obsolete']:
                            replaced_by = linked_rxn.id
                    except KeyError:
                        warn('Reaction {0} is obsolete and linked reaction {1} not found'.format(rxn.id, linked_id))
                if replaced_by is not None:
                    rxn.notes['replaced_by'] = replaced_by
                else:
                    warn('Reaction {0} is obsolete and all replacements are obsolete'.format(rxn.id))
            else:
                warn('Reaction {0} is obsolete but no replacement is specified'.format(rxn.id))

    # If requested, run checks to validate the reactions.
    if validate:
        num_unbalanced = 0
        for rxn in reactions:
            try:
                unbalanced = rxn.check_mass_balance()
            except ValueError as e:
                unbalanced = {'formula': e.message}
            if len(unbalanced) > 0:
                if verbose:
                    warn('Reaction {0} is unbalanced because {1}\n    {2}'
                         .format(rxn.id, unbalanced, rxn.build_reaction_string(use_metabolite_names=True)))
                num_unbalanced += 1
        if num_unbalanced > 0:
            warn('Found {0} unbalanced universal reactions'.format(num_unbalanced))

    return
