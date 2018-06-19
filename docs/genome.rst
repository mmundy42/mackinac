
Work with PATRIC genomes
------------------------

Mackinac provides functions for working with PATRIC genomes which can be
used to reconstruct models using the PATRIC web service, the ModelSEED
web service, or with template models.

PATRIC updates the annotations for genomes on a regular schedule so the
data returned by the genome functions can be different depending on when
you get the data. Check the `PATRIC
News <https://docs.patricbrc.org/news/index.html>`__ for details on the
changes in each PATRIC release.

.. code:: ipython3

    import mackinac

Get summary information for a PATRIC genome with
``get_genome_summary()``. You can
`search <https://www.patricbrc.org/view/DataType/Genomes>`__ on the
PATRIC website for available organisms. The genome ID
`226186.12 <https://www.patricbrc.org/view/Genome/226186.12>`__ is for
the gram negative bacteria Bacteroides thetaiotaomicron VPI-5482. Note
that information available in the summary can be different for different
genomes depending on the source of the genome.

.. code:: ipython3

    mackinac.get_genome_summary('226186.12')




.. parsed-literal::

    {'_version_': 1585509101369032700,
     'assembly_accession': 'GCA_000011065.1',
     'bioproject_accession': 'PRJNA399',
     'biosample_accession': 'SAMN02604314',
     'brc1_cds': 0,
     'cell_shape': 'Rod',
     'chromosomes': 1,
     'class': 'Bacteroidia',
     'comments': ['Bacteroides thetaiotaomicron strain VPI-5482. This is the type strain for this organism and was isolated from the feces of a healthy adult.'],
     'common_name': 'Bacteroides_thetaiotaomicron_VPI-5482',
     'completion_date': '2003-03-29T00:00:00Z',
     'contigs': 0,
     'date_inserted': '2014-12-08T22:10:24.729Z',
     'date_modified': '2015-03-16T03:17:09.594Z',
     'disease': ['Peritonitis'],
     'document_type': 'genome',
     'family': 'Bacteroidaceae',
     'gc_content': 42.9,
     'genbank_accessions': 'AE015928,AY171301',
     'genome_id': '226186.12',
     'genome_length': 6293399,
     'genome_name': 'Bacteroides thetaiotaomicron VPI-5482',
     'genome_status': 'Complete',
     'genus': 'Bacteroides',
     'gram_stain': '-',
     'habitat': 'Host-associated',
     'isolation_comments': 'isolated from the feces of a healthy adult',
     'isolation_source': 'the feces of a healthy adult',
     'kingdom': 'Bacteria',
     'ncbi_project_id': '399',
     'optimal_temperature': '-',
     'order': 'Bacteroidales',
     'organism_name': 'Bacteroides thetaiotaomicron VPI-5482',
     'owner': 'PATRIC',
     'oxygen_requirement': 'Anaerobic',
     'p2_genome_id': 70966,
     'patric_cds': 4872,
     'phylum': 'Bacteroidetes',
     'plasmids': 1,
     'public': True,
     'publication': '12663928,19321416',
     'reference_genome': 'Reference',
     'refseq_accessions': 'NC_004663,NC_004703',
     'refseq_cds': 4816,
     'refseq_project_id': '62913',
     'sequences': 2,
     'sequencing_centers': 'Genome Sequencing Center (GSC) at Washington University (WashU) School of Medicine',
     'sequencing_status': 'complete',
     'species': 'Bacteroides thetaiotaomicron',
     'strain': 'VPI-5482',
     'taxon_id': 226186,
     'taxon_lineage_ids': ['131567',
      '2',
      '1783270',
      '68336',
      '976',
      '200643',
      '171549',
      '815',
      '816',
      '818',
      '226186'],
     'taxon_lineage_names': ['cellular organisms',
      'Bacteria',
      'FCB group',
      'Bacteroidetes/Chlorobi group',
      'Bacteroidetes',
      'Bacteroidia',
      'Bacteroidales',
      'Bacteroidaceae',
      'Bacteroides',
      'Bacteroides thetaiotaomicron',
      'Bacteroides thetaiotaomicron VPI-5482'],
     'temperature_range': 'Mesophilic',
     'type_strain': 'Yes'}



Get the features for an annotated genome with ``get_genome_features()``.
Both PATRIC and RefSeq annotations are available. Note that the number
of features and details of the features can change as PATRIC updates the
annotations.

.. code:: ipython3

    features = mackinac.get_genome_features('226186.12', annotation='PATRIC')
    len(features)




.. parsed-literal::

    4965



The returned list has detailed information about each feature including
the type and DNA sequence. If the feature is a coding sequence, the
returned data also includes the amino acid sequence.

