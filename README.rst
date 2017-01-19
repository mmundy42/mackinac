ModelSEED for cobrapy
=====================

ModelSEED for `cobrapy <https://github.com/opencobra/cobrapy>`_ provides
support for creating COBRA models from ModelSEED models and using the ModelSEED
web service to create draft models from genomes available in the `Pathosystems
Resource Integration Center <https://www.patricbrc.org/portal/portal/patric/Home>`_
(PATRIC). If you are not a `registered PATRIC user
<http://enews.patricbrc.org/faqs/workspace-faqs/registration-faqs/>`_,
you must complete a `new user registration <https://user.patricbrc.org/register/>`_
to work with the ModelSEED web service.
 
If you already have models available in ModelSEED, you can simply import and
create a COBRA model with the ``create_cobra_model_from_modelseed_model()``
function. You can then use all of the features in cobrapy for analyzing,
inspecting, and drawing conclusions from the model.

You can also reconstruct and gap fill models using the ModelSEED
service for any organism with a genome available in PATRIC. In addition,
there are functions to manage and work with ModelSEED models.

The documentation is browseable online at
`readthedocs <https://cobrapy-modelseed.readthedocs.org/en/stable/>`_
and can also be
`downloaded <https://readthedocs.org/projects/cobrapy-modelseed/downloads/>`_.

Please use the `cobrapy Google
Group <http://groups.google.com/group/cobra-pie>`_ for help.
Alternatively, you can use
`gitter.im <https://gitter.im/opencobra/cobrapy>`_ for quick questions
and discussions (faster response times).

More information about opencobra is available at the
`website <http://opencobra.github.io/>`_.

Installation
^^^^^^^^^^^^

Use pip to install ModelSEED for cobrapy from
`PyPI <https://pypi.python.org/pypi/modelseed>`_ (we recommend doing this
inside a `virtual environment
<http://docs.python-guide.org/en/latest/dev/virtualenvs/>`_)::

    pip install modelseed

ModelSEED for cobrapy requires the cobrapy, requests, configparser, and six packages.

Direct installation in virtual environment
------------------------------------------

1. If virtualenvwrapper is not installed, `follow the directions <https://virtualenvwrapper.readthedocs.io/en/latest/>`__
   to install virtualenvwrapper.

2. Clone the `git repository <https://github.com/mmundy42/modelseed-cobrapy>`_ to your computer.

2. Create a virtualenv for modelseed with these commands::

    $ cd modelseed-cobrapy
    $ mkvirtualenv --python /Library/Frameworks/Python.framework/Versions/2.7/bin/python modelseed-py27

   Use the ``--python`` option to select a specific version of Python for the virtualenv. For example,
   ``python=python3`` to select the latest python3 installed on the system.

   Note on macOS, matplotlib requires Python be installed as a framework but virtualenv creates a
   non-framework build of Python. See the `matplotlib FAQ <http://matplotlib.org/1.5.3/faq/virtualenv_faq.html>`__
   for details on a workaround.

3. Upgrade pip and setuptools to the latest versions with these commands::

    (modelseed-py27)$ pip install --upgrade pip setuptools

4. Install all of the modelseed dependencies with this command::

    (modelseed-py27) pip install -r requirements.txt

   This command takes a few minutes while numpy, pandas, and libsbml are built in the virtualenv.

5. Install the latest version of modelseed with this command::

    (modelseed-py27)$ python setup.py install


Run tests to verify installation
--------------------------------

You need to provide a username and password for the tests to obtain an authentication
token.

1. Install the pytest package with this command::

    (modelseed-py27)$ pip install pytest

2. Substitute your PATRIC username and password and run the tests with this command::

    (modelseed-py27)$ TEST_USERNAME=<username> TEST_PASSWORD=<password> pytest modelseed/test

Run examples in a notebook
--------------------------

An example of how to use ModelSEED for cobrapy is provided in a notebook. Here's how to start Jupyter and run
the notebook from the virtualenv.

1. Install Jupyter with this command::

    (modelseed-py27)$ pip install jupyter

2. Install a kernel that uses the virtualenv installation with this command::

    (modelseed-py27)$ ipython kernel install --name "modelseed Python 27" --user

3. Start the Jupyter notebook server with this command::

    (modelseed-py27)$ juypter notebook

   Jupyter opens a web page in your default browser with a file browser.

4. Navigate to the "documentation_builder" folder and click on the "modelseed.ipynb" notebook.

5. After the notebook opens, from the "Kernel" menu, select "Change kernel" and click on "modelseed Python 27".

6. Now you can run the cells in the notebook.

