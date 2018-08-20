from warnings import warn
from collections import defaultdict
from six import iteritems
from tempfile import NamedTemporaryFile
import re

from cobra.core import Object, DictList, Model, Gene
from cobra.io import save_json_model
try:
    from psamm.importers.cobrajson import Importer
except ImportError:
    Importer = None

from .util import read_source_file, create_boundary
from .templatecompartment import create_template_compartment, compartment_fields
from .templatebiomass import create_template_biomass_component, biomass_component_fields
from .templatebiomass import create_template_biomass, biomass_fields
from .templaterole import create_template_role, role_fields
from .templatecomplex import create_template_complex, complex_fields
from .templatereaction import create_template_reaction, reaction_fields
from .feature import create_features_from_patric
from ..logger import LOGGER


class TemplateError(Exception):
    """ Exception raised when there is an error with a template model """
    pass


class TemplateModel(Object):
    """ A template model is the source for automated reconstruction of an organism model. 
    
    Parameters
    ----------
    id : str
        ID of template model
    name : str
        Descriptive name of template model
    type : str, optional
        Type of template model (usually 'growth')
    domain : str, optional
        Domain of organisms reconstructed from template model
        
    Attributes
    ----------
    roles : cobra.core.DictList
        List of TemplateRole objects
    complexes : cobra.core.DictList
        List of TemplateComplex objects
    compartments : cobra.core.DictList
        List of TemplateCompartment objects
    reactions : cobra.core.DictList
        List of TemplateReaction objects
    metabolites : cobra.core.DictList
        List of cobra.core.Metabolite objects
    biomasses : cobra.core.DictList
        List of TemplateBiomass objects
    ec_number_index : dict
        Dictionary with EC number as key and list of roles for EC number as value
    role_name_index : dict
        Dictionary with search name of role as key and list of TemplateRole objects as value
    _complexes_to_roles : dict
        Dictionary with complex ID as key and list of role IDs as value
    _reactions_to_complexes : dict
        Dictionary with reaction ID as key and list of complex IDs as value
    """

    def __init__(self, id, name, type='growth', domain='bacteria'):
        Object.__init__(self, id, name)
        self.type = type
        self.domain = domain.lower()

        self.roles = DictList()
        self.complexes = DictList()
        self.compartments = DictList()
        self.reactions = DictList()
        self.metabolites = DictList()
        self.biomasses = DictList()
        self.ec_number_index = defaultdict(list)
        self.role_name_index = defaultdict(list)
        self._complexes_to_roles = dict()
        self._reactions_to_complexes = dict()

    def init_from_files(self, compartment_filename, biomass_filename, component_filename,
                        reaction_filename, complex_filename, role_filename, universal_metabolites,
                        universal_reactions, exclude=None, verbose=False):
        """ Initialize object from source files.

        The source files are tab-delimited files with a header line that defines
        the fields. Each line contains the attributes for initializing an object.
        The format of the source files comes from ModelSEED.
        
        Parameters
        ----------
        compartment_filename : str
            Path to source file that defines template compartments
        biomass_filename : str
            Path to source file that defines template biomass entities
        component_filename : str
            Path to source file that defines template biomass entity components
        reaction_filename : str
            Path to source file that defines template reactions
        complex_filename : str
            Path to source file that defines universal complexes
        role_filename : str
            Path to source file that defines universal roles
        universal_metabolites : cobra.core.DictList
            List of cobra.core.Metabolite objects for universal metabolites
        universal_reactions : cobra.core.DictList
            List of cobra.core.Reaction objects for universal reactions
        exclude : set of str, {"pseudo", "status"}, optional
            Types of reactions to exclude from template, where "pseudo" means to exclude
            reactions with no metabolites, "status" means to exclude reactions where
            reaction status is not OK
        verbose : bool
            When True, show all warning messages
        """

        LOGGER.info('Started initializing template model "%s" from source files', self.id)
        if exclude is None:
            exclude = set()

        # Get compartments from the compartment source file.
        self.compartments.extend(read_source_file(compartment_filename, compartment_fields,
                                                  create_template_compartment))
        LOGGER.info('Added %d compartments from source file "%s"',
                    len(self.compartments), compartment_filename)

        # Get biomasses from the biomass and biomass component source files. Resolve
        # biomass components to universal metabolites and add the metabolites to the
        # template model.
        components = read_source_file(component_filename, biomass_component_fields,
                                      create_template_biomass_component)
        biomasses = read_source_file(biomass_filename, biomass_fields, create_template_biomass)
        for biomass in biomasses:
            biomass.add_components(components.query(lambda x: x == biomass.id, 'biomass_id'),
                                   universal_metabolites)
            self.metabolites.union(biomass.get_metabolites())
            self.biomasses.append(biomass)
        LOGGER.info('Added %d biomasses from source files "%s" and "%s"',
                    len(self.biomasses), biomass_filename, component_filename)

        # Get complexes from the complex source file. Only complexes that are
        # referenced by reactions are added to the template model.
        all_complexes = read_source_file(complex_filename, complex_fields, create_template_complex)

        # Get reactions from the reaction source file. Get details about reaction from
        # corresponding universal reaction.
        skipped = 0
        bad_status = 0
        obsolete = 0
        pseudo = 0
        reactions = read_source_file(reaction_filename, reaction_fields, create_template_reaction)
        for rxn in reactions:
            # Get universal reaction for definition, metabolites, and status.
            try:
                u_rxn = universal_reactions.get_by_id(rxn.id)
                if u_rxn.notes['is_obsolete']:
                    u_rxn = universal_reactions.get_by_id(u_rxn.notes['replaced_by'])
                    obsolete += 1
                    LOGGER.info('Obsolete universal reaction %s replaced by %s', rxn.id, u_rxn.id)
            except KeyError:
                if verbose:
                    warn('Template reaction {0} was not found in universal reactions'.format(rxn.id))
                skipped += 1
                continue
            if 'OK' not in u_rxn.notes['status']:
                bad_status += 1
                if 'status' in exclude:
                    LOGGER.info('Skipped universal reaction %s because status %s is not OK',
                                u_rxn.id, u_rxn.notes['status'])
                    continue
                LOGGER.info('Universal reaction %s status %s is not OK', u_rxn.id, u_rxn.notes['status'])
            if len(u_rxn.metabolites) == 0:
                if 'pseudo' in exclude:
                    LOGGER.info('Skipped universal reaction %s because it has no metabolites', u_rxn.id)
                    pseudo += 1

            # Convert a reverse reaction to a forward reaction.
            reverse = 1.0
            if rxn.direction == '<':
                reverse = -1.0
                rxn.direction = '>'

            # Resolve to universal metabolites and copy any new metabolites to the
            # template model.
            metabolites = dict()
            for u_met, coefficient in iteritems(u_rxn.metabolites):
                try:
                    met = self.metabolites.get_by_id(u_met.id)
                except KeyError:
                    met = u_met.copy()
                    self.metabolites.append(met)
                metabolites[met] = coefficient * reverse
            rxn.metabolites = metabolites
            rxn.name = u_rxn.name
            self.reactions.append(rxn)

            # All conditional reactions must reference valid complexes. Only complexes
            # referenced by a reaction are added to the template model.
            if rxn.type == 'conditional':
                try:
                    complexes = [all_complexes.get_by_id(complex_id) for complex_id in rxn.complex_ids]
                except KeyError as e:
                    LOGGER.error('Complex {0} referenced by reaction {1} was not found'.format(e.args[0], rxn.id))
                    raise e
                self.complexes.union(complexes)
                for complx in complexes:
                    complx.reaction_ids.add(rxn.id)

        if verbose:
            if skipped > 0:
                warn('{0} template reactions were not found in universal reactions'.format(skipped))
            if bad_status > 0:
                warn('{0} template reactions reference a universal reaction with bad status'.format(bad_status))
            if obsolete > 0:
                warn('{0} template reactions reference a universal reaction that is obsolete'.format(obsolete))
            if pseudo > 0:
                warn('{0} template reactions reference a universal reaction that has no metabolites'.format(pseudo))
        LOGGER.info('Added %d reactions from source file "%s"', len(self.reactions), reaction_filename)
        LOGGER.info('Added %d metabolites from reactions', len(self.metabolites))
        for rxn in self.reactions.query(lambda x: len(x) > 0, 'complex_ids'):
            self.reactions_to_complexes[rxn.id] = rxn.complex_ids
        LOGGER.info('Added %d complexes from source file "%s"', len(self.complexes), complex_filename)

        # Get roles from the role source file. Only roles that are referenced by
        # complexes are added to the template model.
        all_roles = read_source_file(role_filename, role_fields, create_template_role)
        for complx in self.complexes:
            try:
                roles = [all_roles.get_by_id(role['role_id']) for role in complx.roles]
            except KeyError as e:
                LOGGER.error('Role {0} referenced by complex {1} is not available'.format(e.args[0], complx.id))
                raise e
            self.roles.union(roles)
            for role in roles:
                role.complex_ids.add(complx.id)
        for complx in self.complexes.query(lambda x: len(x) > 0, 'roles'):
            self.complexes_to_roles[complx.id] = [role['role_id'] for role in complx.roles]
        LOGGER.info('Added %d roles from source file "%s"', len(self.roles), role_filename)

        # Build an index to lookup roles by EC number.
        self._build_role_ec_index()
        LOGGER.info('Finished initializing template model "%s" from source files', self.id)

        return

    @property
    def complexes_to_roles(self):
        return self._complexes_to_roles

    @property
    def reactions_to_complexes(self):
        return self._reactions_to_complexes

    def _build_role_ec_index(self):
        """ Build an index for finding roles by Enzyme Commission number. """

        # Find all of the roles that have at least one EC number.
        ec_roles = self.roles.query(lambda x: len(x) > 0, 'ec_numbers')

        # Build an index that maps a EC number to one or more TemplateRole objects.
        for role in ec_roles:
            for ec_num in role.ec_numbers:
                self.ec_number_index[ec_num].append(role)

        return

    def _build_role_name_index(self):
        """ Build an index for finding roles by search name. """

        # Build an index that maps a search name to one or more TemplateRole objects.
        for role in self.roles:
            self.role_name_index[role.search_name[0]].append(role)
        return

    def reconstruct(self, model_id, genome_features, biomass_id, model_name=None,
                    gc_content=0.5, annotation='PATRIC'):
        """ Reconstruct a draft model from the genome of an organism.

        The reconstruction algorithm is essentially a string matching algorithm.
        When the function of a genome feature matches the name of a role in the
        template, then all reactions linked to the role are added to the draft
        model. This means that the source for the names of the template roles and
        the type of annotation must be consistent.

        For example, with template models created from ModelSEED source files,
        only a PATRIC annotation works to reconstruct a draft model. Use the
        get_genome_summary() and get_genome_features() functions to retrieve the
        information needed for the input parameters.

        Parameters
        ----------
        model_id : str
            ID for draft model of organism
        genome_features : list of dict
            List of feature data for organism. The key names in the dictionary
            can be different based on the type of annotation but an ID and function
            are required for the reconstruction algorithm to work.
        biomass_id : str
            ID of biomass entity used to create biomass objective
        model_name : str, optional
            Name for draft model of organism
        gc_content : float, optional
            Percent GC content in genome of organism (value between 0 and 1)
        annotation : {'PATRIC'}, optional
            Type of annotation in feature data
            
        Returns
        -------
        cobra.core.Model
            Draft model of organism based on genome features
        """

        if gc_content < 0. or gc_content > 1.:
            raise ValueError('Percent GC content value must be between 0 and 1')

        # Create Feature objects from the list of features in the genome annotation.
        if annotation == 'PATRIC':
            feature_list, genome_stats = create_features_from_patric(genome_features)
        else:
            raise ValueError('Annotation type {0} is not supported'.format(annotation))
        if len(feature_list) == 0:
            raise ValueError('No valid features found in genome features')

        # Create a new cobra.core.Model object.
        model = Model(model_id, name=model_name)
        model_stats = defaultdict(int)

        # Start by adding universal and spontaneous template reactions.
        universal_reactions = self.reactions.query(lambda x: x == 'universal', 'type')
        model.add_reactions([r.create_model_reaction(self.compartments) for r in universal_reactions])
        LOGGER.info('Added %d universal reactions to model', len(universal_reactions))
        spontaneous_reactions = self.reactions.query(lambda x: x == 'spontaneous', 'type')
        model.add_reactions([r.create_model_reaction(self.compartments) for r in spontaneous_reactions])
        LOGGER.info('Added %d spontaneous reactions to model', len(spontaneous_reactions))

        # The matched_roles dictionary is keyed by TemplateRole object and contains
        # roles that match a role from a feature in the organism's genome. The value
        # is another dictionary keyed by compartment ID where the value is a list of
        # matching Feature objects. When there is a match, the genome feature is assumed
        # to be active in all of the compartments associated with the feature. Most of
        # the time the compartment is unknown which means the feature is not localized
        # to a specific compartment in the cell.
        matched_roles = defaultdict(lambda: defaultdict(list))

        # Run through the features in the genome looking for roles that match in the
        # template model.
        LOGGER.info('Started search for matches to roles in template model')
        for feature in feature_list:
            matches = DictList()
            # Remember that a genome feature can have multiple roles.
            for genome_role in feature.search_roles:
                # Search for the role from the feature in the list of roles in
                # the template model.
                match = self.roles.query(lambda x: x[0] == genome_role, 'search_name')
                if len(match) > 0:
                    matches.extend(match)
            if len(matches) > 0:
                for template_role in matches:
                    # For many features, the compartment list is a list of one with
                    # the unknown compartment.
                    for compartment_id in feature.compartments:
                        matched_roles[template_role][compartment_id].append(feature)
                        model_stats['num_roles_matched'] += 1
            else:
                model_stats['num_roles_unmatched'] += 1
        LOGGER.info('Finished search and found %d matching roles', len(matched_roles))

        # It is not possible to reconstruct a model if there are no matched roles.
        if len(matched_roles) == 0:
            raise TemplateError('Genome with {0} features has no matches to roles in template {1}'
                                .format(len(genome_features), self.id))

        # For every matched role, create model reactions from the associated template reactions.
        LOGGER.info('Started adding conditional reactions to model')
        model_reactions = DictList()
        for template_role in matched_roles:
            # A role triggers a complex.
            for complx in self.complexes.get_by_any(list(template_role.complex_ids)):
                # A complex catalyzes a reaction.
                for template_reaction in self.reactions.get_by_any(list(complx.reaction_ids)):
                    # When the matched role is not associated with a specific
                    # compartment, just add the reaction. Otherwise, the template
                    # reaction's compartment must be the same as the matched role's
                    # compartment.
                    for compartment_id in matched_roles[template_role]:
                        if compartment_id == 'u' or compartment_id == template_reaction.compartment:
                            try:
                                model_reactions.append(template_reaction.create_model_reaction(self.compartments))
                            except ValueError:
                                pass

        # Set the gene reaction rule for the model reactions.
        for model_rxn in model_reactions:
            # Go back to the template reaction to follow path to roles.
            try:
                template_rxn = self.reactions.get_by_id(model_rxn.notes['template_id'])
            except KeyError:
                continue
            protein_list = list()
            for complx in self.complexes.get_by_any(template_rxn.complex_ids):
                subunit_list = list()
                for complex_role in complx.roles:
                    template_role = self.roles.get_by_id(complex_role['role_id'])
                    if template_role in matched_roles:
                        gene_list = list()
                        for compartment_id in matched_roles[template_role]:
                            for feature in matched_roles[template_role][compartment_id]:
                                gene_list.append(feature.id)
                                try:
                                    model.genes.append(Gene(feature.id, feature_list.get_by_id(feature.id).function))
                                except ValueError:
                                    pass

                        #  Join multiple features using an OR relationship.
                        if len(gene_list) > 1:
                            subunit_list.append('( {0} )'.format(' or '.join(sorted(gene_list))))
                        else:
                            subunit_list.append(gene_list[0])

                # Join multiple protein subunits using an AND relationship.
                if len(subunit_list) > 0:
                    if len(subunit_list) > 1:
                        protein_list.append('( {0} )'.format(' and '.join(sorted(subunit_list))))
                    else:
                        protein_list.append(subunit_list[0])

            # If there is an association to a feature, add the rule to the reaction.
            if len(protein_list) > 0:
                # Join multiple proteins using an OR relationship.
                if len(protein_list) > 1:
                    gpr_rule = '( {0} )'.format(' or '.join(protein_list))
                else:
                    gpr_rule = protein_list[0]

                model_rxn.gene_reaction_rule = gpr_rule

        model.add_reactions(model_reactions)
        LOGGER.info('Finished adding %d conditional reactions to model', len(model_reactions))

        # Add exchange reactions for all metabolites in the extracellular compartment.
        LOGGER.info('Started adding exchange reactions to model')
        extracellular = model.metabolites.query(lambda x: x == 'e', 'compartment')
        exchanges = [create_boundary(met) for met in extracellular]
        model.add_reactions(exchanges)
        LOGGER.info('Finished adding %d exchange reactions to model', len(exchanges))

        # Add a magic exchange reaction for the special biomass metabolite which seems to be
        # required for ModelSEED models and which we know has id "cpd11416_c".
        # @todo Move this since it is specific to ModelSEED?
        model.add_reactions([create_boundary(self.metabolites.get_by_id('cpd11416_c'), type='sink')])

        # Create a biomass reaction, add it to the model, and make it the objective.
        LOGGER.info('Started adding biomass reaction')
        try:
            biomass_reaction = self.biomasses.get_by_id(biomass_id).create_objective(gc_content)
        except KeyError:
            raise TemplateError('Biomass "{0}" does not exist in template model'.format(biomass_id))
        model.add_reactions([biomass_reaction])
        biomass_reaction.objective_coefficient = 1.0
        LOGGER.info('Finished adding biomass reaction {0} as objective'.format(biomass_reaction.id))

        # Add compartments to the model (this is fixed in a future version of cobra).
        for compartment in self.compartments:
            model.compartments[compartment.model_id] = compartment.name

        return model

    def map_reaction_to_role(self, reaction_id_list):
        """ Follow the path from a reaction to roles.
        
        Parameters
        ----------
        reaction_id_list : list of str
            List of reaction IDs 
        
        Returns
        -------
        dict
            Dictionary keyed by reaction ID with details on each role
        """

        # Find the TemplateReaction objects for the specified IDs.
        try:
            reaction_list = [self.reactions.get_by_id(reaction_id) for reaction_id in reaction_id_list]
        except KeyError as e:
            LOGGER.error('Reaction {0} is not available in template'.format(e.args[0]))
            raise e

        # Follow the path to roles and create output dictionary.
        output = dict()
        for reaction in reaction_list:
            output[reaction.id] = dict()
            output[reaction.id]['name'] = reaction.name
            output[reaction.id]['roles'] = dict()
            for complex_id in reaction.complex_ids:
                complx = self.complexes.get_by_id(complex_id)
                for r in complx.roles:
                    role = self.roles.get_by_id(r['role_id'])
                    output[reaction.id]['roles'][role.id] = dict()
                    output[reaction.id]['roles'][role.id]['name'] = role.name
                    output[reaction.id]['roles'][role.id]['complex_id'] = complx.id
        return output

    def map_role_to_reaction(self, role_id_list):
        """ Follow the path from a role to reactions. 
        
        Parameters
        ----------
        role_id_list : list of str
            List of role IDs
        
        Returns
        -------
        dict
            Dictionary keyed by role ID with details on each reaction
        """

        # Find the TemplateRole objects for the specified role IDs.
        try:
            role_list = [self.roles.get_by_id(role_id) for role_id in role_id_list]
        except KeyError as e:
            LOGGER.error('Role {0} is not available in template'.format(e.args[0]))
            raise e

        # Follow the path to reactions and create output dictionary.
        output = dict()
        for role in role_list:
            output[role.id] = dict()
            output[role.id]['name'] = role.name
            output[role.id]['reactions'] = dict()
            for complex_id in role.complex_ids:
                complx = self.complexes.get_by_id(complex_id)
                for reaction_id in complx.reaction_ids:
                    reaction = self.reactions.get_by_id(reaction_id)
                    output[role.id]['reactions'][reaction.id] = dict()
                    output[role.id]['reactions'][reaction.id]['name'] = reaction.name
                    output[role.id]['reactions'][reaction.id]['complex_id'] = complx.id
        return output

    def to_cobra_model(self, reversible=False, extracellular_id='e'):
        """ Make a COBRA model from the template model.

        The returned model includes exchange reactions for all metabolites in the
        extracellular compartment (which is assumed to have compartment ID 'e').

        Parameters
        ----------
        reversible : bool, optional
            When True, all reactions in returned model are reversible
        extracellular_id : str, optional
            ID of extracellular compartment

        Returns
        -------
        cobra.core.Model
            Template model converted to a COBRA model
        """

        LOGGER.info('Started making cobra Model object from template %s', self.id)
        model = Model(self.id, name=self.name)
        model.add_reactions([rxn.create_model_reaction(self.compartments) for rxn in self.reactions])
        if reversible:
            for rxn in model.reactions:
                rxn.bounds = (-1000.0, 1000.0)
        extracellular = model.metabolites.query(lambda x: x == extracellular_id, 'compartment')
        model.add_reactions([create_boundary(met) for met in extracellular])
        LOGGER.info('Finished making cobra Model object from template %s', self.id)
        return model

    def to_psamm_model(self):
        """ Make a PSAMM native model from the template model.

        PSAMM can import COBRA json (only from a file object) so first convert to
        a COBRA model and then use PSAMM importer to do the conversion.

        Returns
        -------
        psamm.datasource.native.NativeModel
            Template model converted to a PSAMM native model
        """

        if not Importer:
            raise ImportError('to_psamm_model() method requires psamm Importer module')
        with NamedTemporaryFile() as cobra_json:
            # TODO save_json_model() fails with TypeError exception
            save_json_model(self.to_cobra_model(), cobra_json)
            cobra_json.seek(0)
            model = Importer().import_model(cobra_json)
        return model

    def to_reaction_list_file(self, list_file_name, dictionary_file_name):
        """ Make a file with the list of reactions from the template.

        The output file can be used as the universal model for fastgapfill.

        Parameters
        ----------
        list_file_name : str
            Path to output file with reaction list
        dictionary_file_name : str
            Path to output dictionary file that maps model metabolite IDs to template metabolite IDs
        """

        # All coefficients must be whole numbers.
        integer_re = re.compile('\.0')

        metabolite_dict = dict()
        with open(list_file_name, 'w') as handle:
            for rxn in self.reactions:
                invalid = False
                for coefficient in rxn.metabolites.values():
                    if abs(coefficient) < 1.0:
                        invalid = True
                if invalid:
                    LOGGER.warn('Skipped reaction %s with invalid coefficient: %s',
                                rxn.id, rxn.reaction_str)
                    continue
                if len(rxn.reactants) == 0:
                    LOGGER.warn('Skipped reaction %s with no reactants', rxn.id)
                    continue
                if len(rxn.products) == 0:
                    LOGGER.warn('Skipped reaction %s with no products', rxn.id)
                    continue
                for metabolite in rxn.metabolites:
                    model_compartment = self.compartments.get_by_id(metabolite.compartment)
                    model_id = '{0}_{1}'.format(metabolite.notes['universal_id'], model_compartment.model_id)
                    metabolite_dict[model_id] = metabolite.id
                definition = rxn.reaction_str
                handle.write('{0}: {1}\n'.format(rxn.id, re.sub(integer_re, '', definition)))

        with open(dictionary_file_name, 'w') as handle:
            for model_id in metabolite_dict:
                handle.write('{0}\t{1}\n'.format(model_id, metabolite_dict[model_id]))