.. code:: ipython3

    features[100]




.. parsed-literal::

    {'aa_length': 1052,
     'aa_sequence': 'MKIEKFYLFLLACFVAIGAYSQDGQQKMTGDEKSQQQSDAKVKITGQVFDESGEGIPGANVTLKSNPTSGTVTDLDGKFILMASPQKDVLVVSFIGYNTQEFPLKGKTNVTIQLSQNVNELDAVEIVAFGTQKKESVIGSITTLSPKSLRVPSSNMTTALAGQVAGIISYQTSGEPGADDASFFVRGIASFGFNTSPLILIDNIESTSTDLGRLNPDDIESFSIMKDAMATALYGSRGANGVVLVKTKEGERGKTKFDVRIEGSNSRPTSNIELADPVTYMKLHNEAILTRDPSAPVMYSDDKIDRTVPGSGSIIYPTNDWRRQLMKNSTWNGRANMSISGGGNSATYYVSLRYTKDQGLLNVDGKNNFNNNINLQTYQMRANVNINVTKTTQVRVNLSGIFDTYEGPIYSGSDIYKMVMKSNPVLFPAVYPTDEQHKYIKHILFGNSDDGSYLNPYAEMVKGYKEYENTTLLATLGVTQDLNFITKGLKFEGFFNVSRKSYYGQTRQYKPYYYALSSYDFMTEKYSIENINPDSGTEYLDFSPGDKTVNNVMTIETRTSYNQTFGDHSVGGLIVTQYIDSKNPNYKTLQESLPSRNMGVSGRFTYAYSDRYFTEFNFGYNASERFDKKHRWGFFPSVGGGWMISNEPFFQPLSSKITKLKLRASYGLVGNDKIGRVDERFLYLSNVNMNAGGASFGYENKYSRPGVNVSRYANPAIGWEKSRKANFALEASFYGFDLIAEYFTEHRTDILQKRASIPSVMGYQADVYANIGETKGHGVDLDLKYQKNLNKNAFLIVRGNLTYAHSEYLKYEDNTYDKEWWKYKIGYSPNQKWGYIAEGLFIDDAEVANSPVQFGDYKAGDIKYRDMNGDGVINSLDQVPIGHPTSPEINYGFGSTFSYKGFDINFQFHGSAQSSFWIDYDKMSPFFKDSKMSQKTNNQLVKFIANSYWSESNRNRYATWPRLSTTSVANNKELSTWFMRDGSFLRLKLVELGYTVPQKIVSKWGMSNLRLYMSSTNLFVLSKFKDWDVELAGNGLNYPLQRVFNIGVNVSF',
     'aa_sequence_md5': '7a4ce145bf65d16f0ff5240e40a33cf9',
     'accession': 'NC_004663',
     'alt_locus_tag': 'VBIBacThe70966_3018',
     'annotation': 'PATRIC',
     'date_inserted': '2014-10-20T23:55:52.504Z',
     'date_modified': '2014-10-27T18:24:47.095Z',
     'end': 3743808,
     'feature_id': 'PATRIC.226186.12.NC_004663.CDS.3740650.3743808.rev',
     'feature_type': 'CDS',
     'figfam_id': 'FIG01260980',
     'gene_id': 1075832,
     'genome_id': '226186.12',
     'genome_name': 'Bacteroides thetaiotaomicron VPI-5482',
     'gi': 29348377,
     'location': 'complement(3740650..3743808)',
     'na_length': 3159,
     'na_sequence': 'atgaaaattgaaaagttttatttgtttctgctagcttgctttgtcgcgataggagcatattcgcaagatgggcaacagaaaatgactggtgatgaaaagagtcagcagcaaagtgatgcaaaagttaagattaccgggcaggtctttgatgagagcggtgaaggaatacctggagcgaatgttactcttaaaagtaatcccaccagtggaactgtcacagatctggatggtaagtttattttgatggcttctcctcaaaaggatgtgctggtagtcagctttattggatataacacacaagaatttccactgaaagggaaaacaaacgttaccatccaactctcacaaaacgtaaatgaactggatgcggtggaaattgtggcattcggaacacaaaagaaggagagtgtgattggttctatcactacactttcgccaaagagcctgagagtgccgagcagtaatatgacaactgcattggcaggtcaggtagccggtattatttcttatcagacatcaggagagccgggtgcggacgatgctagcttttttgtacgtggtatcgcatctttcggatttaacaccagtcctttgattctgattgataacattgaatctacaagtacggacttagggcgtttgaatcccgatgatatcgaaagtttttcaatcatgaaagatgccatggcaacggccctttacggttcgagaggagctaatggcgtcgttctagtaaagacaaaagagggagagagaggaaaaactaagtttgatgtaagaatagagggaagtaattctcgtccgaccagtaatattgagttggcagaccctgtcacttacatgaaattgcataatgaagccatcttaacacgtgatccttccgcccctgtcatgtatagtgatgataaaatagacagaaccgttccgggatctggttctatcatttatcctacaaatgactggagaaggcaactaatgaagaactcgacctggaatggaagagccaacatgagcatcagtggcggaggaaattcggctacgtattacgtgtctctgcgatataccaaagaccagggtttgctcaacgtagacggcaagaacaacttcaacaacaatatcaatcttcagacttatcagatgagggctaatgtcaacatcaatgtgacaaaaacgacccaggtaagagtaaacttaagtggaatctttgacacttatgaaggtcctatttattcgggatcggatatttataagatggtaatgaagtctaatcctgtactttttcccgctgtatatcctaccgatgaacaacataaatatatcaaacacattctttttggaaacagcgatgacggaagttatcttaacccgtatgctgaaatggtaaaaggatataaggaatatgagaatacgactcttcttgctacattaggtgttacgcaggacttgaactttatcactaaaggtttgaaatttgaaggtttcttcaacgtttctcgtaaatcatattacggtcagaccagacaatataagccatattactatgctttaagttcttatgatttcatgacagagaaatattctatcgaaaacatcaatcctgactccggaacggaataccttgattttagtcccggtgacaagactgtcaacaatgtaatgacaatcgaaacgagaaccagttataatcagactttcggtgatcattccgtaggtggtcttatcgttactcagtatatcgacagtaagaatccaaactacaaaactttgcaggagagcttgccttcaagaaatatgggtgtgtcgggacgttttacttatgcctatagtgaccgctatttcacggagttcaattttggatacaatgcttccgaacgctttgataagaaacacagatggggattctttccgtccgtcggtggtggctggatgatttcgaacgaaccattcttccaaccgctcagttcaaaaattacgaaattgaaactaagagcctcatacggtttggtgggaaatgataagattggcagagtcgatgaacgtttcttatatctgtctaatgtgaatatgaatgcaggtggagcatctttcgggtatgaaaacaaatatagcagaccgggcgtaaatgtttcacgttatgctaatcctgccattggatgggaaaaatcccgtaaagctaatttcgcattggaagcttctttctacggatttgacctgatagctgaatatttcacagaacatcgtactgacatattacagaaaagagccagtattccaagcgtaatgggatatcaggcagacgtatatgctaacattggcgagaccaaaggacacggtgtggatcttgatttaaagtatcaaaagaaccttaacaaaaacgcttttttgatagtacgcggaaacttaacctatgcgcatagtgaatatctgaaatatgaagataacacgtatgataaggaatggtggaaatacaaaataggctactcgcccaaccagaagtggggatacattgcggaagggctatttatagacgatgcggaagtggccaactctcctgtacagtttggtgattataaagccggagatatcaaataccgggatatgaatggagatggagtaattaattcattggatcaagttcctattggacatccgactagtccggaaatcaactatggctttggatcaacatttagctataaaggttttgacatcaatttccagttccacggctcggcgcagtcttctttctggattgattatgataagatgtctccattctttaaagattcgaagatgtctcagaaaactaataatcaactagtgaaatttattgcaaatagctattggtcggaaagtaaccgcaatcgttatgcaacatggcccagattgtcaaccacttctgttgccaacaataaagaactgagtacatggttcatgagagacggttccttcttacgactgaaattggttgaactgggatatacagtacctcaaaaaattgtgagcaaatggggtatgtccaatctgaggctctatatgtcttctaccaatctttttgttttgagtaagttcaaggattgggatgtggaattggcaggtaatggtcttaattatccgttacaacgtgtattcaatattggtgtaaatgtaagtttctaa',
     'owner': 'PATRIC',
     'p2_feature_id': 21060909,
     'patric_id': 'fig|226186.12.peg.3018',
     'pgfam_id': 'PGF_02755714',
     'plfam_id': 'PLF_816_00024336',
     'pos_group': 'NC_004663:3740650:-',
     'product': 'Outer membrane TonB-dependent transporter, utilization system for glycans and polysaccharides (PUL), SusC family',
     'protein_id': 'NP_811880.1',
     'public': True,
     'refseq_locus_tag': 'BT_2968',
     'segments': ['3740650..3743808'],
     'sequence_id': 'NC_004663',
     'start': 3740650,
     'strand': '-',
     'taxon_id': 226186,
     'uniprotkb_accession': ['Q8A3I6']}


