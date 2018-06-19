
Analyze models
--------------

Mackinac enables you to seamlessly work with PATRIC models in COBRApy.

The examples below show how to work with two models for Escherichia coli
str. K-12 substr. MG1655. The `iJO1366
model <http://bigg.ucsd.edu/models/iJO1366>`__ is a manually curated
model that is available from BiGG. You need to download the SBML file to
your computer. PATRIC has the `genome
511145.183 <https://www.patricbrc.org/view/Genome/511145.183>`__ that
can be used to reconstruct a model for the organism.

Use the PATRIC web service to reconstruct and gap fill a model from the
511145.183 genome and using a complete medium. Note that it takes a few
minutes for the PATRIC web service to reconstruct and gap fill the
model.

.. code:: ipython3

    import mackinac
    mackinac.create_patric_model('511145.183', 'Ecoli')




.. parsed-literal::

    {'fba_count': 0,
     'gapfilled_reactions': 58,
     'gene_associated_reactions': 1526,
     'genome_ref': '/mmundy@patricbrc.org/home/models/.Ecoli/genome',
     'id': 'Ecoli',
     'integrated_gapfills': 1,
     'name': 'Escherichia coli str. K-12 substr. MG1655',
     'num_biomass_compounds': 85,
     'num_biomasses': 1,
     'num_compartments': 2,
     'num_compounds': 1635,
     'num_genes': 1010,
     'num_reactions': 1584,
     'ref': '/mmundy@patricbrc.org/home/models/.Ecoli',
     'rundate': '2018-01-31T02:11:19Z',
     'source': 'PATRIC',
     'source_id': '.Ecoli',
     'template_ref': '/chenry/public/modelsupport/templates/GramNegative.modeltemplate',
     'type': 'GenomeScale',
     'unintegrated_gapfills': 0}



Create a COBRA model from the PATRIC model.

.. code:: ipython3

    patric_model = mackinac.create_cobra_model_from_patric_model('Ecoli')

Analyze the model using the functions in COBRApy. Check the number of
reactions and metabolites in the model.

.. code:: ipython3

    len(patric_model.reactions)




.. parsed-literal::

    1737



.. code:: ipython3

    len(patric_model.metabolites)




.. parsed-literal::

    1635



Optimize the model to check for growth on a complete medium.

.. code:: ipython3

    patric_sol = patric_model.optimize()

And get a summary of the optimization to see the metabolites consumed
and produced by the organism.

.. code:: ipython3

    patric_model.summary(patric_sol)


.. parsed-literal::

    IN FLUXES            OUT FLUXES           OBJECTIVES
    -------------------  -------------------  ------------
    cpd00007_e    1e+03  cpd00009_e    1e+03  bio1  373
    cpd00024_e    1e+03  cpd00011_e    1e+03
    cpd00080_e    1e+03  cpd00033_e    1e+03
    cpd00132_e    1e+03  cpd00100_e    1e+03
    cpd00246_e    1e+03  cpd00309_e    1e+03
    cpd00276_e    1e+03  cpd00108_e  963
    cpd00438_e  929      cpd00122_e  899
    cpd00367_e  846      cpd00182_e  875
    cpd00054_e  765      cpd00047_e  858
    cpd00794_e  655      cpd00027_e  800
    cpd00079_e  500      cpd00041_e  748
    cpd17041_c  373      cpd00249_e  712
    cpd17042_c  373      cpd00035_e  596
    cpd17043_c  373      cpd00106_e  436
    cpd00137_e  286      cpd11416_c  373
    cpd00107_e  172      cpd00067_e  314
    cpd00156_e  131      cpd00129_e  191
    cpd00039_e  116      cpd00036_e  144
    cpd00051_e   92.1    cpd00013_e  129
    cpd00322_e   90.2    cpd00012_e   99.5
    cpd00277_e   62.4    cpd00092_e   71.1
    cpd00066_e   57.7
    cpd03847_e   56
    cpd11590_e   48.8
    cpd00069_e   45
    cpd00154_e   32.7
    cpd00210_e   31.9
    cpd01080_e   31.8
    cpd11584_e   29.6
    cpd00065_e   17.6
    cpd00654_e    8.73
    cpd00184_e    5.88
    cpd01188_e    4.67
    cpd11606_e    3.47
    cpd00028_e    2.31
    cpd00644_e    2.31
    cpd00355_e    2.31
    cpd00030_e    1.16
    cpd00034_e    1.16
    cpd00048_e    1.16
    cpd00058_e    1.16
    cpd00063_e    1.16
    cpd00099_e    1.16
    cpd00149_e    1.16
    cpd00205_e    1.16
    cpd00254_e    1.16
    cpd00264_e    1.16
    cpd00305_e    1.16
    cpd10515_e    1.16
    cpd10516_e    1.16
    cpd00118_e    1.16


For comparison, load the iJO1366 model from a SBML file. In the cell
below, change the input parameter to the path to the SBML file you
downloaded from BiGG.

.. code:: ipython3

    from cobra.io import read_sbml_model
    jo_model = read_sbml_model('iJO1366.xml')

Check the number of reactions and metabolites in the model.

.. code:: ipython3

    len(jo_model.reactions)




.. parsed-literal::

    2583



.. code:: ipython3

    len(jo_model.metabolites)




.. parsed-literal::

    1805



Optimize the model to check for growth on the medium defined in the
model.

.. code:: ipython3

    jo_sol = jo_model.optimize()

And get a summary of the optimization.

.. code:: ipython3

    jo_model.summary(jo_sol)


.. parsed-literal::

    IN FLUXES             OUT FLUXES           OBJECTIVES
    --------------------  -------------------  ----------------------
    o2_e       17.6       h2o_e     45.6       BIOMASS_Ec_i...  0.982
    nh4_e      10.6       co2_e     19.7
    glc__D_e   10         h_e        9.03
    pi_e        0.948     mththf_c   0.00044
    so4_e       0.248     5drib_c    0.000221
    k_e         0.192     4crsol_c   0.000219
    fe2_e       0.0158    amob_c     1.96e-06
    mg2_e       0.00852   meoh_e     1.96e-06
    ca2_e       0.00511
    cl_e        0.00511
    cu2_e       0.000697
    mn2_e       0.000679
    zn2_e       0.000335
    ni2_e       0.000317
    mobd_e      0.000127
    cobalt2_e   2.46e-05

