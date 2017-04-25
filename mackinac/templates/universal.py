from warnings import warn

from cobra.core import Metabolite, Reaction, Model

from .util import read_source_file


def create_universal_metabolite(fields, names):
    """ Create a metabolite for the universal model.

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

    # Create a Metabolite object. All metabolites are placed in the "0" compartment.
    # @todo This means the universal metabolite ID will need to be adjusted when
    # building a template model.
    metabolite = Metabolite(id=fields[names['id']]+'_0',
                            formula=fields[names['formula']],
                            name=fields[names['name']],
                            charge=float(fields[names['charge']]),
                            compartment='0')

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
    if fields[names['deltag']] != 'null':
        metabolite.notes['deltag'] = float(fields[names['deltag']])
    if fields[names['deltagerr']] != 'null':
        metabolite.notes['deltagerr'] = float(fields[names['deltagerr']])
    if fields[names['aliases']] != 'null':
        metabolite.notes['aliases'] = dict()
        alias_list = fields[names['aliases']].split(';')
        for alias in alias_list:
            parts = alias.split(':')
            metabolite.notes['aliases'][parts[0]] = parts[1]
    return metabolite


def create_universal_reaction(fields, names):
    """ Create a reaction for the universal model.

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

    # Create a Reaction object. Note that lower bound, upper bound, and metabolites
    # need to be set later when the universal metabolites are available using
    # the data stored in the "stoichiometry" note.
    reaction = Reaction(id=fields[names['id']], name=fields[names['name']])

    # Add extended information as notes.
    reaction.notes['abbreviation'] = fields[names['abbreviation']]
    reaction.notes['code'] = fields[names['code']]
    reaction.notes['stoichiometry'] = fields[names['stoichiometry']]
    reaction.notes['direction'] = fields[names['direction']]
    reaction.notes['reversibility'] = fields[names['reversibility']]
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
    if fields[names['is_transport']] == '1':
        reaction.notes['is_transport'] = True
    else:
        reaction.notes['is_transport'] = False

    return reaction


def create_universal_model_from_source(metabolites_filename, reactions_filename,
                                       validate=False, verbose=False):
    """ Create universal model from ModelSEED source files.

    In the ModelSEED reaction source file, each metabolite in the reaction stoichiometry 
    is expressed in this format:

        n:ID:m:i:"NAME"

    where "n" is the metabolite coefficient and a negative number indicates a reactant
    and a positive number indicates a product, "ID" is the metabolite ID, "m" is the
    compartment index number, "i" is the community index number, and "NAME" is the 
    metabolite name. Metabolites are separated by semicolon. Only the coefficient and
    ID are used when creating a Reaction object.

    Reactions marked as obsolete are not included.
    
    Parameters
    ----------
    metabolites_filename : str
        Path to metabolites file
    reactions_filename : str
        Path to reactions file
    validate : bool, optional
        When True, check for common problems
    verbose : bool, optional
        When True, show all warning messages

    Returns
    -------
    cobra.core.Model
         COBRA model created from source files
    """

    # Use a cobra.core.Model object as a container for universal reactions and
    # metabolites. A universal model does not have compartments. A universal
    # model has no objective since it is not meant to be solved.
    universal = Model('ms_universal', name='ModelSEED universal model')

    # Add metabolites and reactions to the model by processing the source files.
    # Note that metabolites are NOT set in the reactions as they are processed
    # because the metabolites are not available in the get_universal_reactions()
    # function.
    required = {'id', 'abbreviation', 'name', 'formula', 'mass', 'source',
                'structure', 'charge', 'is_core', 'is_obsolete', 'linked_compound',
                'is_cofactor', 'deltag', 'deltagerr', 'pka', 'pkb',
                'abstract_compound', 'comprised_of', 'aliases'}
    universal.add_metabolites(read_source_file(metabolites_filename, required, create_universal_metabolite))
    required = {'id', 'name', 'abbreviation', 'code', 'stoichiometry', 'direction',
                'reversibility', 'status', 'deltag', 'deltagerr', 'aliases',
                'linked_reaction', 'is_obsolete', 'is_transport'}
    universal.add_reactions(read_source_file(reactions_filename, required, create_universal_reaction))

    # Parse the reaction stoichiometry to set the metabolites, lower bound, and upper bound.
    for reaction in universal.reactions:
        # Set upper and lower bounds based directionality. Switch reverse
        # reactions to forward reactions.
        reverse = 1.0
        if reaction.notes['direction'] == '=':
            lower_bound = -1000.0
            upper_bound = 1000.0
        elif reaction.notes['direction'] == '>':
            lower_bound = 0.0
            upper_bound = 1000.0
        elif reaction.notes['direction'] == '<':
            lower_bound = 0.0
            upper_bound = 1000.0
            reverse = -1.0
        else:
            warn('Reaction direction {0} assumed to be reversible for reaction {1}'
                 .format(reaction.notes['direction'], reaction.id))
            lower_bound = -1000.0
            upper_bound = 1000.0
        reaction.bounds = (lower_bound, upper_bound)

        # Parse the "stoichiometry" note to set the metabolites. Add metabolites
        # that are in compartments other than the default compartment.
        metabolites = dict()
        metabolite_list = reaction.notes['stoichiometry'].split(';')
        for met in metabolite_list:
            fields = met.split(':')
            metabolite_id = '{0}_{1}'.format(fields[1], fields[2])
            if universal.metabolites.has_id(metabolite_id):
                model_metabolite = universal.metabolites.get_by_id(metabolite_id)
            else:
                model_metabolite = universal.metabolites.get_by_id(fields[1] + '_0').copy()
                model_metabolite.id = '{0}_{1}'.format(fields[1], fields[2])
                model_metabolite.compartment = fields[2]
                universal.add_metabolites([model_metabolite])
            metabolites[model_metabolite] = float(fields[0]) * reverse
        reaction.add_metabolites(metabolites)

    # If requested, run checks to validate the universal model.
    if validate:
        num_unbalanced = 0
        for reaction in universal.reactions:
            try:
                unbalanced = reaction.check_mass_balance()
            except ValueError as e:
                unbalanced = {'formula': e.message}
            if len(unbalanced) > 0:
                if verbose:
                    warn('Reaction {0} is unbalanced because {1}\n    {2}'
                         .format(reaction.id, unbalanced, reaction.build_reaction_string(use_metabolite_names=True)))
                num_unbalanced += 1
        if num_unbalanced > 0:
            warn('Model {0} has {1} unbalanced reactions'.format(universal.id, num_unbalanced))

    return universal
