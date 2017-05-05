from setuptools import setup, find_packages

requirements = [
    'cobra>=0.5.4',
    'six',
    'requests',
    'configparser'
]

try:
    with open('README.rst') as handle:
        description = handle.read()
except:
    description = ''

setup(
    name='mackinac',
    version='0.8.2',
    packages=find_packages(),
    setup_requires=[],
    install_requires=requirements,
    tests_require=['pytest'],
    author='Michael Mundy, Helena Mendes-Soares, Nicholas Chia',
    author_email='mundy.michael@mayo.edu',
    description='Mackinac: A bridge between ModelSEED and COBRApy',
    long_description=description,
    license='BSD',
    keywords='metabolism biology optimization flux balance analysis fba',
    url='https://github.com/mmundy42/mackinac',
    download_url='https://pypi.python.org/pypi/mackinac',
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
    platforms='GNU/Linux, Mac OS X >= 10.7, Microsoft Windows >= 7'
)
