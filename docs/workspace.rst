
Work with PATRIC workspace
--------------------------

The PATRIC web service and the ModelSEED web service both use the same
PATRIC workspace. Mackinac provides functions for managing and working
with your PATRIC workspace. The ModelSEED web service stores models in
``/<userid>@patricbrc.org/modelseed``. The PATRIC web service stores
models in ``/<userid>@patricbrc.org/home/models``.

.. code:: ipython3

    import mackinac

Get a list of objects in a folder in a workspace with
``list_workspace_objects()``. For example, get a list of the templates
available for reconstructing models with this command:

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
    -rr seaver    	  20713372	2017-08-11T19:29:36Z	modeltemplate	/chenry/public/modelsupport/templates/PlantModelTemplate


Get the metadata for an object in the workspace with
``get_workspace_object_metadata()``. The metadata for an object can
include additional information about the contents or attributes of the
object. The media available for gap filling a model are in
``/chenry/public/modelsupport/media``.

.. code:: ipython3

    mackinac.get_workspace_object_meta('/chenry/public/modelsupport/media/Nitrogen-Uric-Acid')




.. parsed-literal::

    ['Nitrogen-Uric-Acid',
     'media',
     '/chenry/public/modelsupport/media/',
     '2015-05-11T05:39:04Z',
     '0918D468-F7A0-11E4-AA0D-729D682E0674',
     'chenry',
     580,
     {'isDefined': 1,
      'isMinimal': 1,
      'name': 'Nitrogen-Uric Acid',
      'source_id': 'Nitrogen-Uric Acid',
      'type': 'biolog'},
     {'is_folder': 0},
     'r',
     'r',
     '']



Get the data in an object with ``get_workspace_object_data()``. The data
for an object can be large so use caution with this function. By
default, the object data is assumed to be in JSON format. Set the
``json_data=False`` parameter if the object data is not in JSON format.

.. code:: ipython3

    mackinac.get_workspace_object_data('/chenry/public/modelsupport/media/Nitrogen-Uric-Acid', json_data=False)




.. parsed-literal::

    'id\tname\tconcentration\tminflux\tmaxflux\ncpd00027\tD-Glucose\t0.001\t-100\t5\ncpd00300\tUrate\t0.001\t-100\t5\ncpd00009\tPhosphate\t0.001\t-100\t5\ncpd00048\tSulfate\t0.001\t-100\t5\ncpd00063\tCa2+\t0.001\t-100\t100\ncpd00011\tCO2\t0.001\t-100\t0\ncpd10516\tfe3\t0.001\t-100\t100\ncpd00067\tH+\t0.001\t-100\t100\ncpd00001\tH2O\t0.001\t-100\t100\ncpd00205\tK+\t0.001\t-100\t100\ncpd00254\tMg\t0.001\t-100\t100\ncpd00971\tNa+\t0.001\t-100\t100\ncpd00007\tO2\t0.001\t-100\t100\ncpd00099\tCl-\t0.001\t-100\t100\ncpd00058\tCu2+\t0.001\t-100\t100\ncpd00149\tCo2+\t0.001\t-100\t100\ncpd00030\tMn2+\t0.001\t-100\t100\ncpd00034\tZn2+\t0.001\t-100\t100\ncpd10515\tFe2+\t0.001\t-100\t100\n'


