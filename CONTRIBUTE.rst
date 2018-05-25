Contributing
============

Contributions are always welcome! You can contribute by reporting problems, fixing
bugs, implementing new features, or improving the documentation.

Direct installation in virtual environment
------------------------------------------

Here's how to setup Mackinac for local development:

1. If virtualenvwrapper is not installed, `follow the directions <https://virtualenvwrapper.readthedocs.io/en/stable/>`__
   to install virtualenvwrapper. You should also `update your shell startup file
   <http://virtualenvwrapper.readthedocs.io/en/stable/install.html#shell-startup-file>`_.

2. Clone the `git repository <https://github.com/mmundy42/mackinac>`_ to your
   computer with this command::

    $ git clone https://github.com/mmundy42/mackinac.git

3. Create a virtualenv for Mackinac with these commands::

    $ cd mackinac
    $ mkvirtualenv mackinac

   Use the ``--python`` option to select a specific version of Python for the
   virtualenv. For example, to select the current python3 installed on the system
   run this command:

    $ mkvirtualenv --python=python3 mackinac

   Note on macOS, matplotlib requires Python be installed as a framework but
   virtualenv creates a non-framework build of Python. See the
   `matplotlib FAQ <http://matplotlib.org/1.5.3/faq/virtualenv_faq.html>`__
   for details on a workaround.

4. Upgrade pip and setuptools to the latest versions with these command::

    (mackinac)$ pip install --upgrade pip setuptools

5. Install the required packages for development with this command::

    (mackinac)$ pip install -r develop-requirements.txt

6. Check out the `devel` branch which is used for development with this command::

    (mackinac)$ git checkout devel

7. Setup Mackinac for development with this command::

    (mackinac)$ python setup.py develop

8. You need to provide a username and password for the tests to obtain an
   authentication token. Substitute your PATRIC username and password and run
   the tests with this command::

    (mackinac)$ TEST_USERNAME=<username> TEST_PASSWORD=<password> pytest mackinac/test -v

