
Work with PATRIC models
-----------------------

Mackinac provides functions for managing and working with your PATRIC
models which are stored in the ``home/models`` folder in your PATRIC
workspace. The examples below assume that there is model with ID
``Btheta`` in your workspace.

.. code:: ipython3

    import mackinac

Get a list of all of the PATRIC models stored in your workspace with
``list_patric_models()``. Remove the ``print_output`` parameter to
return a list of model statistics about your models.

.. code:: ipython3

    mackinac.list_patric_models(print_output=True)


.. parsed-literal::

    Model /mmundy@patricbrc.org/modelseed/226186.12-pytest for organism Bacteroides thetaiotaomicron VPI-5482 with 1029 reactions and 1191 metabolites
    Model /mmundy@patricbrc.org/modelseed/411464.8 for organism Desulfovibrio piger ATCC 29098 with 846 reactions and 1058 metabolites
    Model /mmundy@patricbrc.org/modelseed/bt_likelihood for organism Bacteroides thetaiotaomicron VPI-5482 with 1029 reactions and 1191 metabolites
    Model /mmundy@patricbrc.org/modelseed/226186.12-0531 for organism Bacteroides thetaiotaomicron VPI-5482 with 1034 reactions and 1202 metabolites
    Model /mmundy@patricbrc.org/modelseed/1679.26 for organism Bifidobacterium longum subsp. longum strain AH1206 with 994 reactions and 1304 metabolites
    Model /mmundy@patricbrc.org/modelseed/742823.3 for organism Sutterella wadsworthensis 2_1_59BFAA with 979 reactions and 1306 metabolites
    Model /mmundy@patricbrc.org/modelseed/742726.3 for organism Barnesiella intestinihominis YIT 11860 with 1026 reactions and 1329 metabolites
    Model /mmundy@patricbrc.org/modelseed/557855.3 for organism Mitsuaria sp. H24L5A with 1317 reactions and 1593 metabolites
    Model /mmundy@patricbrc.org/modelseed/484018.6 for organism Bacteroides plebeius DSM 17135 with 1089 reactions and 1363 metabolites
    Model /mmundy@patricbrc.org/modelseed/717962.3 for organism Coprococcus catus GD/7 with 1097 reactions and 1403 metabolites
    Model /mmundy@patricbrc.org/modelseed/29354.3 for organism [Clostridium] celerecrescens strain 152B with 1235 reactions and 1483 metabolites
    Model /mmundy@patricbrc.org/modelseed/1297617.3 for organism Intestinimonas butyriciproducens ER1 with 1074 reactions and 1383 metabolites
    Model /mmundy@patricbrc.org/modelseed/180332.3 for organism Robinsoniella peoriensis WT with 1219 reactions and 1488 metabolites
    Model /mmundy@patricbrc.org/modelseed/1156417.3 for organism Caloranaerobacter azorensis H53214 with 935 reactions and 1265 metabolites
    Model /mmundy@patricbrc.org/modelseed/525362.3 for organism Lactobacillus ruminis ATCC 25644 with 1005 reactions and 1296 metabolites
    Model /mmundy@patricbrc.org/modelseed/657315.3 for organism Roseburia intestinalis M50/1 with 1120 reactions and 1454 metabolites
    Model /mmundy@patricbrc.org/modelseed/1414720.3 for organism Clostridium sp. JCC with 1214 reactions and 1509 metabolites
    Model /mmundy@patricbrc.org/modelseed/1000569.4 for organism Megasphaera sp. UPII 135-E with 844 reactions and 1174 metabolites
    Model /mmundy@patricbrc.org/modelseed/1469948.3 for organism Clostridium sp. KNHs209 with 1103 reactions and 1419 metabolites
    Model /mmundy@patricbrc.org/modelseed/1313290.3 for organism Erysipelothrix rhusiopathiae SY1027 with 838 reactions and 1105 metabolites
    Model /mmundy@patricbrc.org/modelseed/1165092.3 for organism Lachnospiraceae bacterium JC7 with 1097 reactions and 1375 metabolites
    Model /mmundy@patricbrc.org/modelseed/1235835.3 for organism Anaerotruncus sp. G3(2012) with 968 reactions and 1310 metabolites
    Model /mmundy@patricbrc.org/modelseed/1367212.3 for organism Clostridium cellulosi CS-4-4 with 1121 reactions and 1372 metabolites
    Model /mmundy@patricbrc.org/modelseed/511145.183 for organism Escherichia coli str. K-12 substr. MG1655 with 1609 reactions and 1755 metabolites
    Model /mmundy@patricbrc.org/modelseed/511145.12 for organism Escherichia coli str. K-12 substr. MG1655 with 1565 reactions and 1649 metabolites
    Model /mmundy@patricbrc.org/modelseed/226186.12-0202 for organism Bacteroides thetaiotaomicron VPI-5482 with 1034 reactions and 1202 metabolites
    Model /mmundy@patricbrc.org/modelseed/226186.12-new for organism Bacteroides thetaiotaomicron VPI-5482 with 927 reactions and 1026 metabolites
    Model /mmundy@patricbrc.org/modelseed/220668.9.12-new for organism Lactobacillus plantarum WCFS1 with 992 reactions and 1063 metabolites
    Model /mmundy@patricbrc.org/modelseed/511145.12-new for organism Escherichia coli str. K-12 substr. MG1655 with 1478 reactions and 1423 metabolites
    Model /mmundy@patricbrc.org/modelseed/220668.9-pa for organism Lactobacillus plantarum WCFS1 with 992 reactions and 1063 metabolites
    Model /mmundy@patricbrc.org/modelseed/511145.12-pa for organism Escherichia coli str. K-12 substr. MG1655 with 1478 reactions and 1423 metabolites
    Model /mmundy@patricbrc.org/modelseed/226186.12-pa for organism Bacteroides thetaiotaomicron VPI-5482 with 1013 reactions and 1069 metabolites
    Model /mmundy@patricbrc.org/modelseed/264199.4 for organism Streptococcus thermophilus LMG 18311 with 824 reactions and 878 metabolites


