
Configuring model reconstruction
--------------------------------

Mackinac supports reconstructing and gap filling models from a PATRIC
genome using probabilistic annotation. Probabilistic annotation uses a
search progam and a search database which requires some additional
configuration on your system. Mackinac supports the USEARCH and BLASTP
search programs, both of which are free. We recommend USEARCH because it
has better performance compared to BLASTP.

How to install USEARCH program
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

`USEARCH <http://www.drive5.com/usearch/>`__ is "a unique sequence
analysis tool" that "offers search and clustering algorithms that are
often orders of magnitude faster than BLAST". Licenses for the 32-bit
USEARCH are free for all users but the license does not allow for
re-distribution of the binary. So you must register to download the
USEARCH executable and install it on your system.

First, `submit a
request <http://www.drive5.com/usearch/download.html>`__ to download
USEARCH for your system. Linux, Windows, and MacOS are all supported.
After submitting the request, you will receive an email with a link that
allows you to download the USEARCH program. The USEARCH program is
completely self-contained so there is no installer for it. You can put
the USEARCH program in any location on your system. If you are using a
virutal environment, you can put the USEARCH program in the "bin" folder
of the virtual environment. See the `Installing
USEARCH <http://www.drive5.com/usearch/manual/install.html>`__ for more
information and help with common installation problems.

How to install BLASTP program
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

`BLASTP <https://blast.ncbi.nlm.nih.gov/Blast.cgi?PROGRAM=blastp&PAGE_TYPE=BlastSearch&LINK_LOC=blasthome>`__
is a component of the BLAST suite for comparing protein sequences.
Download it. You can put the BLASTP program in any location on your
system. If you are using a virutal environment, you can put the BLASTP
program in the "bin" folder of the virtual environment.

Download data files and build a search database
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Probabilistic annotation uses a search database to match genome features
to protein sequences with known functions. There are two data files: (1)
a FASTA file with the known protein sequences and (2) a file that maps
feature IDs from the FASTA file to functional roles from genome
annotations.

First, import the mackinac package and a few other needed packages.

.. code:: ipython3

    import mackinac
    import json
    from os.path import expanduser, join

Second, make a copy of the default configuration and get your home
folder.

.. code:: ipython3

    my_config = mackinac.likelihood.default_config
    home_folder = expanduser('~')

Third, set the path in the configuration to the search program that you
downloaded above. In the cell below, it is assumed that you put the
USEARCH program in your home folder. Change the folder if you put the
USEARCH progam in a different location.

.. code:: ipython3

    my_config['search_program_path'] = join(home_folder, 'usearch')

Fourth, set the path in the configuration to the data folder for storing
the downloaded files.

.. code:: ipython3

    my_config['data_folder'] = join(home_folder, 'mackinac_data')

Fifth, set the path in the configuration to the work folder for storing
the intermediate files that are created by probabilistic annotation.

.. code:: ipython3

    my_config['work_folder'] = join(home_folder, 'mackinac_work')

Sixth, download the files and create the search database. Note this step
can take a few minutes, depending on your network connection.

.. code:: ipython3

    mackinac.download_data_files('/mmundy/public/modelsupport', my_config)

Finally, save your configuration to a file so you can use it in later
analysis.

.. code:: ipython3

    json.dump(my_config, open(join(home_folder, 'mackinac_config.json'), 'w'))
