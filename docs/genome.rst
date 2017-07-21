
Working with PATRIC genomes
---------------------------

Mackinac provides functions for working with PATRIC genomes.

.. code:: ipython2

    import mackinac

Get summary information for a PATRIC genome with
``get_genome_summary()``. Note that information available in the summary
can be different for different genomes depending on the source of the
genome.

.. code:: ipython2

    mackinac.get_genome_summary('226186.12')




.. parsed-literal::

    {u'_version_': 1552608979212828700,
     u'assembly_accession': u'GCA_000011065.1',
     u'bioproject_accession': u'PRJNA399',
     u'biosample_accession': u'SAMN02604314',
     u'brc1_cds': 0,
     u'cell_shape': u'Rod',
     u'chromosomes': 1,
     u'class': u'Bacteroidia',
     u'comments': [u'Bacteroides thetaiotaomicron strain VPI-5482. This is the type strain for this organism and was isolated from the feces of a healthy adult.'],
     u'common_name': u'Bacteroides_thetaiotaomicron_VPI-5482',
     u'completion_date': u'2003-03-29T00:00:00Z',
     u'contigs': 0,
     u'date_inserted': u'2014-12-08T22:10:24.729Z',
     u'date_modified': u'2015-03-16T03:17:09.594Z',
     u'disease': [u'Peritonitis'],
     u'document_type': u'genome',
     u'family': u'Bacteroidaceae',
     u'gc_content': 42.9,
     u'genbank_accessions': u'AE015928,AY171301',
     u'genome_id': u'226186.12',
     u'genome_length': 6293399,
     u'genome_name': u'Bacteroides thetaiotaomicron VPI-5482',
     u'genome_status': u'Complete',
     u'genus': u'Bacteroides',
     u'gram_stain': u'-',
     u'habitat': u'Host-associated',
     u'isolation_comments': u'isolated from the feces of a healthy adult',
     u'isolation_source': u'the feces of a healthy adult',
     u'kingdom': u'Bacteria',
     u'ncbi_project_id': u'399',
     u'optimal_temperature': u'-',
     u'order': u'Bacteroidales',
     u'organism_name': u'Bacteroides thetaiotaomicron VPI-5482',
     u'owner': u'PATRIC',
     u'oxygen_requirement': u'Anaerobic',
     u'p2_genome_id': 70966,
     u'patric_cds': 4872,
     u'phylum': u'Bacteroidetes',
     u'plasmids': 1,
     u'public': True,
     u'publication': u'12663928,19321416',
     u'reference_genome': u'Reference',
     u'refseq_accessions': u'NC_004663,NC_004703',
     u'refseq_cds': 4816,
     u'refseq_project_id': u'62913',
     u'sequences': 2,
     u'sequencing_centers': u'Genome Sequencing Center (GSC) at Washington University (WashU) School of Medicine',
     u'sequencing_status': u'complete',
     u'species': u'Bacteroides thetaiotaomicron',
     u'strain': u'VPI-5482',
     u'taxon_id': 226186,
     u'taxon_lineage_ids': [u'131567',
      u'2',
      u'1783270',
      u'68336',
      u'976',
      u'200643',
      u'171549',
      u'815',
      u'816',
      u'818',
      u'226186'],
     u'taxon_lineage_names': [u'cellular organisms',
      u'Bacteria',
      u'FCB group',
      u'Bacteroidetes/Chlorobi group',
      u'Bacteroidetes',
      u'Bacteroidia',
      u'Bacteroidales',
      u'Bacteroidaceae',
      u'Bacteroides',
      u'Bacteroides thetaiotaomicron',
      u'Bacteroides thetaiotaomicron VPI-5482'],
     u'temperature_range': u'Mesophilic',
     u'type_strain': u'Yes'}



Get the features for an annotated genome with ``get_genome_features()``.
Both PATRIC and RefSeq annotations are available.

.. code:: ipython2

    features = mackinac.get_genome_features('226186.12', annotation='PATRIC')
    len(features)




.. parsed-literal::

    4965



The returned list has detailed information about each feature including
the type and DNA sequence. If the feature is a coding sequence, the
returned data also includes the amino acid sequence.

.. code:: ipython2

    features[100]




