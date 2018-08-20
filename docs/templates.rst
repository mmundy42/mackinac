
Work with template models
-------------------------

A template model is the source that is used to reconstruct a model for
an organism. A template model can be generic for a large set of
organisms or specific to a small set of organisms. A template model
contains the following components:

-  a list of reactions that are available for models created from the
   template model
-  a list of complexes that link reactions to roles
-  a list of roles that match the annotations on features of a genome
-  a list of biomass reactions
-  a list of cellular compartments

Template models are built from a set of data files. Details on the
format of the data files are available in the
`ModelSEEDDatabase <https://github.com/ModelSEED/ModelSEEDDatabase>`__
repository.

.. code:: ipython3

    import mackinac
    import pkg_resources
    from os import makedirs
    from os.path import expanduser, join, exists

When creating models using the ModelSEED and PATRIC web services, a
template model is automatically selected based on an organism's genome.
Get the list of template models used by the services with this command:

.. code:: ipython3

    mackinac.list_workspace_objects('/chenry/public/modelsupport/templates', print_output=True)


.. parsed-literal::

    Contents of /chenry/public/modelsupport/templates:
    -rr chenry    	  27225828	2016-06-23T15:25:46Z	modeltemplate	/chenry/public/modelsupport/templates/Core.modeltemplate
    -rr chenry    	  19776723	2016-06-27T21:31:36Z	modeltemplate	/chenry/public/modelsupport/templates/newplant.modeltemplate
    -rr chenry    	  73533708	2016-09-08T07:17:41Z	modeltemplate	/chenry/public/modelsupport/templates/FullBiomass.modeltemplate
    -rr chenry    	  26559014	2016-11-16T06:52:49Z	modeltemplate	/chenry/public/modelsupport/templates/GramNegative.modeltemplate
    -rr chenry    	  26564644	2016-11-16T06:55:11Z	modeltemplate	/chenry/public/modelsupport/templates/GramPositive.modeltemplate
    -rr seaver    	  20808794	2017-04-14T19:34:42Z	modeltemplate	/chenry/public/modelsupport/templates/plant.modeltemplate
    -rr chenry    	  26564644	2017-08-10T15:30:06Z	modeltemplate	/chenry/public/modelsupport/templates/GramPosModelTemplate
    -rr chenry    	  26559014	2017-08-10T15:30:25Z	modeltemplate	/chenry/public/modelsupport/templates/GramNegModelTemplate
    -rr chenry    	  27225828	2017-08-10T15:31:17Z	modeltemplate	/chenry/public/modelsupport/templates/CoreModelTemplate
    -rr seaver    	  22704731	2018-07-27T19:57:27Z	modeltemplate	/chenry/public/modelsupport/templates/PlantModelTemplate
    -rr seaver    	     71213	2018-08-16T18:37:41Z	modeltemplate	/chenry/public/modelsupport/templates/PlastidialSandboxModelTemplate


Mackinac provides functions for working with ModelSEED and PATRIC
template models. Create a COBRA model from a template model with
``create_universal_model()``. The COBRA model can be used as a universal
model for the organisms represented by the template model.

.. code:: ipython3

    gramneg = mackinac.create_universal_model('/chenry/public/modelsupport/templates/GramNegModelTemplate')

Generate the data files from a template model with
``save_modelseed_template_model()``.

.. code:: ipython3

    template_folder = join(expanduser('~'), 'mackinac_templates', 'GramNeg')
    if not exists(template_folder):
        makedirs(template_folder)
    mackinac.save_modelseed_template_model('/chenry/public/modelsupport/templates/GramNegModelTemplate', template_folder)

Mackinac template models
~~~~~~~~~~~~~~~~~~~~~~~~

Mackinac supports creating template models from data files. Mackinac
includes data files for building a template for:

-  gram negative and gram positive bacteria from the expanded ModelSEED
   biochemistry
-  gram negative and gram positive bacteria from the original ModelSEED
   biochemistry

A template model selects reactions from the complete (or universal) set
of reactions and metabolites in the ModelSEED biochemistry. The
``universal`` folder contains the data files that define universal
reactions and metabolites.

The ``bacteria`` folder contains the data files for the expanded
biochemistry that define the reactions and known features (or functional
roles) for bacterial organisms along with the definition for creating a
biomass reaction for gram negative and gram positive bacteria. The
``original`` folder contains the data files for the original
biochemistry.

Set variables to specify the path to the folders with the data files for
a template model.

.. code:: ipython3

    universal_folder = pkg_resources.resource_filename('mackinac', 'data/modelseed/universal')
    bacteria_folder = pkg_resources.resource_filename('mackinac', 'data/modelseed/bacteria')

Create a template model with ``create_template_model()``. You need to
provide the path to the folder with the universal reaction and
metabolite data files, the path to the folder with the template model
data files, an ID for the template model, and a name for the template
model. Create a template model for bacteria using the expanded ModelSEED
biochemistry using this command:

