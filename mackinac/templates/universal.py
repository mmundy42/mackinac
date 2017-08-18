from warnings import warn

from cobra.core import Metabolite, Reaction

# Required fields in source file for creating a universal metabolite.
universal_metabolite_fields = {
    'id', 'formula', 'name', 'charge', 'abbreviation', 'source', 'structure',
    'pka', 'pkb', 'mass', 'deltag', 'deltagerr', 'aliases', 'is_core',
    'is_cofactor', 'is_obsolete', 'linked_compound'
}

# Required fields in source file for creating a universal reaction.
universal_reaction_fields = {
    'id', 'name', 'abbreviation', 'code', 'stoichiometry', 'direction', 'reversibility', 'status',
    'deltag', 'deltagerr', 'aliases', 'linked_reaction', 'is_obsolete', 'is_transport'
}

# Default compartment ID for universal metabolites.
default_compartment_id = '0'


def create_universal_metabolite(fields, names):
    """ Create a cobra.core.Metabolite object from a list of fields for a universal metabolite.

    Parameters
    ----------
    fields : list of str
        Each element is a field from a text file defining a universal metabolite
    names : dict
        Dictionary with field name as key and list index number as value

    Returns
    -------
    cobra.core.Metabolite
        Object created from input fields
    """

    # If metabolite is marked as obsolete, skip it.
    if fields[names['is_obsolete']] == '1':
        return None

    # Create a Metabolite object. All metabolites are placed in the default compartment.
    metabolite = Metabolite(id=fields[names['id']] + '_0',
                            name=fields[names['name']],
                            charge=float(fields[names['charge']]),
                            compartment=default_compartment_id)
    if fields[names['formula']] != 'null':
        metabolite.formula = fields[names['formula']]

    # Add extended information as notes.
    metabolite.notes['abbreviation'] = fields[names['abbreviation']]
    metabolite.notes['source'] = fields[names['source']]
    metabolite.notes['structure'] = fields[names['structure']]
    if fields[names['pka']] != 'null' and fields[names['pka']] != '':
        metabolite.notes['pka'] = dict()
        pka_list = fields[names['pka']].split(';')
        for pka in pka_list:
            parts = pka.split(':')
            try:
                metabolite.notes['pka'][parts[0]] = float(parts[1])
            except IndexError:
                warn('Metabolite {0} has an invalid pka field: {1}'.format(metabolite.id, fields[names['pka']]))
    if fields[names['pkb']] != 'null' and fields[names['pkb']] != '':
        metabolite.notes['pkb'] = dict()
        pkb_list = fields[names['pkb']].split(';')
        for pkb in pkb_list:
            parts = pkb.split(':')
            try:
                metabolite.notes['pkb'][parts[0]] = float(parts[1])
            except IndexError:
                warn('Metabolite {0} has an invalid pkb field: {1}'.format(metabolite.id, fields[names['pkb']]))
    if fields[names['mass']] != 'null':
        metabolite.notes['mass'] = float(fields[names['mass']])
    if fields[names['deltag']] != 'null' and fields[names['deltag']] != '10000000':
        metabolite.notes['deltag'] = float(fields[names['deltag']])
    if fields[names['deltagerr']] != 'null' and fields[names['deltagerr']] != '10000000':
        metabolite.notes['deltagerr'] = float(fields[names['deltagerr']])
    if fields[names['aliases']] != 'null':
        metabolite.notes['aliases'] = dict()
        alias_list = fields[names['aliases']].split(';')
        for alias in alias_list:
            parts = alias.split(':')
            metabolite.notes['aliases'][parts[0]] = parts[1]
    if fields[names['linked_compound']] != 'null':
        metabolite.notes['linked_ids'] = fields[names['linked_compound']].split(';')
    else:
        metabolite.notes['linked_ids'] = None
    metabolite.notes['is_core'] = True if fields[names['is_core']] == '1' else False
    metabolite.notes['is_cofactor'] = True if fields[names['is_cofactor']] == '1' else False
    return metabolite


def create_universal_reaction(fields, names):
    """ Create a cobra.core.Reaction object from a list of fields for a universal reaction.

    Parameters
    ----------
    fields : list of str
        Each element is a field from a text file defining a universal reaction
    names : dict
        Dictionary with field name as key and list index number as value

    Returns
    -------
    cobra.core.Reaction
        Object created from input fields
    """

    # If reaction is marked as obsolete or there are no metabolites, skip it.
    if fields[names['is_obsolete']] == '1' or fields[names['status']] == 'EMPTY':
        return None

    # Create a cobra.core.Reaction object. Note that lower bound, upper bound, and
    # metabolites need to be set later using the data stored in the "stoichiometry"
    # note and the complete list of universal metabolites.
    reaction = Reaction(id=fields[names['id']], name=fields[names['name']])

    # Add extended information as notes.
    reaction.notes['universal_direction'] = fields[names['direction']]
    reaction.notes['universal_reversibility'] = fields[names['reversibility']]
    reaction.notes['abbreviation'] = fields[names['abbreviation']]
    reaction.notes['code'] = fields[names['code']]
    reaction.notes['stoichiometry'] = fields[names['stoichiometry']]
    reaction.notes['status'] = fields[names['status']]
    if fields[names['deltag']] != 'null':
        reaction.notes['deltag'] = float(fields[names['deltag']])
    if fields[names['deltagerr']] != 'null':
        reaction.notes['deltagerr'] = float(fields[names['deltagerr']])
    if fields[names['aliases']] != 'null':
        reaction.notes['aliases'] = dict()
        alias_list = fields[names['aliases']].split(';')
        for alias in alias_list:
            parts = alias.split(':')
            reaction.notes['aliases'][parts[0]] = parts[1]
    if fields[names['linked_reaction']] != 'null':
        reaction.notes['linked_ids'] = fields[names['linked_reaction']].split(';')
    else:
        reaction.notes['linked_ids'] = None
    reaction.notes['is_transport'] = True if fields[names['is_transport']] == '1' else False

    return reaction


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
