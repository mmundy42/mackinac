from os.path import join
import numpy as np

import mackinac


class TestLikelihood:

    def test_download(self, data_folder, search_program_path):
        fid_role_path = join(data_folder, 'otu_fid_role.tsv')
        protein_sequence_path = join(data_folder, 'protein.fasta')
        search_db_path = join(data_folder, 'protein.udb')
        mackinac.download_data_files(fid_role_path, protein_sequence_path, search_db_path, search_program_path)

    def test_calculate(self, data_folder, search_program_path, work_folder,
                       b_theta_genome_id, b_theta_id, b_theta_name):
        fid_role_path = join(data_folder, 'otu_fid_role.tsv')
        search_db_path = join(data_folder, 'protein.udb')
        stats = mackinac.create_patric_model(b_theta_genome_id, model_id=b_theta_id)
        assert stats['id'] == b_theta_id
        assert stats['name'] == b_theta_name
        likelihoods = mackinac.calculate_patric_likelihoods(b_theta_id, search_program_path, search_db_path,
                                                            fid_role_path, work_folder)
        assert len(likelihoods) == 6160
        assert likelihoods['rxn00006_c']['likelihood'] == 0.0
        assert np.isclose(likelihoods['rxn14380_c']['likelihood'], 0.9594912486067599)