.. code:: ipython3

    template = mackinac.create_template_model(universal_folder, bacteria_folder, 'bacteria', 'Bacteria template')

You can find the relationship between roles and reactions with two
methods. Show the reactions that are associated with a list of roles
using ``map_role_to_reaction()``.

.. code:: ipython3

    template.map_role_to_reaction(['ftr01232', 'ftr05342', 'ftr05348', 'ftr34574'])




.. parsed-literal::

    {'ftr01232': {'name': 'Inorganic pyrophospatase PpaX',
      'reactions': {'rxn00001': {'complex_id': 'cpx01833',
        'name': 'diphosphate phosphohydrolase'}}},
     'ftr05342': {'name': 'Inorganic pyrophosphatase (EC 3.6.1.1)',
      'reactions': {'rxn00001': {'complex_id': 'cpx01835',
        'name': 'diphosphate phosphohydrolase'}}},
     'ftr05348': {'name': 'Manganese-dependent inorganic pyrophosphatase (EC 3.6.1.1)',
      'reactions': {'rxn00001': {'complex_id': 'cpx01834',
        'name': 'diphosphate phosphohydrolase'}}},
     'ftr34574': {'name': 'inorganic diphosphatase (EC 3.6.1.1)',
      'reactions': {'rxn00001': {'complex_id': 'cpx34574',
        'name': 'diphosphate phosphohydrolase'}}}}



Show the roles that are associated with a list of reactions with
``map_reaction_to_role()``.

.. code:: ipython3

    template.map_reaction_to_role(['rxn00001', 'rxn00002', 'rxn00003'])




.. parsed-literal::

    {'rxn00001': {'name': 'diphosphate phosphohydrolase',
      'roles': {'ftr01232': {'complex_id': 'cpx01833',
        'name': 'Inorganic pyrophospatase PpaX'},
       'ftr05342': {'complex_id': 'cpx01835',
        'name': 'Inorganic pyrophosphatase (EC 3.6.1.1)'},
       'ftr05348': {'complex_id': 'cpx01834',
        'name': 'Manganese-dependent inorganic pyrophosphatase (EC 3.6.1.1)'},
       'ftr34574': {'complex_id': 'cpx34574',
        'name': 'inorganic diphosphatase (EC 3.6.1.1)'}}},
     'rxn00002': {'name': 'urea-1-carboxylate amidohydrolase',
      'roles': {'ftr02686': {'complex_id': 'cpx01285',
        'name': 'Allophanate hydrolase (EC 3.5.1.54)'},
       'ftr11228': {'complex_id': 'cpx01286',
        'name': 'Allophanate hydrolase 2 subunit 1 (EC 3.5.1.54)'},
       'ftr11229': {'complex_id': 'cpx01286',
        'name': 'Allophanate hydrolase 2 subunit 2 (EC 3.5.1.54)'}}},
     'rxn00003': {'name': 'pyruvate:pyruvate acetaldehydetransferase (decarboxylating)',
      'roles': {}}}



Note that some reactions are not associated with a role.

You can export a template model to a COBRA model or a reaction list
file. Create a COBRA model from the template model with
``to_cobra_model()``.

.. code:: ipython3

    cobra_model = template.to_cobra_model()

A reaction list file is used as the universal model for the
``generateSUXMatrix`` function used by the fastgapfill algorithm in the
COBRA Toolbox. The ``to_reaction_list_file()`` creates two output files,
a reaction list file and a metabolite dictionary file. Each line of the
reaction list file has the definition of a reaction. For example:

::

    rxn00001: 1 cpd00001_0 + 1 cpd00012_0 <=> 2 cpd00009_0 + 1 cpd00067_0

The reaction list file is specified as the ``KEGGFilename`` parameter of
``generateSUXMatrix``.

Each line of the metabolite dictionary file maps a model metabolite ID
to the metabolite ID in the universal model. The metabolite dictionary
file has two columns (separated by tab) where the first column is the
model metabolite ID and the second column is the template model
metabolite ID. For example:

::

    cpd00001_c  cpd00001_0
    cpd00012_c  cpd00012_0
    cpd00009_c  cpd00009_0
    cpd00067_c  cpd00067_0

The metabolite dictionary file is specified as the ``dictionary``
parameter of ``generateSUXMatrix``.

Create a reaction list file with ``to_reaction_list_file()``. Note that
some reactions from the template model are not included in the reaction
list file because the coefficients are not valid for fastgapfill or the
reaction is unbalanced.

.. code:: ipython3

    template_folder = join(expanduser('~'), 'mackinac_templates', 'bacteria')
    if not exists(template_folder):
        makedirs(template_folder)
    template.to_reaction_list_file(join(template_folder, 'reactions.txt'), join(template_folder, 'dictionary.tsv'))


