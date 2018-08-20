.. Mackinac documentation master file, created by
   sphinx-quickstart on Fri Jul 21 09:03:48 2017.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Mackinac: A bridge between ModelSEED and COBRApy
================================================

Reconstructing and analyzing a large number of genome-scale metabolic models is
a fundamental part of the integrated study of microbial communities. However,
two of the most widely used frameworks for building and analyzing models use
different metabolic network representations.

Mackinac supports automatic reconstruction of metabolic models using the ModelSEED
web service, the PATRIC web service, or directly from a template model. The
generated metabolic models can then be used with COBRApy's advanced analysis
capabilities to analyze the growth characteristics of the organisms and to evaluate
the effects of reaction or gene knockouts.

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   configure
   genome
   templates
   patric
   modelseed
   reconstruct
   analysis
   patric-advanced
   modelseed-advanced
   workspace
   mackinac

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
