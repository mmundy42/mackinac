
Get a PATRIC authentication token
---------------------------------

You need to provide a PATRIC authentiation token to use the ModelSEED or
PATRIC web services.

Mackinac reconstructs metabolic models from genomes available in the
`Pathosystems Resource Integration
Center <https://www.patricbrc.org/portal/portal/patric/Home>`__
(PATRIC). If you are not a `registered PATRIC
user <http://enews.patricbrc.org/faqs/workspace-faqs/registration-faqs/>`__,
you must complete a `new user
registration <https://user.patricbrc.org/register/>`__ to work with the
ModelSEED and PATRIC web services.

After you become a registered user, you need to provide an
authentication token with your PATRIC username and password. The
``get_token()`` function stores the authentication token in the
``.patric_config`` file in your home directory. You can use the token
until it expires.

Change ``username`` in the cell below to your PATRIC username and enter
your password when prompted. You only need to run this the first time
you use Mackinac or when the token has expired.

.. code:: ipython3

    mackinac.get_token('username')

Install a search program
------------------------

If you call the likelihood-based gene annotation functions, Mackinac
uses a search progam and a search database which requires some
additional configuration on your system. Mackinac supports the USEARCH
and BLASTP search programs, both of which are free. We recommend USEARCH
because it has better performance compared to BLASTP.

Follow the directions to install one of the supported search programs
and then follow the directions to download the search database.

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
of the virtual environment. See `Installing
USEARCH <http://www.drive5.com/usearch/manual/install.html>`__ for more
information and help with common installation problems.

Second, set the path to where you installed the USEARCH program. In this
example, USEARCH is installed in the user's home directory.

.. code:: ipython3

    import mackinac
    from os.path import expanduser, join, exists
    from os import makedirs
    search_program_path = join(expanduser('~'), 'usearch')

How to install BLASTP program
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

`BLASTP <https://blast.ncbi.nlm.nih.gov/Blast.cgi?PROGRAM=blastp&PAGE_TYPE=BlastSearch&LINK_LOC=blasthome>`__
is a component of the BLAST suite for comparing protein sequences.

First, download the appropriate version for your system from NCBI. You
can put the BLASTP program in any location on your system. If you are
using a virutal environment, you can put the BLASTP program in the "bin"
folder of the virtual environment.

Second, set the path to where you installed the BLASTP program. In this
example, BLASTP is installed in the user's home directory.

.. code:: ipython3

    import mackinac
    from os.path import expanduser, join, exists
    from os import makedirs
    search_program_path = join(expanduser('~'), 'blastp')

Download data files and build a search database
-----------------------------------------------

Likelihood-based gene annotation uses a search database to match genome
features to protein sequences with known functions. There are two data
files:

1. a FASTA file with the known protein sequences
2. a file that maps feature IDs from the FASTA file to functional roles
   from genome annotations

Create a folder for storing the data files. Change the value assigned to
``data_folder`` if you want to use a different location from your home
folder.

.. code:: ipython3

    data_folder = join(expanduser('~'), 'mackinac_data')
    if not exists(data_folder):
        makedirs(data_folder)

Set variables for the locations of the data files.

.. code:: ipython3

    fid_role_path = join(data_folder, 'otu_fid_role.tsv')
    protein_sequence_path = join(data_folder, 'protein.fasta')
    search_db_path = join(data_folder, 'protein.udb')

Download the files and create the search database. Note this step can
take a few minutes, depending on your network connection.

.. code:: ipython3

    mackinac.download_data_files(fid_role_path, protein_sequence_path, search_db_path, search_program_path)
