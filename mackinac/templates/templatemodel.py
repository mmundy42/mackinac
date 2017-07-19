from warnings import warn
import logging
from collections import defaultdict
from six import iteritems

from cobra.core import Object, DictList, Model, Gene

from .util import read_source_file, create_exchange_reaction
from .templatecompartment import create_template_compartment, compartment_fields
from .templatebiomass import create_template_biomass_component, biomass_component_fields
from .templatebiomass import create_template_biomass, biomass_fields
from .templaterole import create_template_role, role_fields
from .templatecomplex import create_template_complex, complex_fields
from .templatereaction import create_template_reaction, reaction_fields
from .feature import create_features_from_patric


# Logger for this module
LOGGER = logging.getLogger(__name__)


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

    def init_from_files(self, compartment_filename, biomass_filename, component_filename,
                        reaction_filename, complex_filename, role_filename, universal_metabolites,
                        universal_reactions, verbose=False):
        """ Initialize object from ModelSEED source files.
        
        ModelSEED source files are tab-delimited files with a header line that defines
        the fields. Each line contains the attributes for initializing an object.
        
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
        verbose : bool
            When true
        """

        LOGGER.info('Started initializing from source files')

        # Get compartments from the compartment source file.
        self.compartments.extend(read_source_file(compartment_filename, compartment_fields,
                                                  create_template_compartment))

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

        # Get complexes from the complex source file. Only complexes that are
        # referenced by reactions are added to the template model.
        all_complexes = read_source_file(complex_filename, complex_fields, create_template_complex)

        # Get reactions from the reaction source file. Get details about reaction from
        # corresponding universal reaction.
        skipped = 0
        bad_status = 0
        reactions = read_source_file(reaction_filename, reaction_fields, create_template_reaction)
        for rxn in reactions:
            # Get universal reaction for definition, metabolites, and status.
            try:
                u_rxn = universal_reactions.get_by_id(rxn.id)
            except KeyError:
                if verbose:
                    warn('Template reaction {0} was not found in universal reactions'.format(rxn.id))
                skipped += 1
                continue
            if 'OK' not in u_rxn.notes['status']:
                if verbose:
                    warn('Universal reaction {0} status {1} is not OK'.format(u_rxn.id, u_rxn.notes['status']))
                bad_status += 1

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
                except:
                    raise TemplateError('Complex {0} referenced by reaction {1} was not found'
                                        .format(complex_id, rxn.id))
                self.complexes.union(complexes)
                for complx in complexes:
                    complx.reaction_ids.add(rxn.id)

        if skipped > 0:
            warn('{0} template reactions were not found in universal reactions'.format(skipped))
        if bad_status > 0:
            warn('{0} template reactions reference a universal reaction with bad status'.format(bad_status))

        # Get roles from the role source file. Only roles that are referenced by
        # complexes are added to the template model.
        all_roles = read_source_file(role_filename, role_fields, create_template_role)
        for complx in self.complexes:
            try:
                roles = [all_roles.get_by_id(role['role_id']) for role in complx.roles]
            except KeyError:
                raise TemplateError('Role {0} referenced by complex {1} is not available'
                                    .format(role['role_id'], complx.id))
            self.roles.union(roles)
            for role in roles:
                role.complex_ids.add(complx.id)

        # Build an index to lookup roles by EC number.
        self._build_role_ec_index()
        LOGGER.info('Finished initializing from source files')

        return

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
            self.role_name_index.append(role.search_name[0])
        return

    def reconstruct(self, genome, genome_features, biomass_id, annotation='PATRIC'):
        """ Reconstruct a draft model from the genome of an organism.
        
        For template models created from ModelSEED source files, only a PATRIC 
        annotation works to reconstruct a draft model. Use the get_genome_summary() 
        and get_genome_features() functions to retrieve the PATRIC annotation 
        needed for the first two parameters.
        
        Parameters
        ----------
        genome : dict
            Dictionary of genome summary data for organism
        genome_features : list of dict
            List of feature data for organism
        biomass_id : str
            ID of biomass entity used to create biomass objective
        annotation : {'PATRIC'}
            Type of annotation in feature data
            
        Returns
        -------
        cobra.core.Model
            Draft model of organism based on genome features
        """

        # @todo Should there be a check to make sure template model is appropriate for organism?
        # if genome['domain'].lower() != self.domain:
        #     raise TemplateError('domain mismatch')

        # Create Feature objects from the list of features in the genome annotation.
        if annotation == 'PATRIC':
            feature_list, genome_stats = create_features_from_patric(genome_features)
        else:
            raise ValueError('Annotation type {0} is not supported'.format(annotation))
        if len(feature_list) == 0:
            raise ValueError('No valid features found in genome {0}'.format(genome['genome_id']))

        # Create a new cobra.core.Model object.
        model = Model(genome['genome_id'], name=genome['organism_name'])
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
            raise TemplateError('Genome {0} with {1} features has no matches to roles in template {2}'
                                .format(genome['genome_id'], len(genome_features), self.id))

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
        exchanges = [create_exchange_reaction(met) for met in extracellular]
        model.add_reactions(exchanges)
        LOGGER.info('Finished adding %d exchange reactions to model', len(exchanges))

        # Check genome summary for gc content value, otherwise use default value.
        LOGGER.info('Started adding biomass reaction')
        try:
            gc_content = genome['gc_content']
            if gc_content > 1.0:
                gc_content /= 100.0
        except KeyError:
            gc_content = 0.5
            LOGGER.warn('GC content not found in genome summary, using default value of {0}'
                        .format(gc_content))

        # Create a biomass reaction, add it to the model, and make it the objective.
        try:
            biomass_reaction = self.biomasses.get_by_id(biomass_id).create_objective(gc_content)
        except KeyError:
            raise TemplateError('Biomass "{0}" does not exist in template model'.format(biomass_id))
        model.add_reactions([biomass_reaction])
        biomass_reaction.objective_coefficient = 1.0
        LOGGER.info('Finished adding biomass reaction {0} as objective'.format(biomass_reaction.id))

        # Add a magic exchange reaction for the special biomass metabolite which seems to be
        # required for ModelSEED models and which we know has id "cpd11416_c".
        model.add_reactions([create_exchange_reaction(model.metabolites.get_by_id('cpd11416_c'))])

        return model

    def reaction_to_role(self, reaction_id_list):
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
        except KeyError:
            raise TemplateError('Reaction {0} is not available in template'.format(reaction_id))

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

    def role_to_reaction(self, role_id_list):
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
        except KeyError:
            raise TemplateError('Role {0} is not available in template'.format(role_id))

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
