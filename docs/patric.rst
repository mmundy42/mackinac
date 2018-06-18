
Create a PATRIC model
---------------------

Mackinac provides functions for creating a PATRIC model using the PATRIC
web service and creating a COBRA model from the PATRIC model.

.. code:: ipython3

    import mackinac

Reconstruct, gap fill, and optimize a model for an organism with
``create_patric_model()``. You need to provide a PATRIC genome ID to
identify the organism. You can
`search <https://www.patricbrc.org/view/DataType/Genomes>`__ on the
PATRIC website for available organisms. The genome ID
`226186.12 <https://www.patricbrc.org/view/Genome/226186.12>`__ is for
the gram negative bacteria Bacteroides thetaiotaomicron VPI-5482.

After a model is created, you refer to it by the specified ID. The
returned statistics provide a summary of the model. The created model is
stored in your PATRIC workspace.

Note that it takes a few minutes for the PATRIC web service to run a
function and return a result.

.. code:: ipython3

    mackinac.create_patric_model('226186.12', 'Btheta')




.. parsed-literal::

    {'fba_count': 1,
     'gapfilled_reactions': 123,
     'gene_associated_reactions': 978,
     'genome_ref': '/mmundy@patricbrc.org/home/models/.Btheta/genome',
     'id': 'Btheta',
     'integrated_gapfills': 1,
     'name': 'Bacteroides thetaiotaomicron VPI-5482',
     'num_biomass_compounds': 85,
     'num_biomasses': 1,
     'num_compartments': 2,
     'num_compounds': 1229,
     'num_genes': 718,
     'num_reactions': 1101,
     'ref': '/mmundy@patricbrc.org/home/models/.Btheta',
     'rundate': '2018-05-08T12:58:12Z',
     'source': 'PATRIC',
     'source_id': '.Btheta',
     'template_ref': '/chenry/public/modelsupport/templates/GramNegative.modeltemplate',
     'type': 'GenomeScale',
     'unintegrated_gapfills': 0}



Create a COBRA model from the PATRIC model with
``create_cobra_model_from_patric_model()``. Now you can analyze the
model using all of the functionality in cobrapy.

.. code:: ipython3

    model = mackinac.create_cobra_model_from_patric_model('Btheta')
    model.id




.. parsed-literal::

    'Btheta'


