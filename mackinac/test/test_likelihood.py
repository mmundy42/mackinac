from os.path import join

import mackinac


class TestLikelihood:

    def test_download(self, data_folder, search_program_path):
        fid_role_path = join(data_folder, 'otu_fid_role.tsv')
        protein_sequence_path = join(data_folder, 'protein.fasta')
        search_db_path = join(data_folder, 'protein.udb')
        mackinac.download_data_files(fid_role_path, protein_sequence_path, search_db_path, search_program_path)
