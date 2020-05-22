.. IMT Epidemic Models documentation master file, created by
   sphinx-quickstart on Mon May 18 17:55:42 2020.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to IMT Epidemic Models's documentation!
===============================================

|docs| |last commit| |most used lang| |join slack| |join discord|

Este projeto tem o objetivo de divulgar como desenvolver modelos para epidemias, desde 
sua modelagem matemática até sua concepção computacional em Python. Sendo assim composto 
por videos explicativos, notebooks em Python, e diversas visualizações, para ajudar com o 
entendimento do conteúdo apresentado.

Alguns resultados
=================

Para dar um gosto do conteúdo aprensentado, uma análise foi feita com dados de epidemias 
do Reino Unido (United Kingdom), e utilizando os modelos aqui desenvolvidos, é possível 
obter modelos capazes de fazer previsões dos surtos epidêmicos dos dados. Essas previsões,
juntamente com os dados, estão apresentadas na figura a seguir: 

.. raw:: html

   <iframe 
      src="UK_result.html" 
      height="780" 
      width="650"
      style="border:none;"
   ></iframe> 

.. toctree::
   :maxdepth: 2
   :caption: Contents:


.. toctree::
   :maxdepth: 2
   :caption: Modelos Analíticos

   analytic

.. toctree::
   :maxdepth: 2
   :caption: Modelos Estocásticos

   stochastic

.. toctree::
   :maxdepth: 2
   :caption: Baseados em Dados

   data_driven


.. toctree::
   :maxdepth: 1
   :caption: Autores

   authors


Indices e tabelas
=================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

.. |join discord| image:: https://img.shields.io/discord/713442259210600448?label=join%20discord
   :alt: Join discussion Discord
   :target: https://discord.gg/EenaYE5

.. |join slack| image:: https://img.shields.io/badge/join%20slack-%23nsee-brightgreen.svg 
   :alt: Join discussion Slack
   :target: https://nseecorot.slack.com/archives/C013Q9068NB

.. |most used lang| image:: https://img.shields.io/github/languages/top/lafetamarcelo/epidemicModels   
   :alt: GitHub top language


.. |last commit| image:: https://img.shields.io/github/last-commit/lafetamarcelo/epidemicModels   
   :alt: GitHub last commit
   :target: https://github.com/lafetamarcelo/epidemicModels/


.. |docs| image:: https://readthedocs.org/projects/epidemicmodels/badge/?version=latest
   :alt: Documentation Status
   :target: https://readthedocs.org/projects/epidemicmodels/