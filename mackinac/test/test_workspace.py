import pytest

import mackinac


@pytest.fixture(scope='module')
def test_model(b_theta_genome_id, b_theta_id):
    # Reconstruct a model so there is a folder in the workspace.
    stats = mackinac.reconstruct_modelseed_model(b_theta_genome_id, model_id=b_theta_id)
    yield stats
    mackinac.delete_modelseed_model(b_theta_id)


@pytest.fixture(scope='module')
def test_file():
    return '/{0}/modelseed/emergency'.format(mackinac.workspace.ws_client.username)


@pytest.fixture(scope='module')
def test_file_data():
    return 'This is a test of the emergency broadcasting system.'


@pytest.fixture(scope='module')
def bad_reference():
    return '/{0}/modelseed/badref'.format(mackinac.workspace.ws_client.username)


@pytest.mark.usefixtures('authenticate')
class TestWorkspace:

    # Remember these tests are calling a server and can take a while depending on the network
    # and how busy the server is servicing other requests.

    def test_list_objects(self, test_model):
        output = mackinac.list_workspace_objects(test_model['ref'])
        assert len(output) == 8
        assert len(output[0]) == 12

    def test_list_objects_by_name(self, test_model):
        output = mackinac.list_workspace_objects(test_model['ref'], sort_key='name')
        assert len(output) == 8
        assert output[0][0] == '{0}.cpdtbl'.format(test_model['id'])

    def test_list_objects_by_type(self, test_model):
        output = mackinac.list_workspace_objects(test_model['ref'], sort_key='type')
        assert len(output) == 8
        assert output[2][1] == 'genome'
        assert output[4][1] == 'model'

    def test_list_objects_bad_folder(self):
        # This fails because there is no leading forward slash.
        bad_reference = '{0}/modelseed/badref'.format(mackinac.workspace.ws_client.username)
        with pytest.raises(mackinac.SeedClient.ObjectNotFoundError):
            mackinac.list_workspace_objects(bad_reference)

    def test_list_objects_no_exist_folder(self):
        no_exist_reference = '/{0}/modelseed/badref'.format(mackinac.workspace.ws_client.username)
        output = mackinac.list_workspace_objects(no_exist_reference)
        assert output is None

    def test_list_objects_bad_sort_key(self, test_model):
        with pytest.raises(ValueError):
            mackinac.list_workspace_objects(test_model['ref'], sort_key='foobar')

    def test_get_object_meta(self, test_model):
        output = mackinac.get_workspace_object_meta(test_model['ref'])
        assert len(output) == 12
        assert output[0] == test_model['id']
        assert output[1] == 'modelfolder'
        assert output[8]['is_folder'] == 1

    def test_get_object_meta_bad_ref(self):
        bad_reference = '{0}/modelseed/badref'.format(mackinac.workspace.ws_client.username)
        with pytest.raises(mackinac.SeedClient.ObjectNotFoundError):
            mackinac.get_workspace_object_meta(bad_reference)

    def test_get_object_data_json(self, test_model):
        reference = '{0}/model'.format(test_model['ref'])
        output = mackinac.get_workspace_object_data(reference)
        assert output['id'] == test_model['id']
        assert len(output['modelcompartments']) == 2
        assert 'modelcompounds' in output
        assert 'modelreactions' in output

    def test_get_object_data_text(self, test_model):
        reference = '{0}/{1}.rxntbl'.format(test_model['ref'], test_model['id'])
        output = mackinac.get_workspace_object_data(reference, json_data=False)
        assert len(output) > 100000  # Just a really long string

    def test_get_object_data_bad_ref(self, bad_reference):
        with pytest.raises(mackinac.SeedClient.ObjectNotFoundError):
            mackinac.get_workspace_object_data(bad_reference)

    def test_put_object_no_data(self, test_file):
        output = mackinac.put_workspace_object(test_file, 'string')
        assert output[0] == 'emergency'
        assert output[1] == 'string'
        assert output[6] == 0
        assert len(output[7]) == 0

    def test_put_object_meta(self, test_file, b_theta_id):
        output = mackinac.put_workspace_object(test_file, 'string', metadata={'model': b_theta_id}, overwrite=True)
        assert output[0] == 'emergency'
        assert output[1] == 'string'
        assert output[6] == 0
        assert len(output[7]) == 1

    def test_put_object_data(self, test_file, test_file_data, b_theta_id):
        output = mackinac.put_workspace_object(test_file, 'string', data=test_file_data,
                                               metadata={'model': b_theta_id}, overwrite=True)
        assert output[0] == 'emergency'
        assert output[1] == 'string'
        assert output[6] == len(test_file_data)
        assert len(output[7]) == 1

    def test_delete_object(self, test_file):
        output = mackinac.delete_workspace_object(test_file)
        assert output[0] == 'emergency'

    def test_delete_object_bad_ref(self, bad_reference):
        with pytest.raises(mackinac.SeedClient.ObjectNotFoundError):
            mackinac.delete_workspace_object(bad_reference)
