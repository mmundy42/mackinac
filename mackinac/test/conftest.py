import pytest
import os
from os.path import expanduser, join, abspath, dirname, exists
import mackinac


@pytest.fixture(scope='session')
def data_folder():
    return join(expanduser('~'), 'mackinac_data')


@pytest.fixture(scope='session')
def work_folder():
    return join(expanduser('~'), 'mackinac_work')


@pytest.fixture(scope='session')
def search_program_path():
    return join(expanduser('~'), 'Applications', 'usearch')


@pytest.fixture(scope='session')
def authenticate():
    # Get a token for authenticating to the services.
    try:
        username = os.environ['TEST_USERNAME']
    except KeyError:
        raise KeyError('You must set TEST_USERNAME environment variable to run this test')
    try:
        password = os.environ['TEST_PASSWORD']
    except KeyError:
        raise KeyError('You must set TEST_PASSWORD environment variable to run this test')
    mackinac.get_token(username, password=password)


@pytest.fixture(scope='session')
def download_data(data_folder, work_folder, search_program_path):
    if not exists(data_folder):
        os.makedirs(data_folder)
    if not exists(work_folder):
        os.makedirs(work_folder)
    fid_role_path = join(data_folder, 'otu_fid_role.tsv')
    protein_sequence_path = join(data_folder, 'protein.fasta')
    search_db_path = join(data_folder, 'protein.udb')
    mackinac.download_data_files(fid_role_path, protein_sequence_path, search_db_path, search_program_path)


@pytest.fixture(scope='session')
def b_theta_genome_id():
    # PATRIC genome ID for Bacteroides thetaiotaomicron VPI-5482
    return '226186.12'


@pytest.fixture(scope='session')
def b_theta_id():
    return 'Btheta-pytest'


@pytest.fixture(scope='session')
def b_theta_name():
    return 'Bacteroides thetaiotaomicron VPI-5482'


@pytest.fixture(scope='session')
def fid_role_path(data_folder):
    return join(data_folder, 'otu_fid_role.tsv')


@pytest.fixture(scope='session')
def search_db_path(data_folder):
    return join(data_folder, 'protein.udb')


@pytest.fixture(scope='session')
def modelseed_data_folder():
    mackinac_folder = abspath(join(dirname(abspath(__file__)), '..'))
    return join(mackinac_folder, 'data', 'modelseed')


@pytest.fixture(scope='session')
def universal_folder(modelseed_data_folder):
    return join(modelseed_data_folder, 'universal')


@pytest.fixture(scope='session')
def bacteria_folder(modelseed_data_folder):
    return join(modelseed_data_folder, 'bacteria')


@pytest.fixture(scope='session')
def original_folder(modelseed_data_folder):
    return join(modelseed_data_folder, 'original')


@pytest.fixture(scope='session')
def b_theta_features(b_theta_genome_id):
    return mackinac.get_genome_features(b_theta_genome_id)


@pytest.fixture(scope='session')
def b_theta_summary(b_theta_genome_id):
    return mackinac.get_genome_summary(b_theta_genome_id)
