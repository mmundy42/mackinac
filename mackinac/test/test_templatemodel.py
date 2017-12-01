import pytest
from os.path import join, exists

import mackinac


class TestTemplateModel:

    def test_reconstruct_bacteria(self, universal_folder, bacteria_folder):
        template = mackinac.create_template_model(
            universal_folder,
            bacteria_folder,
            'bacteria',
            'Bacteria template')
        assert len(template.reactions) == 20329
        assert len(template.metabolites) == 15172
        assert len(template.compartments) == 2
        assert len(template.complexes) == 4353
        assert len(template.roles) == 4656
        assert len(template.biomasses) == 2

    def test_reconstruct_original(self, universal_folder, original_folder):
        template = mackinac.create_template_model(
            universal_folder,
            original_folder,
            'bacteria',
            'Bacteria template')
        assert len(template.reactions) == 8663
        assert len(template.metabolites) == 6994
        assert len(template.compartments) == 2
        assert len(template.complexes) == 4895
        assert len(template.roles) == 5002
        assert len(template.biomasses) == 2

    def test_to_model(self, universal_folder, bacteria_folder):
        template = mackinac.create_template_model(
            universal_folder,
            bacteria_folder,
            'bacteria',
            'Bacteria template')
        model = template.to_cobra_model()
        assert len(model.reactions) == 22163
        assert len(model.metabolites) == 15071

    def test_to_list_file(self, universal_folder, bacteria_folder, work_folder):
        template = mackinac.create_template_model(
            universal_folder,
            bacteria_folder,
            'bacteria',
            'Bacteria template')
        output_file_name = join(work_folder, 'reactions.txt')
        template.to_reaction_list_file(output_file_name)
        assert exists(output_file_name)

    def test_bad_universal_folder(self, bacteria_folder):
        with pytest.raises(IOError):
            template = mackinac.create_template_model(
                './BAD_folder',
                bacteria_folder,
                'bacteria',
                'Bacteria template')

    def test_bad_template_folder(self, universal_folder):
        with pytest.raises(IOError):
            template = mackinac.create_template_model(
                universal_folder,
                './BAD_folder',
                'bacteria',
                'Bacteria template')
