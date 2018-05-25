Mackinac: A bridge between ModelSEED and COBRApy
================================================

Mackinac combines the automatic reconstruction of metabolic models using
`ModelSEED <http://modelseed.org>`_ or the `Pathosystems Resource Integration Center
<https://www.patricbrc.org/portal/portal/patric/Home>`_ (PATRIC) with the
advanced analysis capabilities in `cobrapy <https://github.com/opencobra/cobrapy>`_
to bridge the differences between the frameworks. Mackinac provides support for
using the PATRIC and ModelSEED services to create draft genome-scale models from
genomes available in PATRIC and creates a COBRA model from the draft model. If
you already have models available in PATRIC or ModelSEED, you can simply import and
create a COBRA model. You can then use all of the features in cobrapy to analyze,
inspect, explore, and draw conclusions from the model.

If you are not a `registered PATRIC user <http://enews.patricbrc.org/faqs/workspace-faqs/registration-faqs/>`_,
you must complete a `new user registration <https://user.patricbrc.org/register/>`_
to work with the PATRIC or ModelSEED services.

You can also work with your PATRIC or ModelSEED models, manage your PATRIC workspace,
get information about PATRIC genomes, and create a draft model using likelihoods
from a template model.

Please use the `cobrapy Google
Group <http://groups.google.com/group/cobra-pie>`_ for help.
Alternatively, you can use
`gitter.im <https://gitter.im/opencobra/cobrapy>`_ for quick questions
and discussions (faster response times).

More information about opencobra is available at the
`website <http://opencobra.github.io/>`_.

Installation
------------

Use pip to install Mackinac from
`PyPI <https://pypi.python.org/pypi/mackinac>`_ (we recommend doing this
inside a `virtual environment
<http://docs.python-guide.org/en/latest/dev/virtualenvs/>`_)::

    pip install mackinac

Web service URLs
----------------

Mackinac uses services provided by other organizations which can be offline, the
interface can change, or the URL can change. Mackinac uses these default URLs:

* ModelSEED service at https://p3.theseed.org/services/ProbModelSEED
* Workspace service at https://p3.theseed.org/services/Workspace
* PATRIC API at https://www.patricbrc.org/api/
* PATRIC app service at https://p3.theseed.org/services/app_service

You can change the URL used to connect to a service as shown below:

    >>> import mackinac
    >>> mackinac.modelseed.ms_client.url = 'http://p3.theseed.org/services/ProbModelSEED'
    >>> mackinac.workspace.ws_client.url = 'https://p3.theseed.org/services/Workspace'
    >>> mackinac.genome.patric_url = 'https://www.patricbrc.org/api/'
    >>> mackinac.patric.patric_app_url = 'https://p3.theseed.org/services/app_service'

Run examples in a notebook
^^^^^^^^^^^^^^^^^^^^^^^^^^

An example of how to use Mackinac is provided in a notebook. Here's how to start Jupyter and run
the notebook from the virtualenv.

1. Install Jupyter with this command::

    (mackinac)$ pip install jupyter

2. Install a kernel that uses the virtualenv installation with this command::

    (mackinac)$ ipython kernel install --name "Mackinac_Python27" --user

3. Start the Jupyter notebook server with this command::

    (mackinac)$ jupyter notebook

   Jupyter opens a web page in your default browser with a file browser.

4. Navigate to the "documentation_builder" folder and click on the "modelseed.ipynb"
   notebook.

5. After the notebook opens, from the "Kernel" menu, select "Change kernel" and
   click on "Mackinac_Python27".

6. Now you can run the cells in the notebook.

Acknowledgements
----------------

