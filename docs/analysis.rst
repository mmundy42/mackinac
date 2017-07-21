
Model analysis
--------------

Mackinac enables you to seamlessly work with ModelSEED models in
COBRApy.

This notebook shows how to work with two models for Escherichia coli
str. K-12 substr. MG1655. The `iJO1366
model <http://bigg.ucsd.edu/models/iJO1366>`__ is a manually curated
model that is available from BiGG. You need to download the SBML file to
your computer before running this notebook. PATRIC has the `genome
511145.183 <https://www.patricbrc.org/view/Genome/511145.183>`__ that
can be used to automatically reconstruct a model. Make sure you have
obtained a PATRIC authentication token (see the `modelseed
notebook <modelseed.ipynb>`__) before running this notebook.

First, use the ModelSEED web service to reconstruct and gap fill a model
for the 511145.183 genome. Note that it takes a few minutes for the
ModelSEED web service to reconstruct and gap fill the model.

.. code:: ipython2

    import mackinac
    mackinac.modelseed.ms_client.url = 'http://p3c.theseed.org/dev1/services/ProbModelSEED'
    mackinac.reconstruct_modelseed_model('511145.183')
    mackinac.gapfill_modelseed_model('511145.183')




.. parsed-literal::

    {'fba_count': 0,
     'gapfilled_reactions': 44,
     'gene_associated_reactions': 1565,
     'genome_ref': u'/mmundy@patricbrc.org/modelseed/511145.183/genome',
     'id': u'511145.183',
     'integrated_gapfills': 1,
     'name': u'Escherichia coli str. K-12 substr. MG1655',
     'num_biomass_compounds': 85,
     'num_biomasses': 1,
     'num_compartments': 2,
     'num_compounds': 1755,
     'num_genes': 1045,
     'num_reactions': 1609,
     'ref': u'/mmundy@patricbrc.org/modelseed/511145.183',
     'rundate': u'2017-03-15T20:25:03',
     'source': u'PATRIC',
     'source_id': u'511145.183',
     'template_ref': u'/chenry/public/modelsupport/templates/GramNegative.modeltemplate',
     'type': u'GenomeScale',
     'unintegrated_gapfills': 0}



Second, create a COBRA model from the ModelSEED model.

.. code:: ipython2

    ms_model = mackinac.create_cobra_model_from_modelseed_model('511145.183')

Now you can analyze the ModelSEED model using the functions in COBRApy.
You can optimize the model to check for growth on a complete medium.

.. code:: ipython2

    ms_model.optimize()




.. parsed-literal::

    <Solution 369.21 at 0x10e0b9310>



And get a summary of the optimization to see the metabolites consumed
and produced by the organism.

.. code:: ipython2

    ms_model.summary()


.. parsed-literal::

    IN FLUXES            OUT FLUXES           OBJECTIVES
    -------------------  -------------------  ------------
    cpd00007_e    1e+03  cpd00009_e    1e+03  bio1  369
    cpd00024_e    1e+03  cpd00011_e    1e+03
    cpd00054_e    1e+03  cpd00013_e    1e+03
    cpd00080_e    1e+03  cpd00027_e    1e+03
    cpd00082_e    1e+03  cpd00035_e    1e+03
    cpd00106_e    1e+03  cpd00036_e    1e+03
    cpd00130_e    1e+03  cpd00041_e    1e+03
    cpd00132_e    1e+03  cpd00047_e    1e+03
    cpd00179_e    1e+03  cpd00079_e    1e+03
    cpd00314_e    1e+03  cpd00092_e    1e+03
    cpd00438_e    1e+03  cpd00100_e    1e+03
    cpd00573_e    1e+03  cpd00138_e    1e+03
    cpd00653_e    1e+03  cpd00154_e    1e+03
    cpd00654_e    1e+03  cpd00159_e    1e+03
    cpd00794_e    1e+03  cpd00208_e    1e+03
    cpd01912_e  958      cpd00246_e    1e+03
    cpd00118_e  909      cpd00281_e    1e+03
    cpd00367_e  796      cpd00396_e    1e+03
    cpd00108_e  761      cpd00412_e    1e+03
    cpd03279_e  689      cpd00222_e  942
    cpd00235_e  541      cpd00139_e  918
    cpd00276_e  526      cpd00161_e  849
    cpd00588_e  441      cpd00122_e  848
    cpd17041_c  369      cpd03198_e  761
    cpd17042_c  369      cpd00277_e  689
    cpd17043_c  369      cpd00033_e  624
    cpd00117_e  346      cpd00023_e  448
    cpd00249_e  274      cpd11416_c  369
    cpd00107_e  170      cpd00067_e  236
    cpd00156_e  130      cpd00012_e  101
    cpd00039_e  115
    cpd00051_e   91.1
    cpd00322_e   89.3
    cpd00129_e   68.1
    cpd00311_e   61.7
    cpd00066_e   57.1
    cpd03847_e   55.4
    cpd00182_e   53.4
    cpd01914_e   48.3
    cpd00069_e   44.6
    cpd00210_e   31.5
    cpd01080_e   31.5
    cpd11584_e   29.3
    cpd00065_e   17.4
    cpd00184_e    5.82
    cpd00028_e    2.29
    cpd00355_e    2.29
    cpd00644_e    2.29
    cpd00030_e    1.14
    cpd00034_e    1.14
    cpd00048_e    1.14
    cpd00058_e    1.14
    cpd00063_e    1.14
    cpd00099_e    1.14
    cpd00149_e    1.14
    cpd00205_e    1.14
    cpd00254_e    1.14
    cpd00264_e    1.14
    cpd00305_e    1.14
    cpd10515_e    1.14
    cpd10516_e    1.14


For comparison, you can load the iJO1366 model from a SBML file. In the
cell below, change the input parameter to the path to the SBML file you
downloaded from BiGG.

.. code:: ipython2

    from cobra.io import read_sbml_model
    jo_model = read_sbml_model('iJO1366.xml')

You can check the number of reactions and metabolites in the model.

.. code:: ipython2

    len(jo_model.reactions)




.. parsed-literal::

    2583



.. code:: ipython2

    len(jo_model.metabolites)




.. parsed-literal::

    1805



You can optimize the model to check for growth on the medium defined in
the model.

.. code:: ipython2

    jo_model.optimize()




.. parsed-literal::

    <Solution 0.98 at 0x10ee810d0>



And get a summary of the optimization.

.. code:: ipython2

    jo_model.summary()


.. parsed-literal::

    IN FLUXES             OUT FLUXES           OBJECTIVES
    --------------------  -------------------  ----------------------
    o2_e       17.6       h2o_e     45.6       BIOMASS_Ec_i...  0.982
    nh4_e      10.6       co2_e     19.7
    glc__D_e   10         h_e        9.03
    pi_e        0.948     mththf_c   0.00044
    so4_e       0.248     5drib_c    0.000221
    k_e         0.192     4crsol_c   0.000219
    fe2_e       0.0158    amob_c     2e-06
    mg2_e       0.00852   meoh_e     2e-06
    ca2_e       0.00511
    cl_e        0.00511
    cu2_e       0.000697
    mn2_e       0.000679
    zn2_e       0.000335
    ni2_e       0.000317
    mobd_e      0.000127
    cobalt2_e   2.5e-05

