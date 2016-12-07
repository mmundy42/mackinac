from os.path import join
import requests

# PATRIC service endpoint
patric_url = 'https://www.patricbrc.org/api/'


def get_genome_summary(genome_id):
    """ Get the summary data for a genome in PATRIC.

    Parameters
    ----------
    genome_id : str
        Genome ID of genome available in PATRIC

    Returns
    -------
    dict
        Summary data for genome (keys vary based on available data)
    """

    headers = {'accept': 'application/json'}
    genome_url = join(patric_url, 'genome', genome_id)
    response = requests.get(genome_url, headers=headers, verify=True)
    if response.status_code != requests.codes.OK:
        if response.status_code == 404:
            raise ValueError('Genome ID {0} not found in PATRIC'.format(genome_id))
        response.raise_for_status()
    return response.json()


def get_genome_features(genome_id, annotation='PATRIC'):
    """ Get the list of features from the genome annotation.

    Parameters
    ----------
    genome_id: str
        Genome ID of genome available in PATRIC
    annotation : {'patric', 'refseq'}, optional
        Type of annotation

    Returns
    -------
    list
        List of features (each entry is a dict with keys that vary based on available data)
    """

    if annotation != 'PATRIC' and annotation != 'RefSeq':
        raise ValueError('Annotation must be either "PATRIC" or "RefSeq"')

    # Construct a SOLR query to get the features.
    headers = {
        'content-type': 'application/solrquery+x-www-form-urlencoded',
        'accept': 'application/solr+json'
    }
    feature_url = join(patric_url, 'genome_feature/')  # + '/'
    query = dict()
    query['q'] = 'genome_id:' + genome_id
    query['rows'] = '10000'
    query['start'] = 0

    # Get all of the features for the genome.
    features = list()
    done = False
    count = 0
    while not done:
        # Run the SOLR query to get the next set of features.
        response = requests.get(feature_url, params=query, headers=headers, verify=True)
        if response.status_code != requests.codes.OK:
            response.raise_for_status()
        feature_data = response.json()
        if feature_data['response']['numFound'] == 0:
            raise ValueError('No features found for genome {0}'.format(genome_id))

        # For each feature from the specified annotation, add it to the list of features in the genome.
        for index in range(len(feature_data['response']['docs'])):
            data = feature_data['response']['docs'][index]
            if data['feature_type'] != 'source' and data['annotation'] == annotation:
                features.append(data)

        # Did we get all of the features yet?
        count += len(feature_data['response']['docs'])
        if count >= feature_data['response']['numFound']:
            done = True
        else:
            query['start'] += len(feature_data['response']['docs'])

    return features
