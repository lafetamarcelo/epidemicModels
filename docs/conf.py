# Configuration file for the Sphinx documentation builder.
#
# This file only contains a selection of the most common options. For a full
# list see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Path setup --------------------------------------------------------------

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
#
import os
import sys
sys.path.insert(0, os.path.abspath('..'))

import sphinx_rtd_theme
import sphinxemoji

# -- Project information -----------------------------------------------------

project = 'IMT Epidemic Models'
copyright = '2020, Vanderlei Parro e Marcelo Lima'
author = 'Vanderlei Parro e Marcelo Lima'

# The full version, including alpha/beta/rc tags
release = 'v0.1'


# -- General configuration ---------------------------------------------------

master_doc = 'index'

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
  'nbsphinx',
  'sphinx_rtd_theme',
  'sphinx.ext.autodoc',
  'sphinx.ext.mathjax',
  'sphinx_copybutton',
  'sphinx.ext.githubpages',
  'sphinx.ext.imgconverter',
  'bokeh.sphinxext.bokeh_autodoc',
  'sphinxemoji.sphinxemoji',
]

highlight_language = 'python3'

sphinxemoji_style = 'twemoji'

# Add any paths that contain templates here, relative to this directory.
templates_path = ['_templates']

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store', '.ipynb_checkpoints']


# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
html_theme = 'sphinx_rtd_theme'

html_logo = 'images/icons/Full_white_background.png'
html_favicon = 'images/icons/Small_white_background.ico'

html_title = 'Epidemic Models'
html_short_title = 'EM'

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ['_static']

html_extra_path = [
  "./media_content/UK_result.html"
]