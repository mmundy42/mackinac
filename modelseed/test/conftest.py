import pytest
import os

import modelseed


@pytest.fixture(scope='session')
def authenticate():
    # Get a token for authenticating to the services.
    try:
        username = os.environ['TEST_USERNAME']
    except KeyError as e:
        print('You must set TEST_USERNAME environment variable to run this test')
        raise e
    try:
        password = os.environ['TEST_PASSWORD']
    except KeyError as e:
        print('You must set TEST_PASSWORD environment variable to run this test')
        raise e
    modelseed.get_token(username, password=password)


@pytest.fixture(scope='session')
def b_theta_id():
    # PATRIC genome ID for Bacteroides thetaiotaomicron VPI-5482
    return '226186.12'


@pytest.fixture(scope='session')
def b_theta_name():
    return 'Bacteroides thetaiotaomicron VPI-5482'
