import pytest
from os.path import join

import mackinac
from mackinac.SeedClient import ObjectNotFoundError


@pytest.mark.usefixtures('authenticate', 'download_data')
class TestPatricBacteroidesThetaiotaomicron:

    # Remember these tests are calling a server and can take a while depending on the network
    # and how busy the server is servicing other requests.

    def test_patric_service(self):
        assert mackinac.check_patric_app_service() is True
        app_list = mackinac.list_patric_apps()
        assert len(app_list) >= 18

    def test_create_patric_model(self, b_theta_genome_id, b_theta_id, b_theta_name):
        stats = mackinac.create_patric_model(b_theta_genome_id, model_id=b_theta_id)
        assert stats['id'] == b_theta_id
        assert stats['name'] == b_theta_name
        assert stats['num_compartments'] == 2
        assert stats['num_genes'] > 700  # Value can change if genome annotation changes
        assert stats['num_biomass_compounds'] == 85
        assert stats['source'] == 'PATRIC'

    def test_get_model_stats(self, b_theta_id, b_theta_name):
        stats = mackinac.get_patric_model_stats(b_theta_id)
        assert stats['id'] == b_theta_id
        assert stats['name'] == b_theta_name
        assert stats['num_compartments'] == 2
        assert stats['num_genes'] > 700  # Value can change if genome annotation changes
        assert stats['integrated_gapfills'] == 1
        assert stats['unintegrated_gapfills'] == 0
        assert stats['gapfilled_reactions'] > 100  # Value can change if genome annotation changes
        model_reference = '/{0}/home/models/.{1}'.format(mackinac.patric.patric_client.username, b_theta_id)
        assert stats['ref'] == model_reference
        assert stats['genome_ref'] == '{0}/genome'.format(model_reference, b_theta_id)

    def test_get_model_data(self, b_theta_id):
        data = mackinac.get_patric_model_data(b_theta_id)
        assert data['id'] == '.' + b_theta_id
        assert len(data['modelreactions']) > 1000
        assert len(data['modelcompounds']) > 1000
        assert len(data['modelcompartments']) == 2
        assert len(data['gapfillings']) == 1
        assert data['gapfillings'][0]['id'] == 'gf.0'

    def test_get_gapfill_solutions(self, b_theta_id):
        solutions = mackinac.get_patric_gapfill_solutions(b_theta_id)
        assert len(solutions) == 1
        assert len(solutions[0]['reactions']) > 50  # Value can change if genome annotation changes
        assert solutions[0]['id'] == 'gf.0'

    def test_get_fba_solutions(self, b_theta_id):
        solutions = mackinac.get_patric_fba_solutions(b_theta_id)
        assert len(solutions) == 1
        assert len(solutions[0]['reactions']) > 1000  # Value can change if genome annotation changes
        assert len(solutions[0]['exchanges']) > 50  # Value can change if genome annotation changes
        assert solutions[0]['id'] == 'fba.0'
        assert solutions[0]['objective_function'] == 'Max bio1'

    def test_list_models(self, b_theta_id, b_theta_name):
        output = mackinac.list_patric_models()
        assert len(output) >= 1
        found = False
        for meta in output:
            if meta['id'] == b_theta_id:
                found = True
                assert meta['name'] == b_theta_name
                assert meta['ref'] == '/{0}/home/models/.{1}'.format(mackinac.patric.patric_client.username, b_theta_id)
        assert found is True

    def test_create_cobra_model(self, b_theta_id, b_theta_name):
        model = mackinac.create_cobra_model_from_patric_model(b_theta_id)
        assert model.id == b_theta_id
        assert model.name == b_theta_name
        assert len(model.reactions) > 1100  # Value can change if genome annotation changes
        assert len(model.metabolites) > 1200  # Value can change if genome annotation changes
        assert len(model.compartments) == 2
        solution = model.optimize()
        assert solution.f > 180.  # Value can change if genome annotation changes

    def test_calculate_likelihoods(self, b_theta_id, data_folder, search_program_path, work_folder):
        fid_role_path = join(data_folder, 'otu_fid_role.tsv')
        search_db_path = join(data_folder, 'protein.udb')
        likelihoods = mackinac.calculate_patric_likelihoods(b_theta_id, search_program_path, search_db_path,
                                                            fid_role_path, work_folder)
        assert len(likelihoods) == 6160
        assert likelihoods['rxn00006_c']['likelihood'] == 0.0
        assert pytest.approx(likelihoods['rxn14380_c']['likelihood'], 0.9594912486067599)

    def test_not_found_media(self, b_theta_genome_id, b_theta_id):
        bad_media = '/chenry/public/modelsupport/media/BadMedia'

        with pytest.raises(ObjectNotFoundError):
            mackinac.create_patric_model(b_theta_genome_id, b_theta_id, media_reference=bad_media)

    def test_not_found_model(self, data_folder, search_program_path, work_folder):
        bad_id = 'BadModel'

        with pytest.raises(ObjectNotFoundError):
            fid_role_path = join(data_folder, 'otu_fid_role.tsv')
            search_db_path = join(data_folder, 'protein.udb')
            mackinac.calculate_patric_likelihoods(bad_id, search_program_path, search_db_path,
                                                  fid_role_path, work_folder)

        with pytest.raises(ObjectNotFoundError):
            mackinac.create_cobra_model_from_patric_model(bad_id)

        with pytest.raises(ObjectNotFoundError):
            mackinac.delete_patric_model(bad_id)

        with pytest.raises(ObjectNotFoundError):
            mackinac.get_patric_fba_solutions(bad_id)

        with pytest.raises(ObjectNotFoundError):
            mackinac.get_patric_gapfill_solutions(bad_id)

        with pytest.raises(ObjectNotFoundError):
            mackinac.get_patric_model_data(bad_id)

        with pytest.raises(ObjectNotFoundError):
            mackinac.get_patric_model_stats(bad_id)

    def test_bad_genome_id(self):
        with pytest.raises(ValueError):
            mackinac.create_patric_model('900.900', 'BadModel')

    def test_bad_sort_key(self):
        with pytest.raises(KeyError):
            mackinac.list_patric_models(sort_key='banana')

    def test_delete_model(self, b_theta_id):
        mackinac.delete_patric_model(b_theta_id)

    def test_not_found_template_model(self, b_theta_genome_id, b_theta_id):
        bad_template_model = '/chenry/public/modelsupport/templates/BadTemplate'

        with pytest.raises(ObjectNotFoundError):
            mackinac.create_patric_model(b_theta_genome_id, b_theta_id, template_reference=bad_template_model)
