import mackinac


class TestTemplateModel:

    def test_reconstruct_negative(self, b_theta_genome_id):
        template = mackinac.templates.create_mackinac_template_model('mackinac/data/modelseed/universal',
                                                                     'mackinac/data/modelseed/bacteria',
                                                                     'bacteria', 'bacteria')
        summary = mackinac.get_genome_summary(b_theta_genome_id)
        features = mackinac.get_genome_features(b_theta_genome_id)
        btheta = template.reconstruct(summary, features, 'negbio')
        assert len(btheta.reactions) == 971
        assert len(btheta.metabolites) == 1027

    def test_to_model(self):
        template = mackinac.templates.create_mackinac_template_model('mackinac/data/modelseed/universal',
                                                                     'mackinac/data/modelseed/bacteria',
                                                                     'bacteria', 'bacteria')
        model = template.to_cobra_model()
        assert len(model.reactions) == 22163
        assert len(model.metabolites) == 15071