The support for template models is derived from ModelSEED and as required by the
`ModelSEED license <https://github.com/ModelSEED/ProbModelSEED/blob/master/LICENSE.md>`_
note that:

   This product includes software developed by and/or derived from the SEED Project
   (http://www.theseed.org) to which the U.S. Government retains certain rights.

One source for the template model data files is the Central Data Model provided by
"KBase: The U.S. Department of Energy Systems Biology Knowledgebase". As a user,
you must abide by the following KBase Information and Data Sharing Policy:

   KBase conforms to the Information and Data Sharing Policy of the Genomic Science
   Program of the Office of Biological and Environmental Research within the Office
   of Science. This requires that all publishable data, metadata, and software
   resulting from research funded by the Genomic Science program must conform to
   community-recognized standard formats when they exist; be clearly attributable;
   and be deposited within a community-recognized public database(s) appropriate
   for the research.

   -- www.kbase.us

See `Data Policy and Sources <http://kbase.us/data-policy-and-sources/>`_ for
additional details.

Another source for the template model data files is the Kyoto Encyclopedia of Genes
and Genomes (KEGG). Data from KEGG was obtained using the
`KEGG API <http://www.kegg.jp/kegg/rest/>`_.

Note, there are some limitations on using the KEGG API, most importantly:

    **Restrictions:** KEGG API is provided for academic use by academic users
    belonging to academic institutions. This service should not be used for bulk
    data downloads. Please obtain KEGG FTP academic subscription for downloading
    KEGG data.

    -- www.kegg.jp

Release Notes
-------------

Version 0.9.0 (January XX, 2018)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

* Added support for creating models using PATRIC app service
* Added support for template models which includes reconstructing a draft model
  from the genome of an organism and exporting a template model to a cobra model,
  a PSAMM model, and a list file
* Added support for calculating reaction likelihoods and reconstructing a draft
  model from the reaction likelihoods
* Added support for gap filling a model using cobra gap fill method
* Updates for compatibility with latest COBRApy versions
* Changed documentation to Read the Docs format and configured build with Sphinx
* Fixed get_modelseed_gapfill_solutions() to convert ID type of reactions to match
  conversion done by create_cobra_model_from_modelseed_model()
* Bug fixes and better logging
* Switched default ModelSEED service URL to production server

Version 0.8.4 (May 18, 2017)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

* Fixed usages of deprecated cobra.core.Model.add_reaction() function
* Added another way to parse error returned by ModelSEED server

Version 0.8.3 (May 8, 2017)
^^^^^^^^^^^^^^^^^^^^^^^^^^^

* Fixed setting reaction objective coefficient with cobra 0.6

Version 0.8.2 (May 5, 2017)
^^^^^^^^^^^^^^^^^^^^^^^^^^^

* Removed dependency on a specific version of six package
* Updated directions for virtual environment installation
* Switched default ModelSEED service URL to current active server

Version 0.8.1 (March 15, 2017)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

* Version corresponding to published paper

How to cite Mackinac
--------------------

If you use Mackinac for an analysis, please cite this paper:
`Mackinac: a bridge between ModelSEED and COBRApy to generate and analyze genome-scale
metabolic models <https://dx.doi.org/doi:10.1093/bioinformatics/btx185>`_

References
----------

1. `COBRApy: COnstraints-Based Reconstruction and Analysis for Python <http://dx.doi.org/doi:10.1186/1752-0509-7-74>`_
2. `High-throughput generation, optimization and analysis of genome-scale metabolic models <http://dx.doi.org/doi:10.1038/nbt.1672>`_ (ModelSEED)
3. `PATRIC, the bacterial bioinformatics database and analysis resource <http://dx.doi.org/doi:10.1093/nar/gkt1099>`_
4. `KEGG: Kyoto Encyclopedia of Genes and Genomes <http://www.kegg.jp>`_
5. `Systems Biology Knowledgebase <http://kbase.us>`_


Mackinac Bridge
^^^^^^^^^^^^^^^

The `Mackinac Bridge <http://www.mackinacbridge.org>`_ is one of the longest
suspension bridges in the United States and spans the Straits of Mackinac to
connect the Upper and Lower Peninsulas of Michigan.
