ModelSEED for cobrapy
=====================

ModelSEED for `cobrapy <https://github.com/opencobra/cobrapy>`_ provides
support for creating COBRA models from ModelSEED models and using the ModelSEED
web service. The ModelSEED web service creates draft models from genomes
available in the `Pathosystems Resource Integration Center
<https://www.patricbrc.org/portal/portal/patric/Home>`_ (PATRIC).
If you are not a `registered PATRIC user
<http://enews.patricbrc.org/faqs/workspace-faqs/registration-faqs/>`_,
you must complete a `new user registration <https://user.patricbrc.org/register/>`_
to work with the ModelSEED web service.
 
If you already have models available in ModelSEED, you can simply import and
create a COBRA model with the ``create_cobra_model_from_modelseed_model()``
function. You can then use all of the features in cobrapy for analyzing,
inspecting, and drawing conclusions from the model.

You can also reconstruct and gap fill models using the ModelSEED
service for any organism with a genome available in PATRIC. In addition,
there are functions to help manage and view ModelSEED models.

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

What about cobrapy - gotta have it.

Use pip to install modelseed from
`PyPI <https://pypi.python.org/pypi/modelseed>`_ (we recommend doing this
inside a `virtual
environment <http://docs.python-guide.org/en/latest/dev/virtualenvs/>`_)::

    pip install modelseed
