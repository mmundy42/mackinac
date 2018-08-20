
Create a model using ModelSEED service
--------------------------------------

Mackinac provides functions for creating a model using the ModelSEED web
service and creating a COBRA model from the ModelSEED model. The COBRA
model contains all of the information from the ModelSEED model,
including metabolite data and gene annotations.

.. code:: ipython3

    import mackinac

There are four main functions to reconstruct a metabolic model using the
ModelSEED web service for analysis in cobrapy.

Reconstruct a draft model for an organism with
``reconstruct_modelseed_model()``. You need to provide a PATRIC genome
ID to identify the organism. You can
`search <https://www.patricbrc.org/view/DataType/Genomes>`__ on the
PATRIC website for available organisms. The genome ID is for the gram
negative bacteria Bacteroides thetaiotaomicron VPI-5482.

After a model is reconstructed, you refer to it by the specified ID. The
returned statistics provide a summary of the model. The created model is
stored in your ModelSEED workspace.

Note that it takes a few minutes for the ModelSEED web service to run a
function and return a result.

.. code:: ipython3

    mackinac.reconstruct_modelseed_model('226186.12', 'Btheta')




.. parsed-literal::

    {'fba_count': 0,
     'gapfilled_reactions': 0,
     'gene_associated_reactions': 978,
     'genome_ref': '/mmundy@patricbrc.org/modelseed/Btheta/genome',
     'id': 'Btheta',
     'integrated_gapfills': 0,
     'name': 'Bacteroides thetaiotaomicron VPI-5482',
     'num_biomass_compounds': 85,
     'num_biomasses': 1,
     'num_compartments': 2,
     'num_compounds': 1154,
     'num_genes': 718,
     'num_reactions': 978,
     'ref': '/mmundy@patricbrc.org/modelseed/Btheta',
     'rundate': '2018-06-18T18:25:36Z',
     'source': 'ModelSEED',
     'source_id': 'Btheta',
     'template_ref': '/chenry/public/modelsupport/templates/GramNegModelTemplate',
     'type': 'GenomeScale',
     'unintegrated_gapfills': 0}



Gap fill the model using the ModelSEED algorithm with
``gapfill_modelseed_model()``. By default the ModelSEED model is gap
filled on complete media. Use the ``media_reference`` parameter to
specify a different media. ModelSEED provides over 500 media in the
``/chenry/public/modelsupport/media`` folder. This step is optional if
you want to use other gap fill algorithms in cobrapy. Note that the
number of reactions and compounds in the returned metadata has increased
after gap filling although the number of gapfilled reactions is not
updated.

.. code:: ipython3

    mackinac.gapfill_modelseed_model('Btheta')




.. parsed-literal::

    {'fba_count': 0,
     'gapfilled_reactions': 0,
     'gene_associated_reactions': 978,
     'genome_ref': '/mmundy@patricbrc.org/modelseed/Btheta/genome',
     'id': 'Btheta',
     'integrated_gapfills': 1,
     'name': 'Bacteroides thetaiotaomicron VPI-5482',
     'num_biomass_compounds': 85,
     'num_biomasses': 1,
     'num_compartments': 2,
     'num_compounds': 1224,
     'num_genes': 718,
     'num_reactions': 1096,
     'ref': '/mmundy@patricbrc.org/modelseed/Btheta',
     'rundate': '2018-06-18T18:25:36Z',
     'source': 'ModelSEED',
     'source_id': 'Btheta',
     'template_ref': '/chenry/public/modelsupport/templates/GramNegModelTemplate',
     'type': 'GenomeScale',
     'unintegrated_gapfills': 0}



Run a simulation using the ModelSEED flux balance analysis algorithm
with ``optimize_modelseed_model()``. Use the ``media_reference``
parameter to specify a different media for the simulation. This step is
optional if you want to run the analysis in cobrapy.

.. code:: ipython3

    mackinac.optimize_modelseed_model('Btheta')




.. parsed-literal::

    111.633



Create a COBRA model from the ModelSEED model with
``create_cobra_model_from_modelseed_model()``. Now you can analyze the
model using all of the functionality in cobrapy.

.. code:: ipython3

    model = mackinac.create_cobra_model_from_modelseed_model('Btheta')
    model.id




.. parsed-literal::

    'Btheta'


