from warnings import warn

from cobra.core import Metabolite, Reaction, DictList
from ..logger import LOGGER

# Required fields in source file for creating a universal metabolite.
universal_metabolite_fields = {
    'abbreviation', 'aliases', 'charge', 'deltag', 'deltagerr', 'formula', 'id',
    'inchikey', 'is_cofactor', 'is_core', 'is_obsolete', 'linked_compound',
    'mass', 'name', 'pka', 'pkb', 'smiles', 'source'
}

# Schema for metabolite JSON file.
metabolite_json_schema = {
    "$schema": "http://json-schema.org/draft-04/schema#",
    "title": "Universal metabolites",
    "description": "JSON representation of universal metabolites from ModelSEED",
    "type": "object",
    "additionalProperties": {
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
            "inchikey": {"type": "string"},
            "is_cofactor": {"type": "integer"},
            "is_core": {"type": "integer"},
            "is_obsolete": {"type": "integer"},
            "linked_compound": {"type": "string"},
            "mass": {"type": "string"},
            "name": {"type": "string"},
            "pka": {"type": "string"},
            "pkb": {"type": "string"},
            "smiles": {"type": "string"},
            "source": {"type": "string"},
        },
        "required": list(universal_metabolite_fields),
        "additionalProperties": {"type": "string"}
    }
}

# Required fields in source file for creating a universal reaction.
universal_reaction_fields = {
    'abbreviation', 'aliases', 'code', 'direction', 'deltag', 'deltagerr', 'id',
    'is_obsolete', 'is_transport', 'linked_reaction', 'name', 'reversibility',
    'status', 'stoichiometry'
}

# Schema for reaction JSON file.
reaction_json_schema = {
    "$schema": "http://json-schema.org/draft-04/schema#",
    "title": "Universal metabolites",
    "description": "JSON representation of universal metabolites from ModelSEED",
    "type": "object",
    "additionalProperties": {
        "type": "object",
        "properties": {
            "abbreviation": {"type": "string"},
            "abstract_reaction": {"type": "string"},
            "aliases": {"type": "string"},
            "code": {"type": "string"},
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
        },
        "required": list(universal_reaction_fields),
        "additionalProperties": {"type": "string"}
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

    # Create a Metabolite object. All metabolites are placed in the default compartment.
    metabolite = Metabolite(id=attrs['id'],
                            name=attrs['name'],
                            charge=float(attrs['charge']),
                            compartment=default_compartment_id)
    metabolite.notes['universal_id'] = attrs['id']
    if attrs['formula'] != 'null':
        metabolite.formula = attrs['formula']

    # Add extended information as notes.
    metabolite.notes['is_obsolete'] = True if int(attrs['is_obsolete']) == 1 else False
    metabolite.notes['replaced_by'] = None
    metabolite.notes['abbreviation'] = attrs['abbreviation']
    metabolite.notes['source'] = attrs['source']
    metabolite.notes['inchikey'] = attrs['inchikey']
    metabolite.notes['smiles'] = attrs['smiles']
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


def _parse_stoichiometry(u_rxn, metabolites, resolved_mets):
    """ Parse reaction stoichiometry and find each specified metabolite in universal metabolites.

    Parameters
    ----------
    u_rxn : cobra.core.Reaction
        Universal reaction object
    metabolites : cobra.core.DictList
        List of cobra.core.Metabolite objects for universal metabolites
    resolved_mets : cobra.core.DictList
        List of cobra.core.Metabolite objects of universal metabolites with
        obsolete metabolites removed and placed in a generic compartment
    """

    # Just return when there are no metabolites.
    if len(u_rxn.notes['stoichiometry']) == 0:
        LOGGER.info('Reaction %s does not have any metabolites', u_rxn.id)
        return

    # Find each metabolite in the universal metabolites, taking into account
    # obsolete metabolites.
    reaction_metabolites = dict()
    definition_list = u_rxn.notes['stoichiometry'].split(';')
    for definition in definition_list:
        fields = definition.split(':')
        met_id = '{0}_{1}'.format(fields[1], fields[2])
        try:
            met = resolved_mets.get_by_id(met_id)
        except KeyError:
            # Get the universal metabolite.
            u_met = metabolites.get_by_id(fields[1])

            # If metabolite is obsolete, find the replacement metabolite.
            if u_met.notes['is_obsolete']:
                if u_met.notes['replaced_by'] is not None:
                    u_met = metabolites.get_by_id(u_met.notes['replaced_by'])
                else:
                    if u_met.notes['linked_ids']:
                        replaced_by = None
                        for linked_id in u_met.notes['linked_ids']:
                            try:
                                linked_met = metabolites.get_by_id(linked_id)
                                if not linked_met.notes['is_obsolete']:
                                    # There should be only one linked metabolite that is not obsolete.
                                    replaced_by = linked_met
                            except KeyError:
                                raise ValueError('Metabolite {0} is obsolete and linked metabolite {1} not found'
                                                 .format(u_met.id, linked_id))
                        if replaced_by is not None:
                            LOGGER.info('Obsolete metabolite %s replaced by %s', u_met.id, replaced_by.id)
                            u_met.notes['replaced_by'] = replaced_by.id
                            u_met = replaced_by
                        else:
                            raise ValueError('Metabolite {0} is obsolete and all replacements are obsolete'
                                             .format(u_met.id))
                    else:
                        raise ValueError('Metabolite {0} is obsolete and no replacement is specified'
                                         .format(u_met.id))

            # Put the metabolite in a generic compartment.
            met = u_met.copy()
            met.id = met_id
            met.compartment = fields[2]
            resolved_mets.append(met)

        # Add the metabolite to the set of metabolites for the reaction.
        reaction_metabolites[met] = float(fields[0])

    # Add all of the metabolites to the reaction.
    u_rxn.add_metabolites(reaction_metabolites)
    return


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
        List of cobra.core.Metabolite objects for universal metabolites
    validate : bool, optional
        When True, check for common problems
    verbose : bool, optional
        When True, show all warning messages

    Returns
    -------
    cobra.core.DictList
        List of resolved cobra.core.Reaction objects for universal reactions
    """

    # Parse the reaction stoichiometry to set the metabolites, lower bound, and upper bound.
    resolved_rxns = DictList()
    resolved_mets = DictList()
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

        # Parse the "stoichiometry" note to set the metabolites. See description
        # of stoichiometry format above.
        _parse_stoichiometry(rxn, metabolites, resolved_mets)

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
                        raise ValueError('Reaction {0} is obsolete and linked reaction {1} not found'
                                         .format(rxn.id, linked_id))
                if replaced_by is not None:
                    rxn.notes['replaced_by'] = replaced_by
                else:
                    raise ValueError('Reaction {0} is obsolete and all replacements are obsolete'
                                     .format(rxn.id))
            else:
                raise ValueError('Reaction {0} is obsolete but no replacement is specified'
                                 .format(rxn.id))

        # Add the reaction.
        resolved_rxns.add(rxn)

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

    return resolved_rxns
