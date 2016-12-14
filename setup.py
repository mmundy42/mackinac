from os.path import isfile, abspath, dirname, join
from sys import argv, path

# To temporarily modify sys.path
SETUP_DIR = abspath(dirname(__file__))

try:
    from setuptools import setup, find_packages
except ImportError:
    path.insert(0, SETUP_DIR)
    import ez_setup
    path.pop(0)
    ez_setup.use_setuptools()
    from setuptools import setup, find_packages

# Import version to get the version string
path.insert(0, join(SETUP_DIR, 'modelseed'))
from version import get_version, update_release_version
path.pop(0)
version = get_version(pep440=True)

# If building something for distribution, ensure the VERSION
# file is up to date
if 'sdist' in argv or 'bdist_wheel' in argv:
    update_release_version()

# Begin constructing arguments for building package.
setup_kwargs = {}

try:
    with open('README.rst') as handle:
        readme = handle.read()
    setup_kwargs['long_description'] = readme
except:
    setup_kwargs['long_description'] = ''

setup(
    name='modelseed',
    version=version,
    packages=find_packages(),
    setup_requires=[],
    install_requires=['cobra >= 0.5.6', 'six', 'requests'],
    tests_require=['pytest'],
    package_data={},
    author='Michael Mundy <mundy.michael@mayo.edu',
    author_email='mundy.michael@mayo.edu',
    description='ModelSEED support for cobrapy',
    license='BSD',
    keywords='metabolism biology optimization flux balance analysis fba',
#    url='https://opencobra.github.io/cobrapy',
    test_suite='cobra.test.suite',
    download_url='https://pypi.python.org/pypi/modelseed',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Topic :: Scientific/Engineering',
        'Topic :: Scientific/Engineering :: Bio-Informatics'
    ],
    platforms='GNU/Linux, Mac OS X >= 10.7, Microsoft Windows >= 7',
    **setup_kwargs)