import pytest
from os.path import join

import mackinac

@pytest.mark.fixtures('download_data')
class TestReconstruct:

    def test_reconstruct_features(self, universal_folder, bacteria_folder, b_theta_features,
                                  b_theta_summary, b_theta_id):
        template = mackinac.create_template_model(
            universal_folder,
            bacteria_folder,
            'bacteria',
            'Bacteria template')
        model = mackinac.reconstruct_model_from_features(
            b_theta_features,
            template,
            b_theta_id,
            'negbio',
            gc_content=b_theta_summary['gc_content'] / 100.0
        )
        assert model.id == b_theta_id
        assert len(model.reactions) == 923  # Value can change if genome annotation changes
        assert len(model.metabolites) == 999  # Value can change if genome annotation changes
        assert len(model.compartments) == 2

    def test_reconstruct_likelihoods(self, universal_folder, bacteria_folder, b_theta_features,
                                     b_theta_summary, b_theta_id, search_program_path,
                                     search_db_path, fid_role_path, work_folder):
        template = mackinac.create_template_model(
            universal_folder,
            bacteria_folder,
            'bacteria',
            'Bacteria template')
        likelihoods = mackinac.calculate_likelihoods(
            b_theta_id,
            b_theta_features,
            template,
            search_program_path=search_program_path,
            search_db_path=search_db_path,
            fid_role_path=fid_role_path,
            work_folder=work_folder)
        assert len(likelihoods.reaction_values) == 5652
        assert likelihoods.reaction_values['rxn00006']['likelihood'] == 0.0
        assert pytest.approx(likelihoods.reaction_values['rxn14380']['likelihood'], 0.9594912486067599)
        model = mackinac.reconstruct_model_from_likelihoods(
            likelihoods,
            template,
            b_theta_id,
            'negbio',
            gc_content=b_theta_summary['gc_content'] / 100.0
        )
        assert model.id == b_theta_id
        assert len(model.reactions) == 1164  # Value can change if genome annotation changes
        assert len(model.metabolites) == 1260  # Value can change if genome annotation changes
        assert len(model.compartments) == 2
