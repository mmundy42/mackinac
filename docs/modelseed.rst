
Mackinac: A bridge between ModelSEED and COBRApy
------------------------------------------------

Mackinac provides support for creating a COBRA model directly from a
ModelSEED model. The COBRA model contains all of the information from
the ModelSEED model, including metabolite data and gene annotations. In
addition, Mackinac provides direct access to many of the functions
available from the ModelSEED web service.

.. code:: ipython2

    import mackinac

You create draft models from genomes available in the `Pathosystems
Resource Integration
Center <https://www.patricbrc.org/portal/portal/patric/Home>`__
(PATRIC). If you are not a `registered PATRIC
user <http://enews.patricbrc.org/faqs/workspace-faqs/registration-faqs/>`__,
you must complete a `new user
registration <https://user.patricbrc.org/register/>`__ to work with the
ModelSEED web service.

Before using ModelSEED functions, you must first get an authentication
token with your PATRIC username and password. The ``get_token()``
function stores the authentication token in the ``.patric_config`` file
in your home directory. You can use the token until it expires.

Change ``username`` in the cell below to your PATRIC username and enter
your password when prompted. The returned user ID identifies your
ModelSEED workspace. You only need to get a token the first time you use
this notebook.

.. code:: ipython2

    mackinac.get_token('username')


.. parsed-literal::

    patric password: ········




.. parsed-literal::

    u'mmundy@patricbrc.org'



There are four main functions to reconstruct a metabolic model using the
ModelSEED web service for analysis in cobrapy.

First, reconstruct a draft model for an organism with
``reconstruct_modelseed_model()``. You need to provide a PATRIC genome
ID to identify the organism. You can `search for
genomes <https://www.patricbrc.org/portal/portal/patric/Genomes>`__ on
the PATRIC website from the thousands of bacterial organisms available.
After a model is reconstructed, you refer to it by ID. By default, the
ID of the model is the genome ID. You can give a model a different ID
with the ``model_id`` parameter. The returned statistics provide a
summary of the model.

Note that it takes a minute or two for the ModelSEED web service to run
a function and return a result.

.. code:: ipython2

    mackinac.reconstruct_modelseed_model('226186.12')




.. parsed-literal::

    {'fba_count': 0,
     'gapfilled_reactions': 0,
     'gene_associated_reactions': 1034,
     'genome_ref': u'/mmundy@patricbrc.org/modelseed/226186.12/genome',
     'id': u'226186.12',
     'integrated_gapfills': 0,
     'name': u'Bacteroides thetaiotaomicron VPI-5482',
     'num_biomass_compounds': 85,
     'num_biomasses': 1,
     'num_compartments': 2,
     'num_compounds': 1202,
     'num_genes': 739,
     'num_reactions': 1034,
     'ref': u'/mmundy@patricbrc.org/modelseed/226186.12',
     'rundate': u'2017-01-20T17:39:47',
     'source': u'ModelSEED',
     'source_id': u'226186.12',
     'template_ref': u'/chenry/public/modelsupport/templates/GramNegative.modeltemplate',
     'type': u'GenomeScale',
     'unintegrated_gapfills': 0}



Second, gap fill the model using the ModelSEED algorithm with
``gapfill_modelseed_model()``. By default the ModelSEED model is gap
filled on complete media. Use the ``media_reference`` parameter to
specify a different media. ModelSEED provides over 500 media in the
``/chenry/public/modelsupport/media`` folder (see the workspace notebook
for directions on how to show all of the available media). This step is
optional if you want to use other gap fill algorithms in cobrapy. Note
that the number of reactions and compounds in the returned metadata has
increased after gap filling.

.. code:: ipython2

    mackinac.gapfill_modelseed_model('226186.12')




.. parsed-literal::

    {'fba_count': 0,
     'gapfilled_reactions': 0,
     'gene_associated_reactions': 1034,
     'genome_ref': u'/mmundy@patricbrc.org/modelseed/226186.12/genome',
     'id': u'226186.12',
     'integrated_gapfills': 1,
     'name': u'Bacteroides thetaiotaomicron VPI-5482',
     'num_biomass_compounds': 85,
     'num_biomasses': 1,
     'num_compartments': 2,
     'num_compounds': 1253,
     'num_genes': 739,
     'num_reactions': 1129,
     'ref': u'/mmundy@patricbrc.org/modelseed/226186.12',
     'rundate': u'2017-01-20T17:39:47',
     'source': u'ModelSEED',
     'source_id': u'226186.12',
     'template_ref': u'/chenry/public/modelsupport/templates/GramNegative.modeltemplate',
     'type': u'GenomeScale',
     'unintegrated_gapfills': 0}



Third, run a simulation using the ModelSEED flux balance analysis
algorithm with ``optimize_modelseed_model()``. Use the
``media_reference`` parameter to specify a different media for the
simulation. This step is optional if you want to run the analysis in
cobrapy.

.. code:: ipython2

    mackinac.optimize_modelseed_model('226186.12')




.. parsed-literal::

    99.9203



Finally, create a COBRA model from the ModelSEED model with
``create_cobra_model_from_modelseed_model()``. Now you can analyze the
model using all of the functionality in cobrapy.

.. code:: ipython2

    model = mackinac.create_cobra_model_from_modelseed_model('226186.12')
    model.id




.. parsed-literal::

    u'226186.12'