.. parsed-literal::

    2018-08-20 11:16:38,877 WARNING Skipped reaction rxn00734 with invalid coefficient: 0.5 cpd00007_0 + 1 cpd00009_0 + 1 cpd00067_0 + 1 cpd00094_0 <=> 1 cpd00001_0 + 1 cpd00011_0 + 1 cpd01844_0
    2018-08-20 11:16:38,981 WARNING Skipped reaction rxn05294 with invalid coefficient: 0.884 cpd00115_0 + 0.6692 cpd00241_0 + 0.6684 cpd00356_0 + 0.8807 cpd00357_0 <=> 3.1023 cpd00012_0 + 1 cpd11461_0
    2018-08-20 11:16:38,981 WARNING Skipped reaction rxn05295 with invalid coefficient: 0.7706 cpd00002_0 + 0.9496 cpd00038_0 + 0.5853 cpd00052_0 + 0.6331 cpd00062_0 <=> 2.9386 cpd00012_0 + 1 cpd11462_0
    2018-08-20 11:16:38,982 WARNING Skipped reaction rxn05296 with invalid coefficient: 0.4928 cpd00023_0 + 0.7723 cpd00033_0 + 0.5051 cpd00035_0 + 0.6114 cpd00039_0 + 0.2801 cpd00041_0 + 0.3653 cpd00051_0 + 0.4928 cpd00053_0 + 0.4091 cpd00054_0 + 0.2145 cpd00060_0 + 0.1028 cpd00065_0 + 0.3329 cpd00066_0 + 0.2097 cpd00069_0 + 0.1073 cpd00084_0 + 0.6555 cpd00107_0 + 0.1546 cpd00119_0 + 0.3041 cpd00129_0 + 0.2801 cpd00132_0 + 0.5807 cpd00156_0 + 0.3526 cpd00161_0 + 0.5107 cpd00322_0 <=> 1 cpd11463_0
    2018-08-20 11:16:39,024 WARNING Skipped reaction rxn08287 with invalid coefficient: 0.5 cpd00007_0 + 2 cpd00067_0 + 1 cpd15499_0 <=> 1 cpd00001_0 + 2 cpd00067_1 + 1 cpd15500_0
    2018-08-20 11:16:39,025 WARNING Skipped reaction rxn08288 with invalid coefficient: 0.5 cpd00007_0 + 2 cpd00067_0 + 1 cpd15561_0 <=> 1 cpd00001_0 + 2 cpd00067_1 + 1 cpd15560_0
    2018-08-20 11:16:39,037 WARNING Skipped reaction rxn09040 with invalid coefficient: 0.5 cpd00007_0 + 1 cpd15361_0 <=> 1 cpd15360_0
    2018-08-20 11:16:39,038 WARNING Skipped reaction rxn09042 with invalid coefficient: 0.5 cpd00007_0 + 1 cpd03446_0 <=> 1 cpd15359_0
    2018-08-20 11:16:39,039 WARNING Skipped reaction rxn09044 with invalid coefficient: 0.5 cpd00007_0 + 1 cpd03444_0 <=> 1 cpd03445_0
    2018-08-20 11:16:39,048 WARNING Skipped reaction rxn09566 with invalid coefficient: 2 cpd00001_0 + 0.5 cpd00007_0 + 1 cpd00013_0 + 1 cpd00215_0 <=> 2 cpd00025_0 + 1 cpd00419_0
    2018-08-20 11:16:39,049 WARNING Skipped reaction rxn09568 with invalid coefficient: 0.5 cpd00007_0 + 1 cpd15203_0 <=> 1 cpd15198_0
    2018-08-20 11:16:39,049 WARNING Skipped reaction rxn09570 with invalid coefficient: 0.5 cpd00007_0 + 1 cpd15202_0 <=> 1 cpd15199_0
    2018-08-20 11:16:39,050 WARNING Skipped reaction rxn09571 with invalid coefficient: 0.5 cpd00007_0 + 1 cpd15201_0 <=> 1 cpd15200_0
    2018-08-20 11:16:39,055 WARNING Skipped reaction rxn09997 with invalid coefficient: 1 cpd00001_0 + 1 cpd02140_0 <=> 0.5 cpd00007_0 + 1 cpd00009_0 + 1 cpd00067_0 + 1 cpd00229_0 + 1 cpd00939_0
    2018-08-20 11:16:39,056 WARNING Skipped reaction rxn10043 with invalid coefficient: 0.5 cpd00007_0 + 6 cpd00067_0 + 2 cpd00110_0 <=> 1 cpd00001_0 + 4 cpd00067_1 + 2 cpd00109_0
    2018-08-20 11:16:39,057 WARNING Skipped reaction rxn10045 with invalid coefficient: 0.5 cpd00007_0 + 2 cpd00067_0 + 1 cpd11451_0 <=> 1 cpd00001_0 + 2 cpd00067_1 + 1 cpd11606_0
    2018-08-20 11:16:39,057 WARNING Skipped reaction rxn10046 with invalid coefficient: 0.5 cpd00007_0 + 4 cpd00067_0 + 1 cpd11451_0 <=> 1 cpd00001_0 + 4 cpd00067_1 + 1 cpd11606_0
    2018-08-20 11:16:39,059 WARNING Skipped reaction rxn10113 with invalid coefficient: 0.5 cpd00007_0 + 2.5 cpd00067_0 + 1 cpd15561_0 <=> 1 cpd00001_0 + 2.5 cpd00067_1 + 1 cpd15560_0
    2018-08-20 11:16:39,061 WARNING Skipped reaction rxn10200 with invalid coefficient: 0.004866 cpd15746_0 + 0.001122 cpd15747_0 + 0.001761 cpd15748_0 + 0.003687 cpd15749_0 + 0.008667 cpd15750_0 + 0.0005365 cpd15751_0 + 0.009356 cpd15752_0 + 0.01585 cpd15753_0 + 0.002264 cpd15754_0 + 0.002269 cpd15755_0 + 0.0005201 cpd15756_0 + 0.0008257 cpd15757_0 + 0.001724 cpd15758_0 + 0.004053 cpd15759_0 + 0.0002488 cpd15760_0 + 0.00435 cpd15761_0 + 0.00737 cpd15762_0 + 0.001056 cpd15763_0 + 0.002032 cpd15764_0 + 0.0004655 cpd15765_0 + 0.0007401 cpd15766_0 + 0.001545 cpd15767_0 + 0.003631 cpd15768_0 + 0.0002227 cpd15769_0 + 0.003895 cpd15770_0 + 0.006599 cpd15771_0 + 0.0009457 cpd15772_0 + 0.006441 cpd15773_0 + 0.00148 cpd15774_0 + 0.002339 cpd15775_0 + 0.004889 cpd15776_0 + 0.01149 cpd15777_0 + 0.0007078 cpd15778_0 + 0.01236 cpd15779_0 + 0.02094 cpd15780_0 + 0.002997 cpd15781_0 <=> 1 cpd15670_0
    2018-08-20 11:16:39,075 WARNING Skipped reaction rxn10792 with invalid coefficient: 0.5 cpd00007_0 + 2 cpd00067_0 + 2 cpd00110_0 <=> 1 cpd00001_0 + 2 cpd00109_0
    2018-08-20 11:16:39,080 WARNING Skipped reaction rxn11349 with invalid coefficient: 0.5 cpd00007_0 + 1 cpd00868_0 <=> 1 cpd00011_0 + 1 cpd00489_0
    2018-08-20 11:16:39,082 WARNING Skipped reaction rxn11545 with invalid coefficient: 0.5 cpd00007_0 + 1 cpd00067_0 + 1 cpd03420_0 <=> 1 cpd03833_0
    2018-08-20 11:16:39,090 WARNING Skipped reaction rxn11921 with invalid coefficient: 6.06e-05 cpd15529_0 + 5.57e-05 cpd15531_0 + 5.15e-05 cpd15533_0 + 5.78e-05 cpd15536_0 + 5.33e-05 cpd15538_0 + 4.95e-05 cpd15540_0 + 5.35e-05 cpd15695_0 + 5.35e-05 cpd15696_0 + 6.06e-05 cpd15697_0 + 5.8e-05 cpd15698_0 + 5.8e-05 cpd15699_0 + 5.57e-05 cpd15700_0 + 5.14e-05 cpd15722_0 + 5.14e-05 cpd15723_0 + 5.78e-05 cpd15724_0 + 5.55e-05 cpd15725_0 + 5.55e-05 cpd15726_0 + 5.33e-05 cpd15727_0 + 2.85e-05 cpd15791_0 + 3.11e-05 cpd15792_0 + 2.63e-05 cpd15793_0 + 2.74e-05 cpd15794_0 + 2.74e-05 cpd15795_0 + 2.97e-05 cpd15797_0 + 2.97e-05 cpd15798_0 + 2.85e-05 cpd15799_0 <=> 1 cpd16488_0
    2018-08-20 11:16:39,090 WARNING Skipped reaction rxn11922 with invalid coefficient: 0.000129 cpd15652_0 + 0.000505 cpd15665_0 <=> 0.000505 cpd15666_0 + 1 cpd16489_0
    2018-08-20 11:16:39,091 WARNING Skipped reaction rxn11923 with invalid coefficient: 1.25e-05 cpd11459_0 + 0.000168 cpd15665_0 + 1.99e-05 cpd15667_0 + 1.44e-05 cpd15668_0 + 1.07e-05 cpd15669_0 + 0.167 cpd15670_0 <=> 0.000213 cpd15666_0 + 1 cpd16490_0
    2018-08-20 11:16:39,096 WARNING Skipped reaction rxn12295 with invalid coefficient: 0.5 cpd00007_0 + 1 cpd01433_0 <=> 1 cpd00067_0 + 1 cpd00075_0 + 1 cpd00178_0
    2018-08-20 11:16:39,102 WARNING Skipped reaction rxn12747 with invalid coefficient: 0.5 cpd00007_0 + 1 cpd00218_0 <=> 1 cpd00752_0
    2018-08-20 11:16:39,105 WARNING Skipped reaction rxn13204 with invalid coefficient: 0.5 cpd00007_0 + 1 cpd09429_0 <=> 1 cpd03092_0
    2018-08-20 11:16:39,111 WARNING Skipped reaction rxn13688 with invalid coefficient: 0.5 cpd00007_0 + 4 cpd00067_0 + 2 cpd00110_0 <=> 1 cpd00001_0 + 2 cpd00067_1 + 2 cpd00109_0
    2018-08-20 11:16:39,114 WARNING Skipped reaction rxn13782 with no reactants
    2018-08-20 11:16:39,114 WARNING Skipped reaction rxn13783 with no reactants
    2018-08-20 11:16:39,115 WARNING Skipped reaction rxn13784 with no reactants
    2018-08-20 11:16:39,118 WARNING Skipped reaction rxn14003 with no reactants
    2018-08-20 11:16:39,119 WARNING Skipped reaction rxn14046 with no reactants
    2018-08-20 11:16:39,121 WARNING Skipped reaction rxn14111 with no reactants
    2018-08-20 11:16:39,122 WARNING Skipped reaction rxn14154 with no reactants
    2018-08-20 11:16:39,125 WARNING Skipped reaction rxn14266 with no reactants
    2018-08-20 11:16:39,126 WARNING Skipped reaction rxn14312 with no reactants
    2018-08-20 11:16:39,127 WARNING Skipped reaction rxn14325 with no reactants
    2018-08-20 11:16:39,129 WARNING Skipped reaction rxn14393 with no reactants
    2018-08-20 11:16:39,130 WARNING Skipped reaction rxn14415 with invalid coefficient: 0.5 cpd00007_0 + 4 cpd00067_0 + 2 cpd18074_0 <=> 1 cpd00001_0 + 2 cpd00067_1 + 2 cpd18072_0
    2018-08-20 11:16:39,130 WARNING Skipped reaction rxn14416 with invalid coefficient: 0.5 cpd00007_0 + 6 cpd00067_0 + 1 cpd18074_0 <=> 1 cpd00001_0 + 4 cpd00067_1 + 1 cpd18072_0
    2018-08-20 11:16:39,131 WARNING Skipped reaction rxn14419 with invalid coefficient: 0.5 cpd00007_0 + 4 cpd00067_0 + 1 cpd18076_0 <=> 1 cpd00001_0 + 2 cpd00067_1 + 1 cpd18075_0
    2018-08-20 11:16:39,132 WARNING Skipped reaction rxn14422 with invalid coefficient: 0.5 cpd00007_0 + 4 cpd00067_0 + 1 cpd18078_0 <=> 1 cpd00001_0 + 2 cpd00067_1 + 1 cpd18077_0
    2018-08-20 11:16:39,132 WARNING Skipped reaction rxn14424 with invalid coefficient: 0.5 cpd00007_0 + 4 cpd00067_0 + 1 cpd18080_0 <=> 1 cpd00001_0 + 2 cpd00067_1 + 1 cpd18079_0
    2018-08-20 11:16:39,133 WARNING Skipped reaction rxn14426 with invalid coefficient: 0.5 cpd00007_0 + 4 cpd00067_0 + 1 cpd18082_0 <=> 1 cpd00001_0 + 2 cpd00067_1 + 1 cpd18081_0
    2018-08-20 11:16:39,146 WARNING Skipped reaction rxn15543 with no reactants
    2018-08-20 11:16:39,185 WARNING Skipped reaction rxn17792 with no reactants
    2018-08-20 11:16:39,188 WARNING Skipped reaction rxn17932 with no reactants
    2018-08-20 11:16:39,189 WARNING Skipped reaction rxn17942 with no reactants
    2018-08-20 11:16:39,190 WARNING Skipped reaction rxn17944 with no reactants
    2018-08-20 11:16:39,191 WARNING Skipped reaction rxn17989 with no reactants
    2018-08-20 11:16:39,192 WARNING Skipped reaction rxn17996 with no reactants
    2018-08-20 11:16:39,193 WARNING Skipped reaction rxn18001 with no reactants
    2018-08-20 11:16:39,194 WARNING Skipped reaction rxn18027 with no reactants
    2018-08-20 11:16:39,195 WARNING Skipped reaction rxn18033 with no reactants
    2018-08-20 11:16:39,195 WARNING Skipped reaction rxn18034 with no reactants
    2018-08-20 11:16:39,200 WARNING Skipped reaction rxn18129 with no reactants
    2018-08-20 11:16:39,228 WARNING Skipped reaction rxn18938 with no reactants
    2018-08-20 11:16:39,229 WARNING Skipped reaction rxn18942 with no reactants
    2018-08-20 11:16:39,229 WARNING Skipped reaction rxn18944 with no reactants
    2018-08-20 11:16:39,230 WARNING Skipped reaction rxn18946 with no reactants
    2018-08-20 11:16:39,230 WARNING Skipped reaction rxn18947 with no reactants
    2018-08-20 11:16:39,231 WARNING Skipped reaction rxn18949 with no reactants
    2018-08-20 11:16:39,231 WARNING Skipped reaction rxn18951 with no reactants
    2018-08-20 11:16:39,232 WARNING Skipped reaction rxn18952 with no reactants
    2018-08-20 11:16:39,274 WARNING Skipped reaction rxn21993 with no reactants
    2018-08-20 11:16:39,339 WARNING Skipped reaction rxn26399 with no reactants
    2018-08-20 11:16:39,340 WARNING Skipped reaction rxn26408 with no reactants
    2018-08-20 11:16:39,381 WARNING Skipped reaction rxn30282 with no reactants
    2018-08-20 11:16:39,382 WARNING Skipped reaction rxn30283 with no reactants
    2018-08-20 11:16:39,383 WARNING Skipped reaction rxn30284 with no reactants
    2018-08-20 11:16:39,383 WARNING Skipped reaction rxn30285 with no products
    2018-08-20 11:16:39,384 WARNING Skipped reaction rxn30286 with no reactants
    2018-08-20 11:16:39,386 WARNING Skipped reaction rxn30421 with invalid coefficient: 1 cpd00001_0 + 0.005 cpd11624_0 <=> 1 cpd00067_0 + 0.27 cpd00214_0 + 0.5 cpd00507_0 + 0.05 cpd01080_0 + 0.02 cpd01107_0 + 0.06 cpd01741_0 + 0.1 cpd03847_0 + 0.17 cpd15237_0 + 0.24 cpd15269_0 + 0.09 cpd15270_0
    2018-08-20 11:16:39,387 WARNING Skipped reaction rxn30462 with invalid coefficient: 1 cpd00001_0 + 0.02 cpd29711_0 <=> 1 cpd00046_0 + 2 cpd00067_0 + 0.02 cpd29721_0
    2018-08-20 11:16:39,387 WARNING Skipped reaction rxn30469 with invalid coefficient: 1 cpd00001_0 + 1 cpd00002_0 + 0.5 cpd00004_0 + 1 cpd03915_0 <=> 0.5 cpd00003_0 + 1 cpd00009_0 + 1 cpd00012_0 + 1.5 cpd00067_0 + 1 cpd03916_0
    2018-08-20 11:16:39,388 WARNING Skipped reaction rxn30475 with invalid coefficient: 1 cpd00008_0 + 1 cpd00067_0 + 0.02 cpd29721_0 <=> 1 cpd00002_0 + 0.02 cpd29706_0
    2018-08-20 11:16:39,389 WARNING Skipped reaction rxn30476 with invalid coefficient: 1 cpd00012_0 + 0.02 cpd29711_0 <=> 1 cpd00052_0 + 1 cpd00067_0 + 0.02 cpd29721_0
    2018-08-20 11:16:39,390 WARNING Skipped reaction rxn30489 with invalid coefficient: 1 cpd00001_0 + 0.02 cpd29708_0 <=> 1 cpd00067_0 + 0.69 cpd00214_0 + 0.02 cpd01080_0 + 1 cpd02090_0 + 0.13 cpd03847_0 + 0.04 cpd15237_0 + 0.03 cpd15269_0 + 0.03 cpd15270_0 + 0.06 cpd29719_0
    2018-08-20 11:16:39,391 WARNING Skipped reaction rxn30490 with invalid coefficient: 1 cpd00001_0 + 0.02 cpd29707_0 <=> 1 cpd00067_0 + 0.69 cpd00214_0 + 1 cpd00908_0 + 0.02 cpd01080_0 + 0.13 cpd03847_0 + 0.04 cpd15237_0 + 0.03 cpd15269_0 + 0.03 cpd15270_0 + 0.06 cpd29719_0
    2018-08-20 11:16:39,391 WARNING Skipped reaction rxn30492 with invalid coefficient: 5 cpd00008_0 + 5 cpd00014_0 + 9 cpd00067_0 + 1 cpd19245_0 + 0.04 cpd29706_0 + 1 cpd29716_0 <=> 2 cpd00002_0 + 2 cpd00026_0 + 1 cpd00037_0 + 2 cpd00043_0 + 1 cpd03587_0 + 3 cpd03831_0 + 1 cpd15576_0 + 0.04 cpd29722_0
    2018-08-20 11:16:39,392 WARNING Skipped reaction rxn30510 with invalid coefficient: 1 cpd00001_0 + 0.02 cpd29721_0 <=> 1 cpd00009_0 + 0.02 cpd29706_0
    2018-08-20 11:16:39,393 WARNING Skipped reaction rxn30511 with invalid coefficient: 1 cpd00080_0 + 0.08 cpd15239_0 + 0.04 cpd15268_0 + 0.06 cpd15271_0 + 1.38 cpd15277_0 + 0.26 cpd27551_0 + 0.06 cpd29680_0 + 0.12 cpd29720_0 <=> 2 cpd11493_0 + 0.02 cpd29721_0
    2018-08-20 11:16:39,394 WARNING Skipped reaction rxn30515 with invalid coefficient: 1 cpd00001_0 + 0.02 cpd29725_0 <=> 1 cpd00009_0 + 0.02 cpd29724_0
    2018-08-20 11:16:39,394 WARNING Skipped reaction rxn30516 with invalid coefficient: 1 cpd00080_0 + 0.02 cpd29711_0 <=> 1 cpd00046_0 + 1 cpd00067_0 + 0.02 cpd29725_0
    2018-08-20 11:16:39,395 WARNING Skipped reaction rxn30517 with invalid coefficient: 1 cpd00001_0 + 0.02 cpd29724_0 <=> 1 cpd00067_0 + 0.69 cpd00214_0 + 0.02 cpd01080_0 + 0.13 cpd03847_0 + 0.04 cpd15237_0 + 0.03 cpd15269_0 + 0.03 cpd15270_0 + 0.02 cpd29708_0 + 0.06 cpd29719_0
    2018-08-20 11:16:39,395 WARNING Skipped reaction rxn30518 with invalid coefficient: 1 cpd00001_0 + 0.02 cpd29722_0 <=> 1 cpd00067_0 + 0.69 cpd00214_0 + 0.02 cpd01080_0 + 0.13 cpd03847_0 + 0.04 cpd15237_0 + 0.03 cpd15269_0 + 0.03 cpd15270_0 + 0.02 cpd29707_0 + 0.06 cpd29719_0
    2018-08-20 11:16:39,396 WARNING Skipped reaction rxn30520 with invalid coefficient: 1 cpd00067_0 + 0.02 cpd29726_0 <=> 1 cpd00011_0 + 0.02 cpd29722_0
    2018-08-20 11:16:39,396 WARNING Skipped reaction rxn30521 with invalid coefficient: 1 cpd00054_0 + 0.02 cpd29711_0 <=> 1 cpd00046_0 + 1 cpd00067_0 + 0.02 cpd29726_0
    2018-08-20 11:16:39,412 WARNING Skipped reaction rxn31330 with invalid coefficient: 1 cpd00001_0 + 2.4 cpd00002_0 + 1 cpd00003_0 <=> 1 cpd00004_0 + 0.5 cpd00007_0 + 2.4 cpd00008_0 + 2.4 cpd00009_0 + 1 cpd00067_0
    2018-08-20 11:16:39,413 WARNING Skipped reaction rxn31331 with invalid coefficient: 1 cpd00001_0 + 1.5 cpd00002_0 + 1 cpd00015_0 <=> 0.5 cpd00007_0 + 1.5 cpd00008_0 + 1.5 cpd00009_0 + 1 cpd00982_0
    2018-08-20 11:16:39,417 WARNING Skipped reaction rxn31586 with invalid coefficient: 0.378 cpd00023_0 + 0.74 cpd00033_0 + 0.624 cpd00035_0 + 0.38 cpd00039_0 + 0.417 cpd00041_0 + 0.319 cpd00051_0 + 0.529 cpd00054_0 + 0.372 cpd00060_0 + 0.272 cpd00065_0 + 0.336 cpd00066_0 + 0.307 cpd00069_0 + 0.423 cpd00107_0 + 0.358 cpd00119_0 + 0.483 cpd00129_0 + 0.474 cpd00156_0 + 0.467 cpd00161_0 + 0.423 cpd00322_0 + 0.231 cpd00381_0 <=> 1 cpd11612_0
    2018-08-20 11:16:39,418 WARNING Skipped reaction rxn31587 with invalid coefficient: 0.146 cpd00076_0 + 0.111 cpd00082_0 + 0.067 cpd00105_0 + 0.055 cpd00108_0 + 0.055 cpd00138_0 + 0.086 cpd00472_0 + 0.278 cpd19001_0 + 2.33 cpd29869_0 <=> 1 cpd29189_0
    2018-08-20 11:16:39,418 WARNING Skipped reaction rxn31594 with invalid coefficient: 1 cpd29869_0 <=> 0.144 cpd00108_0 + 0.3 cpd00138_0 + 1.248 cpd00154_0 + 0.166 cpd00164_0 + 0.548 cpd00185_0 + 0.166 cpd00280_0 + 3.253 cpd19001_0
    2018-08-20 11:16:39,419 WARNING Skipped reaction rxn31596 with invalid coefficient: 1 cpd16817_0 <=> 1.466 cpd23060_0 + 0.373 cpd26606_0 + 1.035 cpd29863_0 + 0.157 cpd29864_0 + 0.034 cpd29867_0 + 0.093 cpd29868_0
    2018-08-20 11:16:39,420 WARNING Skipped reaction rxn31598 with invalid coefficient: 6.799 cpd11463_0 + 0.781 cpd11612_0 + 0.061 cpd29873_0 <=> 1 cpd03612_0
    2018-08-20 11:16:39,420 WARNING Skipped reaction rxn31599 with invalid coefficient: 1 cpd29873_0 <=> 0.246 cpd00002_0 + 0.239 cpd00038_0 + 0.259 cpd00052_0 + 0.258 cpd00062_0 + 0.254 cpd00115_0 + 0.246 cpd00241_0 + 0.268 cpd00356_0 + 0.259 cpd00357_0
    2018-08-20 11:16:39,421 WARNING Skipped reaction rxn31600 with invalid coefficient: 1 cpd29874_0 <=> 1.515 cpd00032_0 + 0.676 cpd00040_0 + 0.746 cpd00130_0 + 1.562 cpd00137_0 + 0.555 cpd00180_0 + 1.724 cpd00331_0
    2018-08-20 11:16:39,422 WARNING Skipped reaction rxn31601 with invalid coefficient: 1.527 cpd00023_0 + 0.044 cpd00033_0 + 1.153 cpd00035_0 + 5.7e-05 cpd00039_0 + 0.414 cpd00041_0 + 0.096 cpd00051_0 + 0.612 cpd00054_0 + 0.123 cpd00060_0 + 0.004 cpd00065_0 + 0.313 cpd00066_0 + 0.244 cpd00069_0 + 1.509 cpd00107_0 + 0.091 cpd00119_0 + 0.762 cpd00129_0 + 0.249 cpd00156_0 + 0.175 cpd00161_0 + 0.464 cpd00322_0 + 0.031 cpd00381_0 <=> 1 cpd11463_0
    2018-08-20 11:16:39,433 WARNING Skipped reaction rxn33680 with invalid coefficient: 1 cpd00004_0 + 0.5 cpd00007_0 + 1 cpd00008_0 + 1 cpd00009_0 + 2 cpd00067_0 <=> 2 cpd00001_0 + 1 cpd00002_0 + 1 cpd00003_0
    2018-08-20 11:16:39,435 WARNING Skipped reaction rxn33878 with invalid coefficient: 0.5 cpd00007_0 + 1 cpd00139_0 <=> 1 cpd00001_0 + 1 cpd00040_0
    2018-08-20 11:16:39,436 WARNING Skipped reaction rxn33886 with invalid coefficient: 1 cpd00005_0 + 0.5 cpd00007_0 + 1 cpd00067_0 <=> 1 cpd00001_0 + 1 cpd00006_0 + 4 cpd11632_1
    2018-08-20 11:16:39,436 WARNING Skipped reaction rxn33887 with no reactants
    2018-08-20 11:16:39,440 WARNING Skipped reaction rxn34003 with invalid coefficient: 0.5 cpd00007_0 + 2 cpd00042_0 <=> 1 cpd00001_0 + 1 cpd00111_0
    2018-08-20 11:16:39,441 WARNING Skipped reaction rxn34006 with invalid coefficient: 0.5 cpd00007_0 + 1 cpd00081_0 <=> 1 cpd00048_0 + 1 cpd00067_0
    2018-08-20 11:16:39,442 WARNING Skipped reaction rxn34028 with invalid coefficient: 0.5 cpd00007_0 + 1 cpd00067_0 + 1 cpd00343_0 <=> 2 cpd00001_0 + 1 cpd00247_0
    2018-08-20 11:16:39,446 WARNING Skipped reaction rxn34326 with no reactants
    2018-08-20 11:16:39,447 WARNING Skipped reaction rxn34327 with invalid coefficient: 1 cpd00005_0 + 0.5 cpd00007_0 + 1 cpd00067_0 <=> 1 cpd00001_0 + 1 cpd00006_0 + 4 cpd30058_0
    2018-08-20 11:16:39,448 WARNING Skipped reaction rxn34339 with invalid coefficient: 1 cpd30510_1 <=> 0.870291149592 cpd30507_0 + 0.274325356868 cpd30508_0 + 0.195494060752 cpd30509_0
    2018-08-20 11:16:39,448 WARNING Skipped reaction rxn34340 with invalid coefficient: 1 cpd30510_1 <=> 0.265727748401 cpd30507_0 + 0.660147062166 cpd30508_0 + 0.725321425353 cpd30509_0
    2018-08-20 11:16:39,449 WARNING Skipped reaction rxn34341 with invalid coefficient: 1 cpd30510_1 <=> 0.220793969935 cpd30507_0 + 0.63834334497 cpd30508_0 + 0.733622391471 cpd30509_0

