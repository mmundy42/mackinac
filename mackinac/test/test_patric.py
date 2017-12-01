import pytest
from os.path import join

import mackinac


@pytest.mark.usefixtures('authenticate', 'download_data')
class TestPatricBacteroidesThetaiotaomicron:

    # Remember these tests are calling a server and can take a while depending on the network
    # and how busy the server is servicing other requests.

    def test_reconstruct(self, b_theta_genome_id, b_theta_id, b_theta_name):
        stats = mackinac.create_patric_model(b_theta_genome_id, model_id=b_theta_id)
        assert stats['id'] == b_theta_id
        assert stats['name'] == b_theta_name
        assert stats['num_compartments'] == 2
        assert stats['num_genes'] == 727
        assert stats['num_biomass_compounds'] == 85
        assert stats['source'] == 'PATRIC'

    def test_get_model_stats(self, b_theta_id, b_theta_name):
        stats = mackinac.get_patric_model_stats(b_theta_id)
        assert stats['id'] == b_theta_id
        assert stats['name'] == b_theta_name
        assert stats['num_compartments'] == 2
        assert stats['num_genes'] == 727
        assert stats['integrated_gapfills'] == 1
        assert stats['unintegrated_gapfills'] == 0
        assert stats['gapfilled_reactions'] == 107  # Value can change if server changes
        assert stats['ref'] == '/{0}/home/models/.{1}'.format(mackinac.patric.patric_client.username,
                                                              b_theta_id)
        assert stats['genome_ref'] == '/{0}/home/models/.{1}/genome'.format(mackinac.patric.patric_client.username,
                                                                            b_theta_id)

    def test_create_cobra_model(self, b_theta_id, b_theta_name):
        model = mackinac.create_cobra_model_from_patric_model(b_theta_id)
        assert model.id == b_theta_id
        assert model.name == b_theta_name
        assert len(model.reactions) == 1192
        assert len(model.metabolites) == 1249
        assert len(model.compartments) == 2
        solution = model.optimize()
        assert solution.f > 180.

    def test_calculate_likelihoods(self, b_theta_id, data_folder, search_program_path, work_folder):
        fid_role_path = join(data_folder, 'otu_fid_role.tsv')
        search_db_path = join(data_folder, 'protein.udb')
        likelihoods = mackinac.calculate_patric_likelihoods(b_theta_id, search_program_path, search_db_path,
                                                            fid_role_path, work_folder)
        assert len(likelihoods) == 6160
        assert likelihoods['rxn00006_c']['likelihood'] == 0.0
        assert pytest.approx(likelihoods['rxn14380_c']['likelihood'], 0.9594912486067599)

    def test_delete_model(self, b_theta_id):
        mackinac.delete_patric_model(b_theta_id)
