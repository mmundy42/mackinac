from os.path import join, exists
from os import makedirs, remove
from warnings import warn
from math import log10, isnan
import subprocess
from collections import defaultdict

from .logger import LOGGER
from .workspace import get_workspace_object_data

# E values of less than 1E-200 are treated as 1E-200 to avoid log of 0 issues.
MIN_EVALUE = 1E-200

# Name of fasta file with protein sequences for target feature IDs
protein_sequence_file_name = 'protein.fasta'

# Name of feature ID to role ID mapping file
fid_role_file_name = 'otu_fid_role.tsv'


class LikelihoodError(Exception):
    """ Exception raised when there is a problem calculating likelihoods. """
    pass


class LikelihoodAnnotation(object):
    """ Likelihood-based gene annotation for a genome.

    This class implements the algorithm described in "Likelihood-Based Gene
    Annotations for Gap Filling and Quality Assessment in Genome-Scale Metabolic
    Models". Private methods implement the calculations described by the equations
    in the Methods section of the paper.

    Parameters
    ----------
    search_program_path : str
        Path to search program executable
    search_db_path : str
        Path to search database file
    fid_role_path : str
        Path to feature ID to role ID mapping file
    work_folder : str
        Path to folder for storing intermediate files

    Attributes
    ----------
    search_program_threads : int
        Number of threads search program can use (more makes search faster)
    search_program_evalue : float
        Value for search program evalue parameter
    search_program_accel : float
        Value for search program accel parameter (speed vs. sensitivity)
    pseudo_count : float
        Value used to dilute the likelihoods of annotations that have weak homology
        to the query
    separator : str
        Character string not found in any roles and used to split lists of strings
    _dilution_percent : float
        Percentage of the maximum likelihood to use as a threshold to consider
        other genes as having a particular function aside from the one with
        greatest likelihood
    debug : bool
        Set to True to save generated data for debug or detailed analysis
    _roleset_values : dict
        Dictionary keyed by query feature ID and list of tuples with roleset string
        and likelihood as value
    _role_values : list
        List of tuples with query feature ID, role ID, and role likelihood
    _total_role_values : dict
        Dictionary keyed by role ID and list of tuples with the maximum likelihood
        of the role and the GPR string of feature IDs as value
    _complex_values : dict
        Dictionary keyed by complex ID and likelihood, type, GPR string, list of
        roles not in the organism, and list of roles not in target search database
        as values
    _reaction_values : dict
        Dictionary keyed by reaction ID and likelihood, type, GPR string, and
        complex string as values
    _statistics : dict
        Dictionary keyed by statistic name and number as value
    _target_rolesets : dict
        Dictionary keyed by target feature ID and role ID as value
    """

    def __init__(self, search_program_path, search_db_path, fid_role_path, work_folder):

        self.search_program_path = search_program_path
        self.search_db_path = search_db_path
        self.work_folder = work_folder

        self.search_program_threads = 4
        self.search_program_evalue = 1E-5
        self.search_program_accel = 0.33
        self.pseudo_count = 40.0
        self.separator = '///'
        self._dilution_percent = 0.8
        self.debug = True

        self._roleset_values = defaultdict(list)
        self._role_values = list()
        self._total_role_values = dict()
        self._complex_values = dict()
        self._reaction_values = dict()
        self._statistics = {
            'num_nonzero_likelihoods': 0,
            'num_zero_likelihoods': 0,
            'average_likelihood': 0.0,
            'num_features': 0,
            'num_proteins': 0,
            'complex_types': {
                'num_no_reps': 0,
                'num_not_there': 0,
                'num_no_reps_and_not_there': 0,
                'num_full': 0,
                'num_partial': 0
            },
            'reaction_types': {
                'has_complexes': 0,
                'no_complexes': 0
            }
        }

        # Read the data file that maps target feature IDs to role IDs and build
        # a dictionary with target feature ID as key and the role ID as the value.
        # @todo Lost the concatenated role names in updated fid_role file
        self._target_rolesets = dict()
        with open(fid_role_path, 'r') as handle:
            for line in handle:
                fields = line.strip('\r\n').split('\t')
                self._target_rolesets[fields[0]] = fields[1]
        return

    @property
    def dilution_percent(self):
        return self._dilution_percent

    @dilution_percent.setter
    def dilution_percent(self, new_value):
        if new_value <= 0.0 or new_value > 1.0:
            raise ValueError('Dilution percent value must greater than 0 and less than or equal to 1')
        self._dilution_percent = new_value

    @property
    def statistics(self):
        return self._statistics.copy()

    @property
    def reaction_values(self):
        return self._reaction_values.copy()

    def calculate(self, genome_id, feature_list, complexes_to_roles, reactions_to_complexes):
        """ Calculate reaction likelihoods from annotated features of a genome.

        Parameters
        ----------
        genome_id : str
            ID of genome (just for naming temporary files)
        feature_list : list of dict
            List of annotated features with ID and amino acid sequence
        complexes_to_roles : dict
            Dictionary with complex ID as key and list of role IDs as value
        reactions_to_complexes : dict
            Dictionary with reaction ID as key and list of complex IDs as value
        """

        # If needed, create folder for intermediate files.
        if not exists(self.work_folder):
            makedirs(self.work_folder)

        # Run the probabilistic annotation algorithm to calculate reaction likelihoods.
        self._calculate_roleset_likelihoods(genome_id, feature_list)
        self._calculate_role_likelihoods()
        self._calculate_total_role_likelihoods()
        self._calculate_complex_likelihoods(complexes_to_roles)
        self._calculate_reaction_likelihoods(reactions_to_complexes)

        # If requested, save all of the intermediate data for debug.
        if self.debug:
            self._save_data(genome_id)

        return

    def _calculate_roleset_likelihoods(self, genome_id, feature_list):
        """ Calculate the likelihoods of rolesets from a search for similar proteins.

        A roleset is each possible combination of roles implied by the functions
        of the proteins in subsystems.  The likelihoods are stored in a dictionary
        with query feature IDs as the key and a list of tuples as the value.  Each
        tuple contains (1) roleset string, and (2) likelihood value.  The roleset
        string is a concatenation of all of the roles of a protein with a single
        function (order does not matter).

        Each entry in the list of annotated features is a dictionary that needs to
        contain an 'id' key with the feature ID and a 'protein_translation' key with
        the amino acid sequence.

        Parameters
        ----------
        genome_id : str
            ID of model
        feature_list : list
            List of annotated features from a genome
        """

        if len(feature_list) == 0:
            raise ValueError('No features in genome for model {0}'.format(genome_id))

        # Run the list of features to build a FASTA file of amino acid sequences used as
        # the query for a search against known features.
        self._statistics['num_features'] = len(feature_list)
        query_file = join(self.work_folder, '{0}.faa'.format(genome_id))
        with open(query_file, 'w') as handle:
            for feature in feature_list:
                # Skip the feature if there is no amino acid sequence.
                if 'protein_translation' in feature:
                    handle.write('>{0}\n{1}\n'.format(feature['id'], feature['protein_translation']))
                    self._statistics['num_proteins'] += 1
                elif 'aa_sequence' in feature:
                    handle.write('>{0}\n{1}\n'.format(feature['patric_id'], feature['aa_sequence']))
                    self._statistics['num_proteins'] += 1
        LOGGER.info('Found %d features with amino acid sequence from %d total features',
                    self._statistics['num_proteins'], self._statistics['num_features'])

        # Build the command based on the configured search program. Output format 6 is
        # tab-delimited format.
        result_file = join(self.work_folder, '{0}.blastout'.format(genome_id))
        if 'usearch' in self.search_program_path.lower():
            args = [self.search_program_path,
                    '-ublast', query_file,
                    '-db', self.search_db_path,
                    '-evalue', str(self.search_program_evalue),
                    '-accel', str(self.search_program_accel),
                    '-threads', str(self.search_program_threads),
                    '-blast6out', result_file]
        elif 'blastp' in self.search_program_path:
            args = [self.search_program_path,
                    '-query', query_file,
                    '-db', self.search_db_path,
                    '-outfmt', '6',
                    '-evalue', str(self.search_program_evalue),
                    '-num_threads', str(self.search_program_threads),
                    '-out', result_file]
        else:
            raise ValueError('Search program {0} is not supported, use either usearch or blastp')

        # Run the command to search for query proteins against subsystem proteins.
        cmd = ' '.join(args)
        LOGGER.info('Started search for query proteins using "%s"', cmd)
        try:
            proc = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            (stdout, stderr) = proc.communicate()
            if proc.returncode < 0:
                raise LikelihoodError('"{0}" was terminated by signal {1}'.format(args[0], -proc.returncode))
            else:
                if proc.returncode > 0:
                    raise LikelihoodError('"{0}" failed with return code {1}\n'
                                          'Command: "{2}"\nStdout: "{3}"\nStderr: "{4}"'
                                          .format(args[0], proc.returncode, cmd, stdout, stderr))
        except OSError as e:
            raise LikelihoodError('Failed to run "{0}": {1}'.format(args[0], e.strerror))
        LOGGER.info('Finished search for query proteins')

        # The result file is in BLAST output format 6 where each line describes an alignment
        # found by the search program.  A line has 12 tab delimited fields: (1) query label,
        # (2) target label, (3) percent identity, (4) alignment length, (5) number of
        # mismatches, (6) number of gap opens, (7) 1-based position of start in query,
        # (8) 1-based position of end in query, (9) 1-based position of start in target,
        # (10) 1-based position of end in target, (11) e-value, and (12) bit score.

        # Parse the output from the search program to build a dictionary with query feature ID as key
        # and a list of tuples with target feature ID and score (converted e-value) as value.
        # See equation 1 in the paper ("Calculating annotation likelihoods")
        # query --> [ (target1, score 1), (target 2, score 2), ... ]
        query_scores = dict()
        with open(result_file, 'r') as handle:
            for line in handle:
                fields = line.strip('\r\n').split('\t')
                query_id = fields[0]
                target_id = fields[1]
                if float(fields[11]) < 0.0:  # Throw out alignments with a negative bit score
                    warn('Negative bit score is ignored for {0}'.format(line))
                    continue
                score = -1.0 * log10(float(fields[10]) + MIN_EVALUE)
                value = (target_id, score)
                try:
                    query_scores[query_id].append(value)
                except KeyError:
                    query_scores[query_id] = [value]

        # For each query feature we calculate the likelihood of each possible roleset
        # See equation 2 in the paper ("Calculating annotation likelihoods" section).
        # The results are stored in roleset_likelihoods dictionary keyed by query
        # feature IDs (as described above).
        for query_id in query_scores:
            # First find the maximum score for this feature.
            max_score = 0.0
            for value in query_scores[query_id]:
                if value[1] > max_score:
                    max_score = value[1]

            # Second calculate the cumulative squared scores for each possible
            # roleset. This along with "pseudocount * maxscore" is equivalent to
            # multiplying all scores by themselves and then dividing by the max
            # score. This is done to avoid some pathological cases and give more
            # weight to higher-scoring hits and not let much lower-scoring hits
            # or noise drown them out.
            # Build a dictionary keyed by roleset of the sum of squares of the log-scores.
            # roleset -> sum of squares
            roleset_scores = defaultdict(float)
            num_missing_rolesets = 0
            for value in query_scores[query_id]:
                try:
                    roleset = self._target_rolesets[value[0]]
                    rs_score = float(value[1]) ** 2
                    roleset_scores[roleset] += rs_score
                except KeyError:
                    num_missing_rolesets += 1
                    LOGGER.warn('Target feature id {0} from search results file was not found in roleset dictionary'
                                .format(value[0]))

            if num_missing_rolesets > 0:
                warn('{0} feature IDs not found in target rolesets dictionary (most likely caused by '
                     'mismatch between protein fasta file and feature ID to role ID mapping file'
                     .format(num_missing_rolesets))

            # Third calculate the likelihood that this feature has the given functional annotation.
            # Start with the denominator which is the sum of squares of the log-scores for
            # all possible rolesets.
            denom = float(self.pseudo_count) * max_score
            for roleset in roleset_scores:
                denom += roleset_scores[roleset]
            if isnan(denom):
                raise LikelihoodError('Denominator in likelihood calculation for gene {0} is NaN {1}'
                                      .format(query_id, denom))

            # The numerators are the sum of squares for each roleset.
            # Fourth calculate the likelihood for each roleset and store in the output dictionary.
            # query -> [ (roleset1, likelihood1), (roleset2, likelihood2), ... ]
            for roleset in roleset_scores:
                likelihood = roleset_scores[roleset] / denom
                if isnan(likelihood):
                    raise LikelihoodError('Likelihood for roleset {0} in gene {1} is NaN based on score {2}'
                                          .format(roleset, query_id, roleset_scores[roleset]))
                if likelihood < 0.0 or likelihood > 1.0:
                    warn('Query ID {0} with roleset {1} has an invalid likelihood of {2:1.6f}'
                         .format(query_id, roleset, likelihood))
                value = (roleset, likelihood)
                self._roleset_values[query_id].append(value)

        # If not needed, delete intermediate files.
        if not self.debug:
            remove(query_file)
            remove(result_file)
        LOGGER.info('Calculated %d roleset likelihoods', len(self._roleset_values))

        return

    def _calculate_role_likelihoods(self):
        """ Compute likelihood of each role from the rolesets for each query protein.

        At the moment the strategy is to take any set of rolesets containing
        the same roles and add their likelihoods.  So if we have hits to both
        a bifunctional enzyme with R1 and R2, and hits to a monofunctional enzyme
        with only R1, R1 ends up with a greater probability than R2.

        The likelihoods are stored in a list of tuples where each tuple contains
        (1) query feature ID, (2) role ID, and (3) role likelihood.

        I had tried to normalize to the previous sum but I need to be more careful
        than that (I'll put it on my TODO list) because if you have e.g. one hit
        to R1R2 and one hit to R3 then the probability of R1 and R2 will be unfairly
        brought down due to the normalization scheme.
        """

        if len(self._roleset_values) == 0:
            raise ValueError('There are no values in roleset likelihoods dictionary')

        # Iterate over all of the query features in the roleset likelihood dictionary.
        # query -> [ (roleset1, likelihood_1), (roleset2, likelihood_2), ...]
        for query_id in self._roleset_values:
            # Convert feature annotations into functional roles.
            # See equation 3 in the paper ("Calculating reaction likelihoods" section).
            functional_likelihood = defaultdict(float)
            for value in self._roleset_values[query_id]:
                # Add up all the instances of each particular role on the list.
                for role in value[0].split(self.separator):
                    functional_likelihood[role] += value[1]

            # Add the roles to the list of role likelihoods. Each entry in the list is a
            # tuple with query feature ID, role, and role likelihood.
            for role in functional_likelihood:
                if functional_likelihood[role] < 0.0 or functional_likelihood[role] > 1.0:
                    warn('Query ID {0} with role "{1}" has an invalid likelihood of {2:1.6f}'
                         .format(query_id, role, functional_likelihood[role]))
                self._role_values.append((query_id, role, functional_likelihood[role]))

        LOGGER.info('Calculated %d role likelihoods', len(self._role_values))
        return

    def _calculate_total_role_likelihoods(self):
        """ Given the likelihood that each gene has each role, estimate the likelihood
            that the entire organism has that role.

        To avoid exploding the likelihoods with noise, just take the maximum
        likelihood of any query feature having a function and use that as the
        likelihood that the function exists in the cell.

        A feature is assigned to a role if it is within DILUTION_PERCENT of the maximum
        likelihood. DILUTION_PERCENT can be adjusted in the configuration. For each
        role the maximum likelihood and the estimated set of features that perform that
        role are linked with an OR relationship to form a Boolean Gene-Protein
        relationship (GPR).

        The likelihoods are stored in a dictionary with the role ID as the key and a
        tuple as the value. Each tuple contains (1) the maximum likelihood of the role
        and (2) the GPR string of feature IDs.
        """

        if len(self._role_values) == 0:
            raise ValueError('There are no values in the role likelihoods list')

        # Find maximum likelihood among all query features for each role.
        # This is assumed to be the likelihood of that role occurring in the organism as a whole.
        # value = (query feature ID, role, role likelihood)
        role_max_likelihood = dict()
        for value in self._role_values:
            try:
                if value[2] > role_max_likelihood[value[1]]:
                    role_max_likelihood[value[1]] = value[2]
            except KeyError:
                role_max_likelihood[value[1]] = value[2]

        # Get the features within DILUTION_PERCENT percent of the maximum likelihood and
        # assert that these are the most likely genes responsible for that role.
        # See equation 4 in the paper ("Calculating reaction likelihoods" section).
        # role -> [ query feature ID 1, query feature ID 2, ... ]
        role_genes = defaultdict(list)
        for value in self._role_values:
            if value[1] not in role_max_likelihood:
                raise LikelihoodError('Role {0} not placed properly in role_max_likelihood dictionary?'
                                      .format(value[1]))
            if value[2] >= self._dilution_percent * role_max_likelihood[value[1]]:
                role_genes[value[1]].append(value[0])

        # Build the dictionary of total role probabilities.
        for role in role_max_likelihood:
            gene_list = sorted(list(set(role_genes[role])))
            gpr = ' or '.join(gene_list)
            # We only need to group these if there is more than one role (avoids extra
            # parenthesis when computing complexes).
            if len(gene_list) > 1:
                gpr = '(' + gpr + ')'
            if role in self._total_role_values:
                warn('Duplicate role {0} in total role likelihoods'.format(role))
            if role_max_likelihood[role] < 0.0 or role_max_likelihood[role] > 1.0:
                warn('Role "{0}" has invalid likelihood {1:1.6f}'.format(role, role_max_likelihood[role]))
            self._total_role_values[role] = (role_max_likelihood[role], gpr)

        LOGGER.info('Calculated %d total role likelihoods', len(self._total_role_values))
        return

    def _calculate_complex_likelihoods(self, complexes_to_roles):
        """ Compute the likelihood of each protein complex from the likelihood of each role.

        A protein complex represents a set functional roles that must all be present
        for a complex to exist.  The likelihood of the existence of a complex is
        computed as the minimum likelihood of the roles within that complex (ignoring
        roles not represented in the target search database).

        The likelihoods are stored in a dictionary with the complex ID as the key and
        the likelihood, type, GPR string, list of roles not in the organism, and list of
        roles not in target search database as values.  The type is a string with one
        of the following values:

        CPLX_FULL - All roles found in organism and utilized in the complex
        CPLX_PARTIAL - Only some roles found in organism and only those roles that
            were found were utilized. Note this does not distinguish between not
            there and not represented for roles that were not found
        CPLX_NOTTHERE - Likelihood is 0 because all of the roles are not found in
            the organism
        CPLX_NOREPS - Likelihood is 0 because all of the roles are not represented
            in the target search database
        CPLX_NOREPS_AND_NOTTHERE - Likelihood is 0 because some roles are not found
            in the organism and some roles are not represented in target search database

        Parameters
        ----------
        complexes_to_roles : dict
            Dictionary with complex ID as key and list of role IDs as value
        """

        if len(self._total_role_values) == 0:
            raise ValueError('There are no values in the total role likelihoods dictionary')

        # Build a set of all of the role IDs in the search database (used to distinguish between
        # roles that are unavailable in query organism and roles that have no representatives).
        all_roles = set()
        for feature_id in self._target_rolesets:
            # for role_id in target_roles[feature_id]:
            all_roles.add(self._target_rolesets[feature_id])

        # Iterate over complexes from template model and compute complex probabilities from
        # total role probabilities. Separate out cases where no features seem to exist in the
        # organism for the reaction from cases where there is a database deficiency.
        # See equation 5 in the paper ("Calculating reaction likelihoods" section).
        for complex_id in complexes_to_roles:
            # Determine if the roles for the complex are available in the query organism, are unavailable in the
            # query organism, or do not exist in the search database.
            complex_roles = complexes_to_roles[complex_id]
            avail_roles = list()  # Roles that may have representatives in the query organism
            unavail_roles = list()  # Roles that have representatives in search database but not in query organism
            missing_roles = list()  # Roles with no representatives in search database
            for role in complex_roles:
                if role not in all_roles:
                    missing_roles.append(role)
                elif role not in self._total_role_values:
                    unavail_roles.append(role)
                else:
                    avail_roles.append(role)

            # Add complex to the dictionary.
            self._complex_values[complex_id] = dict()
            self._complex_values[complex_id]['likelihood'] = 0.0
            self._complex_values[complex_id]['type'] = 'UNKNOWN'
            self._complex_values[complex_id]['gpr'] = ''
            self._complex_values[complex_id]['unavail_roles'] = self.separator.join(unavail_roles)
            self._complex_values[complex_id]['missing_roles'] = self.separator.join(missing_roles)

            # Determine the type and GPR string for the complex.
            if len(missing_roles) == len(complex_roles):
                # All of the roles do not exist in the search database.
                self._statistics['complex_types']['num_no_reps'] += 1
                self._complex_values[complex_id]['type'] = 'CPLX_NOREPS'
                continue
            if len(unavail_roles) == len(complex_roles):
                # All of the roles are not in the query organism.
                self._statistics['complex_types']['num_not_there'] += 1
                self._complex_values[complex_id]['type'] = 'CPLX_NOTTHERE'
                continue
            if len(unavail_roles) + len(missing_roles) == len(complex_roles):
                # Some roles do not exist in the search database and the remainder are not in the query organism.
                self._statistics['complex_types']['num_no_reps_and_not_there'] += 1
                self._complex_values[complex_id]['type'] = 'CPLX_NOREPS_AND_NOTTHERE'
                continue
            if len(avail_roles) == len(complex_roles):
                # All of the roles are in the query organism.
                self._statistics['complex_types']['num_full'] += 1
                self._complex_values[complex_id]['type'] = 'CPLX_FULL'
            elif len(avail_roles) < len(complex_roles):
                # Some of the roles are in the query organism.
                self._statistics['complex_types']['num_partial'] += 1
                self._complex_values[complex_id]['type'] = 'CPLX_PARTIAL_{0}_of_{1}' \
                    .format(len(avail_roles), len(complex_roles))

            # Link individual functions in complex with an AND relationship to form a
            # Boolean Gene-Protein relationship.
            gpr_list = [self._total_role_values[role][1] for role in avail_roles]
            gpr_list = list(set(gpr_list))
            if len(gpr_list) > 1:
                self._complex_values[complex_id]['gpr'] = '(' + ' and '.join(gpr_list) + ')'
            elif len(gpr_list) == 1:
                self._complex_values[complex_id]['gpr'] = gpr_list[0]

            # Find the minimum likelihood of the different available roles (ignoring ones
            # that are apparently missing) and call that the complex likelihood.
            min_likelihood = 1000.0
            for role in avail_roles:
                if self._total_role_values[role][0] < min_likelihood:
                    min_likelihood = self._total_role_values[role][0]
            if min_likelihood < 0.0 or min_likelihood > 1.0:
                warn('Complex {0} has invalid likelihood {1:1.6f}'.format(complex_id, min_likelihood))
            self._complex_values[complex_id]['likelihood'] = min_likelihood

        LOGGER.info('Calculated %d complex likelihoods', len(self._complex_values))
        return

    def _calculate_reaction_likelihoods(self, reactions_to_complexes):
        """ Estimate the likelihood of reactions from the likelihood of complexes.

        The reaction likelihood is computed as the maximum likelihood of complexes
        that perform that reaction.

        The likelihoods are stored in a dictionary with the reaction ID as the key
        and the likelihood, type, GPR string, and complex string as values. The
        complex string includes the likelihood and type for the complexes linked to
        the reaction. The type is a string with one of the following values:

        HASCOMPLEXES - Reaction is linked to least one complex
        NOCOMPLEXES - Reaction has no linked complexes

        Parameters
        ----------
        reactions_to_complexes : dict
            Dictionary with reaction ID as key and list of complex IDs as value
        """

        if len(self._complex_values) == 0:
            raise ValueError('There are no values in the complex likelihoods dictionary')

        # Find the maximum likelihood of complexes catalyzing a particular reaction
        # and set that as the reaction likelihood.
        # See equation 6 in the paper ("Calculating reaction likelihoods" section).
        total_likelihood = 0.0
        for reaction_id in reactions_to_complexes:
            # Get details on the complexes linked to the reaction. Each entry in the
            # list is a tuple that contains (1) complex ID, (2) complex likelihood, and
            # (3) complex type.
            complexes = list()
            for complex_id in reactions_to_complexes[reaction_id]:
                if complex_id in self._complex_values:
                    complexes.append([complex_id, self._complex_values[complex_id]['likelihood'],
                                      self._complex_values[complex_id]['type']])

            # Sort the complexes by likelihood to find the maximum likelihood and build
            # the complex string to record details on all of the complexes.
            max_likelihood = 0.0
            complex_string = ''
            if len(complexes) > 0:
                reaction_type = 'HASCOMPLEXES'
                self._statistics['reaction_types']['has_complexes'] += 1
                complexes.sort(key=lambda tup: tup[1], reverse=True)
                max_likelihood = complexes[0][1]  # Complex with maximum likelihood is now the first one in the list
                for complx in complexes:
                    complex_string += '%s (%1.4f; %s)%s' % (complx[0], complx[1], complx[2], self.separator)
                complex_string = complex_string[:-len(self.separator)]  # Remove the final separator
            else:
                # Note this should not happen since only reactions with complexes are included
                # in the reaction_complexes dictionary (leftover from original code).
                reaction_type = 'NOCOMPLEXES'
                self._statistics['reaction_types']['no_complexes'] += 1
            if max_likelihood > 0.0:
                self._statistics['num_nonzero_likelihoods'] += 1
            else:
                self._statistics['num_zero_likelihoods'] += 1
            if max_likelihood < 0.0 or max_likelihood > 1.0:
                warn('Reaction {0} has invalid likelihood {1:1.6f}'.format(reaction_id, max_likelihood))

            # Iterate separately to get a GPR. We want to apply a cutoff here too to avoid
            # a complex with 80% probability being linked by OR to another with a 5%
            # probability.  The same cutoff as is used for which features go with a role
            # is applied here.
            gpr_list = list()
            for complex_id in reactions_to_complexes[reaction_id]:
                if complex_id in self._complex_values:
                    if self._complex_values[complex_id]['likelihood'] < max_likelihood * self._dilution_percent:
                        continue
                    if len(self._complex_values[complex_id]['gpr']) > 0:
                        gpr_list.append(self._complex_values[complex_id]['gpr'])
            if len(gpr_list) == 0:
                gpr = ''
            else:
                gpr = ' or '.join(list(set(gpr_list)))

            # Add the reaction to the dictionary.
            self._reaction_values[reaction_id] = dict()
            self._reaction_values[reaction_id]['likelihood'] = max_likelihood
            self._reaction_values[reaction_id]['type'] = reaction_type
            self._reaction_values[reaction_id]['gpr'] = gpr
            self._reaction_values[reaction_id]['complex_string'] = complex_string
            total_likelihood += max_likelihood

        self._statistics['average_likelihood'] = total_likelihood / float(len(self._reaction_values))
        LOGGER.info('Calculated %d reaction likelihoods with average %f',
                    len(self._reaction_values), self._statistics['average_likelihood'])
        return

    def _save_data(self, genome_id):
        """ Save internal data structures to files for detailed analysis or debug.

        Parameters
        ----------
        genome_id : str
            ID of model
        """

        # Save roleset likelihoods to a file.
        file_name = join(self.work_folder, '{0}.roleset.tsv'.format(genome_id))
        with open(file_name, 'w') as handle:
            handle.write('\t'.join(['Query ID', 'Likelihood', 'Roleset']) + '\n')
            for query_id in sorted(self._roleset_values):
                for value in self._roleset_values[query_id]:
                    handle.write('{0}\t{1:1.6f}\t{2}\n'.format(query_id, value[1], value[0]))

        # Save the role likelihoods to a file.
        file_name = join(self.work_folder, '{0}.role.tsv'.format(genome_id))
        with open(file_name, 'w') as handle:
            handle.write('\t'.join(['Query ID', 'Likelihood', 'Role']) + '\n')
            for value in sorted(self._role_values):
                handle.write('{0}\t{1:1.6f}\t{2}\n'.format(value[0], value[2], value[1]))

        # Save the total role likelihoods to a file.
        file_name = join(self.work_folder, '{0}.totalrole.tsv'.format(genome_id))
        with open(file_name, 'w') as handle:
            handle.write('\t'.join(['Role', 'Likelihood', 'GPR']) + '\n')
            for role in sorted(self._total_role_values):
                value = self._total_role_values[role]
                handle.write('{0}\t{1:1.6f}\t{2}\n'.format(role, value[0], value[1]))

        # Save the complex likelihoods to a file.
        file_name = join(self.work_folder, '{0}.complex.tsv'.format(genome_id))
        with open(file_name, 'w') as handle:
            handle.write(
                '\t'.join(['Complex ID', 'Likelihood', 'Type', 'GPR', 'Unavailable Roles', 'Missing Roles']) + '\n')
            for complex_id in sorted(self._complex_values):
                value = self._complex_values[complex_id]
                handle.write('{0}\t{1:1.6f}\t{2}\t{3}\t{4}\t{5}\n'
                             .format(complex_id, value['likelihood'], value['type'], value['gpr'],
                                     value['unavail_roles'], value['missing_roles']))

        # Save the reaction likelihoods to a file.
        file_name = join(self.work_folder, '{0}.reaction.tsv'.format(genome_id))
        with open(file_name, 'w') as handle:
            handle.write('\t'.join(['Reaction ID', 'Likelihood', 'Type', 'Complexes', 'GPR']) + '\n')
            for reaction_id in sorted(self._reaction_values):
                value = self._reaction_values[reaction_id]
                handle.write('{0}\t{1:1.6f}\t{2}\t{3}\t{4}\n'
                             .format(reaction_id, value['likelihood'], value['type'],
                                     value['complex_string'], value['gpr']))

        return


