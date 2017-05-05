from warnings import warn

from cobra.core import Object, DictList, Model, Reaction

from .templatecompartment import create_template_compartment, compartment_fields
from .templatebiomass import create_template_biomass_component, biomass_component_fields
from .templatebiomass import create_template_biomass, biomass_fields
from .templatereaction import reaction_fields
from .feature import Feature
from .util import read_source_file, validate_header


class TemplateError(Exception):
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
        Domain of organisms represented by template model
        
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
    biomasses : cobra.core.DictList
        List of TemplateBiomass objects
    metabolites : cobra.core.DictList
        List of cobra.core.Metabolite objects
    """

    def __init__(self, id, name, type='growth', domain='Bacteria'):
        Object.__init__(self, id, name)
        self.type = type
        self.domain = domain

        self.roles = DictList()
        self.complexes = DictList()
        self.compartments = DictList()
        self.reactions = DictList()
        self.metabolites = DictList()
        self.biomasses = DictList()

    def add_compartments(self, compartment_filename):
        """ Add compartments to the template model from a source file.
        
        Parameters
        ----------
        compartment_filename : str
            Path to source file that defines TemplateCompartment objects
        """

        self.compartments.extend(read_source_file(compartment_filename,
                                                  compartment_fields,
                                                  create_template_compartment))
        return

    def add_biomasses(self, biomass_filename, component_filename, universal_metabolites):
        """ Add biomasses to the template model from source files.

        Parameters
        ----------
        biomass_filename : str
            Path to source file that defines TemplateBiomass objects
        component_filename : str
            Path to source file that defines TemplateBiomassComponent objects
        universal_metabolites : cobra.core.DictList
            List of cobra.core.Metabolite objects for universal metabolites
        """

        components = read_source_file(component_filename, biomass_component_fields,
                                      create_template_biomass_component)
        biomasses = read_source_file(biomass_filename, biomass_fields, create_template_biomass)
        for biomass in biomasses:
            biomass.add_components(components.query(lambda x: x == biomass.id, 'biomass_id'),
                                   universal_metabolites)
            self.metabolites.union(biomass.get_metabolites())
            self.biomasses.append(biomass)
        return

    def add_reactions(self, reaction_filename, universal_reactions, universal_metabolites,
                      universal_complexes, universal_roles, verbose=False):
        """ Add reactions to the template model from a source file.
    
        Parameters
        ----------
        reaction_filename : str
            Path to source file that defines reactions to add 
        universal_reactions : cobra.core.DictList
            List of TemplateReaction objects for universal reactions
        universal_complexes : cobra.core.DictList
            List of TemplateComplex objects for universal complexes
        universal_roles : cobra.core.DictList
            List of  TemplateRole objects for universal roles
        verbose : bool, optional
            When True, show all warning messages
        """

        # Explain why this is different.
        skipped = 0
        with open(reaction_filename, 'r') as handle:
            # The first line has the header with the field names (which can be in any order).
            names = validate_header(handle.readline().strip().split('\t'), reaction_fields)

            # There is one object per line in the file.
            linenum = 1
            for line in handle:
                # Get the object data.
                linenum += 1
                fields = line.strip().split('\t')
                if len(fields) < len(reaction_fields):
                    warn('Skipped object on line {0} because missing one or more fields: {1}'
                         .format(linenum, fields))
                    skipped += 1
                    continue

                # Get the corresponding TemplateReaction object from the universal reactions.
                try:
                    rxn = universal_reactions.get_by_id(fields[names['id']])
                except KeyError:
                    if verbose:
                        warn('Reaction {0} is not available'.format(fields[names['id']]))
                    skipped += 1
                    continue

                # Update the reaction with additional data from the source file.
                rxn.complex_ids = fields[names['complexes']]
                rxn.type = fields[names['type']]
                rxn.compartment_ids = fields[names['compartment']]
                rxn.base_cost = float(fields[names['base_cost']])
                rxn.forward_cost = float(fields[names['forward_cost']])
                rxn.reverse_cost = float(fields[names['reverse_cost']])
                rxn.direction = fields[names['direction']]
                rxn.gapfill_direction = fields[names['gfdir']]

                # Add the reaction and its metabolites to the template model.
                self.reactions.append(rxn)
                self.metabolites.union(rxn.metabolites)

                # complexes, deal with conditional
                if rxn.type == 'conditional':
                    try:
                        complexes = [universal_complexes.get_by_id(complex_id) for complex_id in rxn.complex_ids]
                    except:
                        raise TemplateError('Complex {0} on line {1} is not available'.format(rxn.complex_ids, linenum))
                    self.complexes.union(complexes)
                    for complx in complexes:
                        complx.reaction_ids.add(rxn.id)

        if skipped > 0:
            warn('{0} template reactions were not found in universal reactions'.format(skipped))

        # Add the roles referenced by the complexes to the template model.
        for complx in self.complexes:
            try:
                roles = [universal_roles.get_by_id(role['role_id']) for role in complx.roles]
            except KeyError:
                raise TemplateError('Role {0} referenced by complex {1} is not available'
                                    .format(role['role_id'], complx.id))
            self.roles.union(roles)
            for role in roles:
                role.complex_ids.add(complx.id)

        return

    def build_model(self, genome, genome_features, biomass_id):
        """ Build a model for an organism.
        
        For PATRIC genomes, use the get_genome_summary() and get_genome_features() 
        functions to retrieve the data for the first two parameters.
        
        Parameters
        ----------
        genome : dict
            Dictionary of genome summary data for organism
        genome_features : list of dict
            List of feature data for organism
        biomass_id : str
            ID of biomass entity used to create biomass objective
            
        Returns
        -------
        cobra.core.Model
            Draft model of organism based on genome features
        """

        # Create a new COBRApy Model object.
        model = Model(genome['genome_id'], name=genome['organism_name'])
        # @todo Use a defaultdict here
        statistics = {'num_roles_matched': 0, 'num_roles_unmatched': 0}

        # Create a biomass objective and add it model.
        # @todo Set a default for gc_content or use a parameter?
        try:
            biomass_reaction = self.biomasses.get_by_id(biomass_id).create_objective(genome['gc_content'])
        except KeyError:
            raise TemplateError('Biomass "{0}" does not exist in template model'.format(biomass_id))
        biomass_reaction.objective_coefficient = 1.0
        model.add_reaction(biomass_reaction)  # This should get metabolites added too

        # Need to go through list of biomass components and add link to metabolite object.
        # Or just give build model all of the metabolites which are available from this object.

        # Select a biomass based on gram stain.
        # Add all of the biomass reactions to the model.
        # biomass_metabolites.extend([universal.metabolites.get_by_id(component.metabolite_id)
        #                            for component in self.biomasses[0].components])
        # biomass_reaction = self.biomasses[0].create_objective(biomass_metabolites, genome['gc_content'])
        # print(biomass_reaction.reaction)
        # for biomass_id in self.biomasses:
        #     self.biomasses[biomass_id].create_objective(model, genome.gc_content, objective)

            # Add a magic exchange reaction for the special biomass metabolite which seems to be
            # required for these models and which we know has id "cpd11416_c".
            #        model.add_reaction(self.create_exchange_reaction(model.metabolites.get_by_id('cpd11416_c')))

        # Start by adding the universal reactions to the model.
        # for reaction_id in self.universal_reactions:
        #     reaction = self.create_reaction(self.reactions[reaction_id])
        #     model.add_reaction(reaction)

        # Go through the list of features and build feature objects for the ones that have product defined?
        # @todo Is the annotation in the summary data? Could get rid of if else on every feature
        feature_list = list()
        for index in range(len(genome_features)):
            if 'product' in genome_features[index]:
                if genome_features[index]['annotation'] == 'PATRIC':
                    feature_id = genome_features[index]['patric_id']
                elif genome_features[index]['annotation'] == 'RefSeq':
                    feature_id = genome_features[index]['refseq_locus_tag']
                else:
                    raise ValueError('Annotation type {0} is not supported'
                                     .format(genome_features[index]['annotation']))

                feature_list.append(Feature(feature_id, genome_features[index]['product']))
        
        # The matched_roles dictionary is keyed by role ID and contains all of the roles in
        # features from the genome of the organism that match a role in the template model.
        # When there is a match between a role from a feature in the genome and a role from the
        # template model, the role is added to the matched_roles dictionary.  The value
        # in the matched_roles dictionary is another dictionary keyed by compartment ID where
        # the value is a list of Feature objects. When there is a match, the feature is
        # assumed to be active in all of the compartments associated with the feature. Most of
        # the time the compartment is unknown which means the feature is not localized to a
        # specific compartment in the cell.
        matched_roles = dict()

        # Run through the features in the genome looking for roles that match in the template model.
        for feature in feature_list:
            # Make a feature object feature['product']
            # Need to split product into list of genome roles that can look up by search name
            # For each role in the feature, see if there is a match to a role in the template model.
            for genome_role in feature.search_roles:
                # Search for the role from the feature in the list of roles in the template model.
                # @todo KEGG roles can have multiple names but this is only searching for the primary name.
                matches = self.roles.query(lambda x: x[0] == genome_role, 'search_name')
                if len(matches) > 1:
                    warn('Got more than one match to a role\n{0}'.format(matches))
                if len(matches) > 0:
                    template_role = matches[0]

                    # For many features, the compartment list is a list of one with the unknown compartment.
                    for compartment_id in feature.compartments:
                        if template_role not in matched_roles:
                            matched_roles[template_role] = dict()  # Dictionary keyed by compartment ID
                        if compartment_id not in matched_roles[template_role]:
                            matched_roles[template_role][compartment_id] = list()  # List of features
                        matched_roles[template_role][compartment_id].append(feature)
                        statistics['num_roles_matched'] += 1
                else:
                    statistics['num_roles_unmatched'] += 1

        # It is not possible to reconstruct a model if there are no matched roles.
        if len(matched_roles) == 0:
            raise TemplateError('Genome {0} with {1} features has no matches to roles in template {2}'
                                .format(genome['genome_id'], len(genome_features), self.id))

        # For every matched role, add the associated reactions to the model.
        for template_role in matched_roles:
            # A role triggers a complex.
            # @todo do this better with query function?
            for complex_id in template_role.complex_ids:
                complex = self.complexes.get_by_id(complex_id)
                # A complex has step reaction (or a reaction is a step of a complex).
                for reaction_id in complex.reaction_ids:
                    template_reaction = self.reactions.get_by_id(reaction_id)
                    # When the matched role is not associated with a specific compartment, just add
                    # the reaction. Otherwise, the template reaction's compartment must be the same
                    # as the matched role's compartment.
                    for compartment_id in matched_roles[template_role]:
                        if compartment_id == 'u' or compartment_id == template_reaction.compartment:
                            # When the reaction has already been added to the model, just update the
                            # gene reaction rule.
                            try:
                                reaction = model.reactions.get_by_id(template_reaction.make_model_id())
                                rule = '(' + ' or '.join(
                                    [f.id for f in matched_roles[template_role][compartment_id]]) + ')'
                                reaction.gene_reaction_rule = reaction.gene_reaction_rule + ' and ' + rule
                            except KeyError:
                                model.add_reaction(template_reaction.create_model_reaction(self.compartments, matched_roles[template_role][compartment_id]))

        # Add exchange reactions for all metabolites in the extracellular compartment.
        # @todo Switch to model.add_boundary(metabolite, type='exchange')
        exchanges = model.metabolites.query(lambda x: x == 'e', 'compartment')
        er = [self.create_exchange_reaction(met) for met in exchanges]
        model.add_reactions(er)
        # Use a function from util if not in cobra
        # for metabolite in model.metabolites:
        #     if metabolite.compartment == 'e':
        #         model.add_reaction(self.create_exchange_reaction(metabolite))

        # Add a magic exchange reaction for the special biomass metabolite which seems to be
        # required for these models and which we know has id "cpd11416_c".
        #        model.add_reaction(self.create_exchange_reaction(model.metabolites.get_by_id('cpd11416_c')))

        return model

    def create_exchange_reaction(self, metabolite):

        rxn = Reaction(id='EX_{0}'.format(metabolite.id),
                       name='{0} exchange'.format(metabolite.name),
                       lower_bound=-1000.0,
                       upper_bound=1000.00)
        rxn.add_metabolites({metabolite: -1})
        return rxn
