
Create a model from a template model
------------------------------------

Mackinac supports creating draft models from the features of an
annotated genome and a template model using two methods:

1. ``reconstruct_model_from_features()`` uses the ModelSEED algorithm
   that is based on pattern matching of the features from the genome to
   the features in the template model that have a known linkage to
   reactions.
2. ``reconstruct_model_from_likelihoods()`` uses the likelihood-based
   gene annotation algorithm that is based on sequence similarity to
   known features in the template model that have a known linkage to
   reactions.

Both methods run locally without using a web service. When using the
likelihood-based gene annotation algorithm, you must first install a
search program, download data files, and build a search database.

The genome must be annotated using RAST. Note that RAST updates its
annotations on a regular basis. The updates include both new features
and changes to existing features. Reconstructing a draft model using
different ModelSEED template models produces different results since the
features in the template might not match the RAST annotation of the
genome.

.. code:: ipython3

    import mackinac
    import pkg_resources
    from os.path import join, expanduser

Create a bacteria template model with ``create_template_model()``.

.. code:: ipython3

    universal_folder = pkg_resources.resource_filename('mackinac', 'data/modelseed/universal')
    bacteria_folder = pkg_resources.resource_filename('mackinac', 'data/modelseed/bacteria')
    template = mackinac.create_template_model(universal_folder, bacteria_folder, 'bacteria', 'Bacteria template')

Download the summary information and features for an organism. You can
`search <https://www.patricbrc.org/view/DataType/Genomes>`__ on the
PATRIC website for available organisms. The genome ID
`226186.12 <https://www.patricbrc.org/view/Genome/226186.12>`__ is for
the gram negative bacteria Bacteroides thetaiotaomicron VPI-5482.

.. code:: ipython3

    summary = mackinac.get_genome_summary('226186.12')
    features = mackinac.get_genome_features('226186.12')

Reconstruct draft model from features
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Reconstruct a draft model from the annotated genome with
``reconstruct_model_from_features()``.

.. code:: ipython3

    feature_model = mackinac.reconstruct_model_from_features(features, template, 'Btheta-feature', 'negbio', gc_content=summary['gc_content'] / 100.0)

Reconstruct draft model from likelihoods
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Calculate reaction likelihoods from the annotated genome with
``calculate_likelihoods()``.

.. code:: ipython3

    work_folder = join(expanduser('~'), 'mackinac_work')
    data_folder = join(expanduser('~'), 'mackinac_data')
    fid_role_path = join(data_folder, 'otu_fid_role.tsv')
    protein_sequence_path = join(data_folder, 'protein.fasta')
    search_db_path = join(data_folder, 'protein.udb')
    search_program_path = join(expanduser('~'), 'usearch')
    likelihoods = mackinac.calculate_likelihoods('226186.12', features, template, search_program_path=search_program_path, search_db_path=search_db_path, fid_role_path=fid_role_path, work_folder=work_folder)

Reconstruct a draft model from likely reactions with
``reconstruct_model_from_likelihoods()``. By default, reactions with
likelihood greater than 0.1 are included in the draft model. Use the
``cutoff`` parameter to choose a different likelihood value.

.. code:: ipython3

    likely_model = mackinac.reconstruct_model_from_likelihoods(likelihoods, template, 'Btheta-likely', 'negbio', gc_content=summary['gc_content'] / 100.0)