def download_data_files(fid_role_path, protein_sequence_path, search_db_path, search_program_path,
                        force=False, source_folder_reference='/mmundy/public/modelsupport'):
    """ Download the data files required to calculate reaction likelihoods.

    Calculating reaction likelihoods requires two data files: (1) a target feature
    ID to role ID mapping file, and (2) a fasta file of protein sequences for
    the target feature IDs which is used to build to a search database.

    Parameters
    ----------
    fid_role_path : str
        Path to feature ID to role ID mapping file
    protein_sequence_path : str
        Path to protein sequence file
    search_db_path : str
        Path to search database file
    search_program_path : str
        Path to search program executable
    force : bool, optional
        When True, always download files from workspace
    source_folder_reference : str, optional
        Workspace reference to folder containing data files
    """

    # Download the target feature ID to role ID mapping file.
    if force or not exists(fid_role_path):
        data = get_workspace_object_data(join(source_folder_reference, fid_role_file_name), json_data=False)
        with open(fid_role_path, 'w') as handle:
            handle.write(data)

    # Download the fasta file of protein sequences.
    if force or not exists(protein_sequence_path):
        data = get_workspace_object_data(join(source_folder_reference, protein_sequence_file_name), json_data=False)
        with open(protein_sequence_path, 'w') as handle:
            handle.write(data)

    # Build the command based on the specified search program.
    if 'usearch' in search_program_path.lower():
        args = [search_program_path,
                '-makeudb_ublast',
                protein_sequence_path,
                '-output', search_db_path]
    elif 'blast' in search_program_path.lower():  # mkblastdb
        args = [search_program_path,
                '-in', protein_sequence_path,
                '-dbtype prot']
    else:
        raise ValueError('Search program {0} is not supported, use either usearch or mkblastdb')

    # Run the command to compile the database from the protein fasta file.
    cmd = ' '.join(args)
    try:
        proc = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        (stdout, stderr) = proc.communicate()
        if proc.returncode < 0:
            raise LikelihoodError('"%s" was terminated by signal %d' % (cmd, -proc.returncode))
        else:
            if proc.returncode > 0:
                details = '"%s" failed with return code %d:\nCommand: "%s"\nStdout: "%s"\nStderr: "%s"' \
                          % (args[0], proc.returncode, cmd, stdout, stderr)
                raise LikelihoodError(details)
    except OSError as e:
        warn('Failed to run "%s": %s' % (cmd, e.strerror))
        raise

    return
