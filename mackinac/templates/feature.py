import re
from collections import defaultdict

from cobra.core import Object, DictList

from .util import make_search_name, ec_number_re
from ..modelutil import patric_gene_prefix_re
from ..logger import LOGGER


# Regular expression to remove special characters from feature IDs because
# they cause confusion in cobra.core.DictList objects.
# @todo Also remove anything before the | character?
special_chars_re = re.compile(r'\|')

# Regular expression to split a function into roles.
# @todo Confirm roles with / are being split as expected
delimiter_re = re.compile(r'\s*;\s+|\s+[@/]\s+')

# Dictionary of regular expressions for searching for compartment names in functions.
# The key is a regular expression for matching keywords and the value is the
# compartment ID.
compartment_search = {
    'cytosolic': 'c',
    'plastidial': 'd',
    'mitochondrial': 'm',
    'peroxisomal': 'x',
    'lysosomal': 'l',
    'vacuolar': 'v',
    'nuclear': 'n',
    'plasma\smembrane': 'p',
    'cell\swall': 'w',
    'golgi\sapparatus': 'g',
    'endoplasmic\sreticulum': 'r',
    'extracellular': 'e',
    'cellwall': 'w',
    'periplasm': 'p',
    'cytosol': 'c',
    'golgi': 'g',
    'endoplasm': 'r',
    'lysosome': 'l',
    'nucleus': 'n',
    'chloroplast': 'h',
    'mitochondria': 'm',
    'peroxisome': 'x',
    'vacuole': 'v',
    'plastid': 'd',
    'unknown': 'u'
}


class Feature(Object):
    """ Feature of a genome.

    A feature (sometimes also called a gene) is a part of a genome that is of special
    interest. Features may be spread across multiple DNA sequences (contigs) of a
    genome, but never across more than one genome. Normally a Feature is just a single
    contiguous region on a contig. Features have types, and an appropriate choice of
    available types allows the support of protein-encoding genes, exons, RNA genes,
    binding sites, pathogenicity islands, or whatever.
    
    Parameters
    ----------
    id : str
        ID of feature
    function : str
        Function of the feature
        
    Attributes
    ----------
    comment : str
        Comment part of function which is used to identify compartments
    compartments : list of str
        Compartments of cell where function is active
    roles : list of str
        List of functional roles associated with feature
    search_roles : list of str
        List of functional roles modified for better string matching
    ec_numbers : list of str
        List of EC numbers found in the functional role strings
    """

    def __init__(self, id, function):
        Object.__init__(self, re.sub(patric_gene_prefix_re, '', id))
        self.function = function
        self.comment = 'none'
        self.compartments = ['u']  # Default is unknown compartment

        # Extract comments from the function and save the comments separately.
        # Anything after the first # character is considered a comment.
        parts = self.function.split('#')
        self.function = parts[0].strip()
        self.compartments = ['u']  # Default is unknown compartment

        # Search the comments for keywords that identify the compartments.
        if len(parts) > 1:
            self.comment = '#'.join(parts[1:])
            found_compartments = set()
            for key in compartment_search:
                # Key is a regular expression for search
                if re.search(compartment_search[key], self.comment):
                    found_compartments.add(compartment_search[key])

            if len(found_compartments) > 0:
                self.compartments = list(found_compartments)

        # Split the function into roles if there is a delimiter with whitespace
        # and make a search name for each role.
        self.roles = re.split(delimiter_re, self.function)
        self.search_roles = [make_search_name(role) for role in self.roles]

        # Find all of the EC numbers in all of the roles.
        self.ec_numbers = list()
        for role in self.roles:
            self.ec_numbers.extend(re.findall(ec_number_re, role))
        return


def create_features_from_patric(genome_features):
    """ Create Feature objects for all of the features in a PATRIC genome annotation.

    Use the get_genome_features() function to download a genome annotation.
    
    Parameters
    ----------
    genome_features : list of dict
        List of genome features where each entry is a dict with keys that vary
        based on available data. To create Feature objects from the genome annotation
        the 'patric_id' key is used for the feature ID parameter and the 'product'
        key is used for the function parameter. All other keys are ignored.
        
    Returns
    -------
    cobra.core.DictList
        List of Feature objects created from genome features
    dict
        Statistics about genome features
    """

    LOGGER.info('Started creating Feature objects from %d features', len(genome_features))
    stats = defaultdict(int)
    stats['num_genome_feature'] = len(genome_features)
    feature_list = DictList()
    for index in range(len(genome_features)):
        try:
            feature = Feature(genome_features[index]['patric_id'], genome_features[index]['product'])
        except KeyError:
            continue
        feature_list.append(feature)
        stats['num_product'] += 1
        if len(feature.ec_numbers) > 1:
            stats['num_multiple_ec_num'] += 1
        if len(feature.roles) > 1:
            stats['num_multiple_role'] += 1
    LOGGER.info('Finished creating %d Feature objects', len(feature_list))

    return feature_list, stats
