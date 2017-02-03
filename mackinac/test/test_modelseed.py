import pytest

import mackinac


@pytest.mark.usefixtures('authenticate')
class TestModelseedBacteroidesThetaiotaomicron:

    # Remember these tests are calling a server and can take a while depending on the network
    # and how busy the server is servicing other requests.

    def test_reconstruct(self, b_theta_genome_id, b_theta_id, b_theta_name):
        stats = mackinac.reconstruct_modelseed_model(b_theta_genome_id, model_id=b_theta_id)
        assert stats['id'] == b_theta_id
        assert stats['name'] == b_theta_name
        assert stats['num_compartments'] == 2
        assert stats['num_genes'] == 739
        assert stats['num_biomass_compounds'] == 85
        assert stats['source'] == 'ModelSEED'

    def test_gapfill(self, b_theta_id, b_theta_name):
        stats = mackinac.gapfill_modelseed_model(b_theta_id, b_theta_name)
        assert stats['id'] == b_theta_id
        assert stats['integrated_gapfills'] == 1
        assert stats['gapfilled_reactions'] == 0  # Server bug causes value to never be updated
        assert stats['id'] == b_theta_id
        assert stats['name'] == b_theta_name
        assert stats['num_compartments'] == 2

    def test_optimize(self, b_theta_id):
        objective = mackinac.optimize_modelseed_model(b_theta_id)
        assert objective == pytest.approx(99.9203)

    def test_get_model_stats(self, b_theta_id, b_theta_name):
        stats = mackinac.get_modelseed_model_stats(b_theta_id)
        assert stats['id'] == b_theta_id
        assert stats['name'] == b_theta_name
        assert stats['num_compartments'] == 2
        assert stats['num_genes'] == 739
        assert stats['integrated_gapfills'] == 1
        assert stats['unintegrated_gapfills'] == 0
        assert stats['gapfilled_reactions'] == 0   # Server bug causes value to never be updated
        assert stats['ref'] == '/{0}/modelseed/{1}'.format(mackinac.modelseed.ms_client.username, b_theta_id)
        assert stats['genome_ref'] == '/{0}/modelseed/{1}/genome'.format(mackinac.modelseed.ms_client.username, b_theta_id)

    def test_get_model_data(self, b_theta_id):
        data = mackinac.get_modelseed_model_data(b_theta_id)
        assert data['id'] == b_theta_id
        assert len(data['modelreactions']) > 1000
        assert len(data['modelcompounds']) > 1000
        assert len(data['modelcompartments']) == 2
        assert len(data['gapfillings']) == 1
        assert data['gapfillings'][0]['id'] == 'gf.0'

    def test_get_gapfill_solutions(self, b_theta_id):
        solutions = mackinac.get_modelseed_gapfill_solutions(b_theta_id)
        assert len(solutions) == 1
        assert len(solutions[0]['reactions']) > 50
        assert solutions[0]['id'] == 'gf.0'

    def test_get_fba_solutions(self, b_theta_id):
        solutions = mackinac.get_modelseed_fba_solutions(b_theta_id)
        assert len(solutions) == 1
        assert len(solutions[0]['reactions']) > 1000
        assert len(solutions[0]['exchanges']) > 50
        assert solutions[0]['id'] == 'fba.0'
        assert solutions[0]['objective_function'] == 'Max bio1'

    def test_list_models(self, b_theta_id, b_theta_name):
        output = mackinac.list_modelseed_models()
        assert len(output) > 1
        found = False
        for meta in output:
            if meta['id'] == b_theta_id:
                found = True
            assert output[0]['name'] == b_theta_name
            assert output[0]['ref'] == '/{0}/modelseed/{1}'.format(mackinac.modelseed.ms_client.username, b_theta_id)
        assert found == True

    def test_create_cobra_model(self, b_theta_id, b_theta_name):
        model = mackinac.create_cobra_model_from_modelseed_model(b_theta_id)
        assert model.id == b_theta_id
        assert model.name == b_theta_name
        assert len(model.reactions) > 1000
        assert len(model.metabolites) > 1000
        assert len(model.compartments) == 2
        solution = model.optimize()
        assert solution.f > 170.

    def test_delete_model(self, b_theta_id):
        mackinac.delete_modelseed_model(b_theta_id)
