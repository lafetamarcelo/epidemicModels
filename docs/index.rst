.. IMT Epidemic Models documentation master file, created by
   sphinx-quickstart on Mon May 18 17:55:42 2020.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to IMT Epidemic Models's documentation!
===============================================

|docs| |last commit| |most used lang| |join discord| 

Este projeto tem o objetivo de divulgar como desenvolver modelos para epidemias, desde 
sua modelagem matemática até sua concepção computacional em Python. Sendo assim composto 
por videos explicativos, notebooks em Python, e diversas visualizações, para ajudar com o 
entendimento do conteúdo apresentado.

Alguns resultados do século XX...
=================================

Para dar um gosto do conteúdo aprensentado, uma análise foi feita com dados de epidemias 
do Reino Unido (United Kingdom), e utilizando os modelos aqui desenvolvidos, é possível 
obter modelos capazes de fazer previsões dos surtos epidêmicos dos dados. Essas previsões,
juntamente com os dados, estão apresentadas na figura a seguir: 

.. raw:: html

   <h3 style="text-align:center;">
      <iframe 
         id="UKiFrame"
         style="border:none;"
         src="UK_result.html"
         height="780"
         width="680"
      ></iframe>
   </h3>
   <script>
      const iframe = document.getElementById("UKiFrame")
      if (screen.width < 600) {
         iframe.setAttribute("src", "UK_result.html")
         iframe.setAttribute("height", 780)
         iframe.setAttribute("width", 680)
      }
   </script>

Assim como o estudo de correlação entre os modelos SIR obtidos para cada uma das cidades 
durante os períodos de epidemias:

.. image:: images/res/UK_models_corr.png
   :width: 700



Previsões dos picos epidêmicos do COVID
========================================

Nesta análise apresentamos o efeito da quantidade de dados na performance do modelo desenvolvido 
analisando a capacidade de prever o dia em que acontecerá o pico da quantidade de infectados da 
epidemia do COVID. Para isso estamos utilizando dados de países que já tiveram seu pico de contágio,
e atualmente estão no período de amortecimento da quantidade de infectados. Alguns dos países analisados 
foram a China |:cn:|, Itália |:it:| e Alemanha |:de:|, que possibilitaram as análises abaixo. 
Nestas figuras é mostrado o erro do modelo ao tentar prever o dia de pico, para cada dia decorrente 
da epidemia:

.. raw:: html

   <h3 style="text-align:center;">
      <iframe 
         id="ChinaInfiFrame"
         style="border:none;"
         src="peak_estimate_CN.html"
         height="530"
         width="680"
      ></iframe>
   </h3>

.. raw:: html

   <h3 style="text-align:center;">
      <iframe 
         id="ItalyInfiFrame"
         style="border:none;"
         src="peak_estimate_IT.html"
         height="530"
         width="680"
      ></iframe>
   </h3>

.. raw:: html

   <h3 style="text-align:center;">
      <iframe 
         id="GermanyInfiFrame"
         style="border:none;"
         src="peak_estimate_DE.html"
         height="530"
         width="680"
      ></iframe>
   </h3>


Uma comparação entre os dados reais e os modelos obtidos a cada dia 
que se passou da epidemia, está sendo apresentado a seguir para os 
dados da Itália |:it:|:

.. raw:: html

   <h3 style="text-align:center;">
      <iframe 
         id="ITalliFrame"
         style="border:none;"
         src="IT_COVID.html"
         height="530"
         width="680"
      ></iframe>
   </h3>
   <script>
      const iframe = document.getElementById("ITalliFrame")
      if (screen.width < 600) {
         iframe.setAttribute("src", "IT_COVID.html")
         iframe.setAttribute("height", 780)
         iframe.setAttribute("width", 680)
      }
   </script>



Modelos COVID Brasil |:br:|
============================

Como exemplo, segue o trabalho atual com as previsões dos comportamentos da epidemia no 
Brasil. Uma mescla entre os dados existentes e a previsão obtida pelo modelo SIR ajustado 
aos dados existentes:

.. raw:: html

   <h3 style="text-align:center;">
      <iframe 
         id="BRiFrame"
         style="border:none;"
         src="BR_result.html"
         height="530"
         width="680"
      ></iframe>
   </h3>
   <script>
      const iframe = document.getElementById("BRiFrame")
      if (screen.width < 600) {
         iframe.setAttribute("src", "BR_result.html")
         iframe.setAttribute("height", 780)
         iframe.setAttribute("width", 680)
      }
   </script>





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
   :maxdepth: 2
   :caption: COVID

   covid


.. toctree::
   :maxdepth: 3
   :caption: Code APIs

   modules


.. toctree::
   :maxdepth: 1
   :caption: Autores

   authors


.. raw:: html 

   <h3 style="text-align:center;">
      <iframe 
         src="https://discordapp.com/widget?id=713442259210600448&theme=dark" 
         width="500" 
         height="300"
         allowtransparency="true" 
         frameborder="0"
      ></iframe>
   </h3>


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