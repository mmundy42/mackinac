#!/usr/bin/env bash
rm mackinac*.rst
sphinx-apidoc -o . ../mackinac ../mackinac/test
rm modules.rst
jupyter nbconvert --to=rst *.ipynb