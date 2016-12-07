import pytest

import modelseed


@pytest.mark.usefixtures('authenticate')
@pytest.fixture(scope='module')
def test_model(b_theta_id):
    # Reconstruct a model so there is a folder in the workspace.
    stats = modelseed.reconstruct_modelseed_model(b_theta_id)
    yield stats
    modelseed.delete_modelseed_model(b_theta_id)


class TestWorkspace:

    # Remember these tests are calling a server and can take a while depending on the network
    # and how busy the server is servicing other requests.

    def test_list_objects(self, test_model):
        output = modelseed.list_workspace_objects(test_model['ref'])
        assert len(output) == 8
        assert len(output[0]) == 12

    def test_list_objects_by_name(self, test_model):
        output = modelseed.list_workspace_objects(test_model['ref'], sort_key='name')
        assert len(output) == 8
        assert output[0][0] == '{0}.cpdtbl'.format(test_model['id'])

    def test_list_objects_by_type(self, test_model):
        output = modelseed.list_workspace_objects(test_model['ref'], sort_key='type')
        assert len(output) == 8
        assert output[0][0] == 'fba'

    def test_list_objects_bad_folder(self):
        # This fails because there is no leading forward slash.
        bad_reference = '{0}/modelseed/badref'.format(modelseed.workspace.ws_client.username)
        with pytest.raises(modelseed.SeedClient.ObjectNotFoundError):
            modelseed.list_workspace_objects(bad_reference)

    def test_list_objects_no_exist_folder(self):
        no_exist_reference = '/{0}/modelseed/badref'.format(modelseed.workspace.ws_client.username)
        output = modelseed.list_workspace_objects(no_exist_reference)
        assert output is None

    def test_list_objects_bad_sort_key(self, test_model):
        with pytest.raises(ValueError):
            modelseed.list_workspace_objects(test_model['ref'], sort_key='foobar')

    def test_get_object_meta(self, test_model):
        output = modelseed.get_workspace_object_meta(test_model['ref'])
        assert len(output) == 12
        assert output[0] == test_model['id']
        assert output[1] == 'modelfolder'
        assert output[8]['is_folder'] == 1

    def test_get_object_meta_bad_ref(self):
        bad_reference = '{0}/modelseed/badref'.format(modelseed.workspace.ws_client.username)
        with pytest.raises(modelseed.SeedClient.ObjectNotFoundError):
            modelseed.get_workspace_object_meta(bad_reference)

    def test_get_object_data_json(self, test_model):
        reference = '{0}/model'.format(test_model['ref'])
        output = modelseed.get_workspace_object_data(reference)
        assert output['id'] == test_model['id']
        assert len(output['modelcompartments']) == 2
        assert 'modelcompounds' in output
        assert 'modelreactions' in output

    def test_get_object_data_text(self, test_model):
        reference = '{0}/{1}.rxntbl'.format(test_model['ref'], test_model['id'])
        output = modelseed.get_workspace_object_data(reference, json_data=False)
        assert len(output) > 100000  # Just a really long string

    def test_get_object_data_bad_ref(self):
        bad_reference = '{0}/modelseed/badref'.format(modelseed.workspace.ws_client.username)
        with pytest.raises(modelseed.SeedClient.ObjectNotFoundError):
            modelseed.get_workspace_object_data(bad_reference)
