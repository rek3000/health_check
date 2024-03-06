# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

import sys
import os

project = 'rekdoc'
copyright = '2024, rek3000'
author = 'rek3000'
release = '1.0'

# sys.path.insert(0, os.path.join(os.path.dirname(__file__), "rekdoc"))
sys.path.insert(0, os.path.abspath("rekdoc/"))
sys.path.insert(1, os.path.abspath("rekdoc/data"))
# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

autodoc_mock_imports = ["rekdoc"]
extensions = ["sphinx.ext.autodoc"]

templates_path = ['_templates']
exclude_patterns = ['_build', 'Thumbs.db',
                    '.DS_Store', ".venv", "test", "demo"]


# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = 'classic'
html_static_path = ['_static']
