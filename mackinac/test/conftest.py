import pytest
import os
from os.path import expanduser, join

import mackinac


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
def data_folder():
    return join(expanduser('~'), 'mackinac_data')


@pytest.fixture(scope='session')
def work_folder():
    return join(expanduser('~'), 'mackinac_work')


@pytest.fixture(scope='session')
def search_program_path():
    return join(expanduser('~'), 'Applications', 'usearch')
