import pytest

import mackinac


class TestGenomeBacteroidesThetaiotaomicron:

    def test_get_summary(self, b_theta_genome_id, b_theta_name):
        summary = mackinac.get_genome_summary(b_theta_genome_id)
        assert summary['genome_id'] == b_theta_genome_id
        assert summary['organism_name'] == b_theta_name
        assert summary['cell_shape'] == 'Rod'
        assert summary['gram_stain'] == '-'
        assert summary['gc_content'] == 42.9
        assert summary['genome_length'] == 6293399

    def test_get_summary_bad_id(self):
        with pytest.raises(ValueError):
            mackinac.get_genome_summary('900.900')

    def test_get_features_patric(self, b_theta_genome_id):
        features = mackinac.get_genome_features(b_theta_genome_id)
        assert len(features) == 4965
        assert 'na_length' in features[0]
        assert 'na_sequence' in features[0]
        assert 'feature_type' in features[0]
        assert features[0]['patric_id'].startswith('fig|{0}'.format(b_theta_genome_id))

    def test_get_features_refseq(self, b_theta_genome_id):
        features = mackinac.get_genome_features(b_theta_genome_id, annotation='RefSeq')
        assert len(features) == 4902
        assert 'na_length' in features[0]
        assert 'na_sequence' in features[0]
        assert 'feature_type' in features[0]
        assert features[0]['feature_id'].startswith('RefSeq.{0}'.format(b_theta_genome_id))

    def test_get_features_bad_id(self):
        with pytest.raises(ValueError):
            mackinac.get_genome_features('900.900')

    def test_get_features_bad_annotation(self, b_theta_genome_id):
        with pytest.raises(ValueError):
            mackinac.get_genome_features(b_theta_genome_id, annotation='foobar')
