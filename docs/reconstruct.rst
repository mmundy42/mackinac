
Reconstruct a model from a template
-----------------------------------

Mackinac supports creating draft models from a genome and template
model. Before running this notebook, you need to configure things.

.. code:: ipython3

    import mackinac

Mackinac includes the source files needed to build a template model for
bacteria. Create a template model

.. code:: ipython3

    template = mackinac.templates.create_mackinac_template_model('mackinac/data/modelseed/universal', 'mackinac/data/modelseed/bacteria', 'bacteria', 'bacteria')

Reconstruct a draft model from the PATRIC genome.

.. code:: ipython3

    data_folder = join(expanduser('~'), 'mackinac_data')
    fid_role_path = join(data_folder, 'otu_fid_role.tsv')
    search_db_path = join(data_folder, 'protein.udb')
    search_program_path = join(expanduser('~'), 'usearch')
    work_folder = join(expanduser('~'), 'mackinac_work')
    btheta = mackinac.reconstruct_model(template, '226186.12', 'negbio', search_program_path, search_db_path, fid_role_path, work_folder)
    btheta.optimize()
