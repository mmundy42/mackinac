
Managing your ModelSEED models
------------------------------

Mackinac provides functions for managing and working with your ModelSEED
models. Before running this notebook, make sure you have reconstructed,
gap filled, and optimized a model with ID "226186.12" (see `modelseed
notebook <modelseed.ipynb>`__) or substitute an ID for a model that
exists in your workspace.

.. code:: ipython2

    import mackinac

Get a list of all of the ModelSEED models stored in your workspace with
``list_modelseed_models()``. Remove the ``print_output`` parameter to
return a list of model statistics about your models.

.. code:: ipython2

    mackinac.list_modelseed_models(print_output=True)


.. parsed-literal::

    Model /mmundy@patricbrc.org/modelseed/226186.12-0202 for organism Bacteroides thetaiotaomicron VPI-5482 with 1034 reactions and 1202 metabolites
    Model /mmundy@patricbrc.org/modelseed/226186.12-new for organism Bacteroides thetaiotaomicron VPI-5482 with 927 reactions and 1026 metabolites
    Model /mmundy@patricbrc.org/modelseed/220668.9.12-new for organism Lactobacillus plantarum WCFS1 with 992 reactions and 1063 metabolites
    Model /mmundy@patricbrc.org/modelseed/511145.12-new for organism Escherichia coli str. K-12 substr. MG1655 with 1478 reactions and 1423 metabolites
    Model /mmundy@patricbrc.org/modelseed/220668.9-pa for organism Lactobacillus plantarum WCFS1 with 992 reactions and 1063 metabolites
    Model /mmundy@patricbrc.org/modelseed/511145.12-pa for organism Escherichia coli str. K-12 substr. MG1655 with 1478 reactions and 1423 metabolites
    Model /mmundy@patricbrc.org/modelseed/226186.12-pa for organism Bacteroides thetaiotaomicron VPI-5482 with 1013 reactions and 1069 metabolites
    Model /mmundy@patricbrc.org/modelseed/226186.12 for organism Bacteroides thetaiotaomicron VPI-5482 with 1129 reactions and 1253 metabolites
    Model /mmundy@patricbrc.org/modelseed/264199.4 for organism Streptococcus thermophilus LMG 18311 with 824 reactions and 878 metabolites
    Model /mmundy@patricbrc.org/modelseed/742823.3 for organism Sutterella wadsworthensis 2_1_59BFAA with 985 reactions and 1161 metabolites
    Model /mmundy@patricbrc.org/modelseed/717962.3 for organism Coprococcus catus GD/7 with 1098 reactions and 1253 metabolites
    Model /mmundy@patricbrc.org/modelseed/1156417.3 for organism Caloranaerobacter azorensis H53214 with 836 reactions and 1072 metabolites
    Model /mmundy@patricbrc.org/modelseed/657315.3 for organism Roseburia intestinalis M50/1 with 1127 reactions and 1305 metabolites
    Model /mmundy@patricbrc.org/modelseed/29354.3 for organism [Clostridium] celerecrescens strain 152B with 1135 reactions and 1304 metabolites
    Model /mmundy@patricbrc.org/modelseed/180332.3 for organism Robinsoniella peoriensis WT with 1133 reactions and 1321 metabolites
    Model /mmundy@patricbrc.org/modelseed/484018.6 for organism Bacteroides plebeius DSM 17135 with 993 reactions and 1181 metabolites
    Model /mmundy@patricbrc.org/modelseed/1367212.3 for organism Clostridium cellulosi CS-4-4 with 1029 reactions and 1191 metabolites
    Model /mmundy@patricbrc.org/modelseed/1469948.3 for organism Clostridium sp. KNHs209 with 999 reactions and 1235 metabolites
    Model /mmundy@patricbrc.org/modelseed/1000569.4 for organism Megasphaera sp. UPII 135-E with 710 reactions and 944 metabolites
    Model /mmundy@patricbrc.org/modelseed/1165092.3 for organism Lachnospiraceae bacterium JC7 with 989 reactions and 1181 metabolites
    Model /mmundy@patricbrc.org/modelseed/1414720.3 for organism Clostridium sp. JCC with 1118 reactions and 1328 metabolites
    Model /mmundy@patricbrc.org/modelseed/742726.3 for organism Barnesiella intestinihominis YIT 11860 with 923 reactions and 1110 metabolites
    Model /mmundy@patricbrc.org/modelseed/1235835.3 for organism Anaerotruncus sp. G3(2012) with 859 reactions and 1110 metabolites
    Model /mmundy@patricbrc.org/modelseed/1297617.3 for organism Intestinimonas butyriciproducens ER1 with 982 reactions and 1228 metabolites
    Model /mmundy@patricbrc.org/modelseed/1313290.3 for organism Erysipelothrix rhusiopathiae SY1027 with 682 reactions and 860 metabolites
    Model /mmundy@patricbrc.org/modelseed/525362.3 for organism Lactobacillus ruminis ATCC 25644 with 908 reactions and 1111 metabolites
    Model /mmundy@patricbrc.org/modelseed/557855.3 for organism Mitsuaria sp. H24L5A with 1267 reactions and 1451 metabolites


Get current statistics about a ModelSEED model with
``get_modelseed_model_stats()``. The returned statistics provide a
summary of the model.

.. code:: ipython2

    mackinac.get_modelseed_model_stats('226186.12')




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



Get the details of the ModelSEED gap fill solutions with
``get_modelseed_gapfill_solutions()``. There can be multiple gap fill
solutions for a model and the returned list is sorted from newest to
oldest.

.. code:: ipython2

    gf_solutions = mackinac.get_modelseed_gapfill_solutions('226186.12')

Get the number of reactions in a gap fill solution by checking the
length of the ``reactions`` key in a solution.

.. code:: ipython2

    len(gf_solutions[0]['reactions'])




.. parsed-literal::

    97



The ``reactions`` key is a dictionary keyed by reaction ID with details
on the reactions added to the model.

.. code:: ipython2

    gf_solutions[0]['reactions']['rxn00086_c0']




.. parsed-literal::

    {u'compartment': u'c0',
     u'direction': u'<',
     u'reaction': u'~/fbamodel/template/reactions/id/rxn00086_c'}



Get the details of a ModelSEED flux balance analysis solution with
``get_modelseed_fba_solutions()``. There can be multiple fba solutions
for a model and the returned list is sorted from newest to oldest.

.. code:: ipython2

    fba_solutions = mackinac.get_modelseed_fba_solutions('226186.12')

In an fba solution, the ``exchanges`` key is a dictionary keyed by
metabolite ID of the metabolites that can be exchanged with the
boundary. Metabolites with a positive flux are consumed and metabolites
with a negative flux are produced.

.. code:: ipython2

    fba_solutions[0]['exchanges']['cpd00001_e0']




.. parsed-literal::

    {'lower_bound': -1000, 'upper_bound': 100, 'x': -830.615}



The ``reactions`` key is a dictionary keyed by reaction ID with details
on the bounds and flux for every reaction in model.

.. code:: ipython2

    fba_solutions[0]['reactions']['rxn00086_c0']




.. parsed-literal::

    {'lower_bound': -1000, 'upper_bound': 0, 'x': -0.1547}



If you no longer need a ModelSEED model, delete it from your ModelSEED
workspace with ``delete_modelseed_model()``.

.. code:: ipython2

    mackinac.delete_modelseed_model('226186.12')
