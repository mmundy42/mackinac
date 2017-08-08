
Configuring model reconstruction
--------------------------------

Mackinac supports using likelihood-based gene annotation for
reconstructing and gap filling models from a PATRIC genome.
Likelihood-based gene annotation uses a search progam and a search
database which requires some additional configuration on your system.
Mackinac supports the USEARCH and BLASTP search programs, both of which
are free. We recommend USEARCH because it has better performance
compared to BLASTP.

Note we are still deciding how to distribute updated versions of the
data files.

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
Download it from NCBI. You can put the BLASTP program in any location on
your system. If you are using a virutal environment, you can put the
BLASTP program in the "bin" folder of the virtual environment.

Download data files and build a search database
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Likelihood-based gene annotation uses a search database to match genome
features to protein sequences with known functions. There are two data
files: (1) a FASTA file with the known protein sequences and (2) a file
that maps feature IDs from the FASTA file to functional roles from
genome annotations.

First, import the mackinac package and a few other needed functions.

.. code:: ipython3

    import mackinac
    from os.path import expanduser, join, exists
    from os import makedirs

Second, create a folder for storing the data files. Change the value
assigned to ``data_folder`` if you want to use a different location from
your home folder.

.. code:: ipython3

    data_folder = join(expanduser('~'), 'mackinac_data')
    if not exists(data_folder):
        makedirs(data_folder)

Third, set variables for the locations of the data files and the search
program that you downloaded above. In the cell below, it is assumed that
you put the USEARCH program in your home folder. Change the value if you
put the USEARCH progam in a different location or are using BLASTP.

.. code:: ipython3

    fid_role_path = join(data_folder, 'otu_fid_role.tsv')
    protein_sequence_path = join(data_folder, 'protein.fasta')
    search_db_path = join(data_folder, 'protein.udb')
    search_program_path = join(expanduser('~'), 'usearch')

Fourth, download the files and create the search database. Note this
step can take a few minutes, depending on your network connection.

.. code:: ipython3

    mackinac.download_data_files(fid_role_path, protein_sequence_path, search_db_path, search_program_path)