.. parsed-literal::

    {u'aa_length': 695,
     u'aa_sequence': u'MMIRKTLTILAVSCMMYSCGTKTESNPFFTEFQTEYGVPSFDKIKLEHYEPAFLKGIEEQNQNIQAIIASPEVPTFDNTIVALDSSAPILDRVSAIFFNMTDAETTDELTELSIKMAPVLSEHEDNISLNQELFKRVNVVYQQKDSMNLTTEQKRLLDKTYKGFVRSGANLDAEKQARLREINKELSTLGITFSNNILNENNAFQLFVDKKEDLAGLPEWFCQSAAEEAKAAGQPGKWLFTLHNASRLPFLQYAENRPLREKMYKAYINRGNNNDKNDNKETIRKIVSLRLEKARLLGFNNYANFVLDETMSKNDSNVMSLLNNLWSYALPKAKAEAAELQQLMDKEGKGEKLEAWDWWYYTEKLRKEKYNLSEEDTKPYFKLENVREGAFAVANKLYGITLNKLEGIPTYHPDVEVFEVKDADGSQLGIFYVDYFPRSGKSGGAWMSNYREQQGATRPLVCNVCSFTKPVGDTPSLLTMDEVETLFHEFGHALHGLLTKCEYKGTSGTNVVRDFVELPSQINEHWATEPEVLKMYAKHYQTGEVIPDEIIEKILKQKTFNQGFMTTELLAAAILDMNLHMITDVKNLDMLAFEKEAMDKLGLIPEIAPRYRVTYFNHIIGGYAAGYYSYLWANVLDNDAFEAFKEHGIFDKNTADLFRYNVLEKGDSEDPMILYKNFRGAEPSLEPLLKNRGMK',
     u'aa_sequence_md5': u'5e357f79ce4c35c27824cc81d38127c6',
     u'accession': u'NC_004663',
     u'alt_locus_tag': u'VBIBacThe70966_2881',
     u'annotation': u'PATRIC',
     u'date_inserted': u'2014-10-21T02:19:49.692Z',
     u'date_modified': u'2014-10-27T18:24:47.095Z',
     u'ec': [u'3.4.15.5|Peptidyl-dipeptidase Dcp'],
     u'end': 3534203,
     u'feature_id': u'PATRIC.226186.12.NC_004663.CDS.3532116.3534203.fwd',
     u'feature_type': u'CDS',
     u'figfam_id': u'FIG00004220',
     u'gene_id': 1071931,
     u'genome_id': u'226186.12',
     u'genome_name': u'Bacteroides thetaiotaomicron VPI-5482',
     u'gi': 29348243,
     u'location': u'3532116..3534203',
     u'na_length': 2088,
     u'na_sequence': u'atgatgattagaaaaactttaaccattttagcagtaagttgtatgatgtactcctgtggaacaaaaacagaaagcaaccctttcttcactgaatttcaaacagagtatggtgttccttccttcgataaaatcaaactggaacattacgaacccgcctttctgaaaggtattgaagagcagaatcagaatatccaagccattatcgcaagcccggaagtgcctactttcgacaatacgattgtagctttggacagcagcgcacccattctggaccgtgtaagcgccattttcttcaatatgacggatgcggaaacaaccgatgaactgaccgagctctctatcaaaatggcaccggtcctttccgagcacgaagataacatctccctgaatcaggagcttttcaaacgtgtaaacgttgtatatcaacagaaagattccatgaatctgaccacggaacagaaacgtctgctggacaaaacttacaaaggatttgtccgttcaggtgctaatctggatgcagagaaacaggcacgtctgcgtgaaatcaacaaagaactttccactctcggcatcacattcagcaataatatactgaatgaaaacaatgctttccagcttttcgtagacaagaaagaagatttagccggattgcccgaatggttctgccaaagcgcagccgaagaagccaaagctgccggacaaccggggaaatggctgttcaccctgcacaacgccagccgccttccgttcctgcaatacgctgagaaccgccctctccgtgagaaaatgtacaaagcatacatcaaccgcggcaataacaatgacaagaatgacaacaaagaaacgatccgcaagatcgtctccctccgcctggaaaaagcaaggctattgggcttcaacaactacgccaacttcgtactggatgagacaatgtcaaagaatgacagcaacgtaatgagtctgctgaacaacctttggagctatgccctcccgaaagcgaaagccgaagccgcagaacttcaacagttaatggacaaagaaggcaaaggagagaaactggaagcctgggactggtggtactacacagaaaaactccgcaaagagaaatacaacctctccgaagaagacaccaaaccttacttcaaactggagaatgtacgtgaaggagctttcgcagtcgccaacaaactatatggtatcactctgaacaaactggaaggtatcccgacttatcatccggatgtagaagtcttcgaagtgaaagacgctgacggctcccaactgggcatattctatgtagactatttcccgcgttcaggaaaaagcggtggcgcatggatgagcaattaccgcgaacagcagggagcaacccgccccttggtatgcaacgtatgcagtttcaccaaaccggtcggcgacaccccttctctgctgactatggacgaagtagaaactctgttccacgaattcgggcacgctctgcatggcttactgacaaagtgcgaatacaaagggacttccggcaccaatgtcgtacgcgattttgttgaacttccttctcagatcaacgaacattgggctaccgaaccggaagtgctgaaaatgtatgccaaacactatcagacaggagaagtaatccccgatgaaatcatcgaaaagattctgaaacagaaaacgttcaaccaaggattcatgaccaccgagttactggctgccgccatcctcgacatgaaccttcacatgataacagatgtaaagaatctggatatgcttgctttcgaaaaagaagccatggacaagctcggcctgatccccgaaattgccccccgctaccgcgtcacttacttcaatcatatcattggcggatacgctgccggatactacagttacctttgggcgaatgtacttgacaatgatgcctttgaagccttcaaagaacatggaatctttgataaaaacactgccgacctcttccgctacaacgtattggaaaagggagacagcgaagatccgatgatactttataagaatttccgcggtgcagaaccaagcctggagccgttactgaaaaacagaggaatgaaataa',
     u'owner': u'PATRIC',
     u'p2_feature_id': 21060633,
     u'patric_id': u'fig|226186.12.peg.2881',
     u'pgfam_id': u'PGF_00423604',
     u'plfam_id': u'PLF_816_00003556',
     u'pos_group': u'NC_004663:3534203:+',
     u'product': u'Dipeptidyl carboxypeptidase Dcp (EC 3.4.15.5)',
     u'protein_id': u'NP_811746.1',
     u'public': True,
     u'refseq_locus_tag': u'BT_2834',
     u'segments': [u'3532116..3534203'],
     u'sequence_id': u'NC_004663',
     u'start': 3532116,
     u'strand': u'+',
     u'taxon_id': 226186,
     u'uniprotkb_accession': [u'Q8A3X0']}