Get current statistics about a PATRIC model with
``get_modelseed_model_stats()``. The returned statistics provide a
summary of the model.

.. code:: ipython3

    mackinac.get_patric_model_stats('Btheta')


::


    ---------------------------------------------------------------------------

    NameError                                 Traceback (most recent call last)

    <ipython-input-1-af14ca7b0b7b> in <module>()
    ----> 1 mackinac.get_modelseed_model_stats('Btheta')
    

    NameError: name 'mackinac' is not defined


Get the details of the PATRIC gap fill solutions with
``get_patric_gapfill_solutions()``. There can be multiple gap fill
solutions for a model and the returned list is sorted from newest to
oldest.

.. code:: ipython3

    gf_solutions = mackinac.get_modelseed_gapfill_solutions('Btheta')

Get the number of reactions in a gap fill solution by checking the
length of the ``reactions`` key in a solution.

.. code:: ipython3

    len(gf_solutions[0]['reactions'])


::


    ---------------------------------------------------------------------------

    IndexError                                Traceback (most recent call last)

    <ipython-input-5-19abfa686887> in <module>()
    ----> 1 len(gf_solutions[0]['reactions'])
    

    IndexError: list index out of range


The ``reactions`` key is a dictionary keyed by reaction ID with details
on the reactions added to the model.

.. code:: ipython3

    gf_solutions[0]['reactions']['rxn00086_c0']

Get the details of a PATRIC flux balance analysis solution with
``get_patric_fba_solutions()``. There can be multiple fba solutions for
a model and the returned list is sorted from newest to oldest.

.. code:: ipython3

    fba_solutions = mackinac.get_patric_fba_solutions('Btheta')

In an fba solution, the ``exchanges`` key is a dictionary keyed by
metabolite ID of the metabolites that can be exchanged with the
boundary. Metabolites with a positive flux are consumed and metabolites
with a negative flux are produced.

.. code:: ipython3

    fba_solutions[0]['exchanges']['cpd00001_e0']




.. parsed-literal::

    {'lower_bound': -1000, 'upper_bound': 100, 'x': -630.187}



The ``reactions`` key is a dictionary keyed by reaction ID with details
on the bounds and flux for every reaction in model.

.. code:: ipython3

    fba_solutions[0]['reactions']['rxn00086_c0']

If you no longer need a PATRIC model, delete it from your workspace with
``delete_patric_model()``.

.. code:: ipython3

    mackinac.delete_patric_model('Btheta')
