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

.. raw:: html

   <h3 style="text-align:center;">
      <iframe 
         width="600" 
         height="450" 
         src="https://datastudio.google.com/embed/reporting/4824fb05-ec67-4b16-bf21-b4b7ab47d958/page/gErTB" 
         frameborder="0" 
         style="border:0" 
         allowfullscreen>
      </iframe>
   </h3>


Alguns resultados do século XX...
=================================

Para dar um gosto do conteúdo aprensentado, foi desenvolvida uma análise com dados 
do Reino Unido (United Kingdom), e utilizando os modelos aqui desenvolvidos, é possível 
obter previsões do comportamento dos dados. Essas previsões, juntamente com os dados reias, 
estão apresentadas na figura a seguir: 

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
durante os períodos de epidemias do Reino Unido:

.. image:: images/res/UK_models_corr.png
   :align: center
   :width: 500


Previsões do COVID
==================

Nesta análise utilizamos o modelo desenvolvido para tentar prever os comportamentos do 
COVID. Para isso, primeiramente utilizamos dados de países que já apresentam um comportamento 
característico da estrutura SIR, e já estão em seu final. Desta forma podemos validar o modelo 
com relação a sua capacidade de prever eventos futuros, mesmo que somente poucos dias de dados 
sejam utilizados. Desta forma algumas análises específicas, e de maior impacto, são apresentadas 
nessa primeira página:

* Determinação do número básico de reprodução :math:`R_0` no decorrer da epidemia
* Previsão da quantidade de infectados notificados no sistema público
* Previsão do momento de pico da epidemia

No caso, essas análises foram feitas para Itália |:it:|, China |:cn:| e Alemanha |:de:|, países 
que já estão em seu período de diminuição do nível de infectados. Para dar um gosto sobre a 
capacidade de previsão do algoritmo de aprendizado desenvolvido, nas visualizações a seguir 
nós mostramos a previsão feita pelo algoritmo para cada país a medida que os tempo da epidemia 
foi passando e mais dados foram utilizados para a aprendizagem:


.. raw:: html

   <h3 style="text-align:center;">
      <iframe 
         id="ItalyPredfiFrame"
         style="border:none;"
         src="slider_IT.html"
         height="480"
         width="520"
      ></iframe>
   </h3>


.. raw:: html

   <h3 style="text-align:center;">
      <iframe 
         id="ChinaPredfiFrame"
         style="border:none;"
         src="slider_CN.html"
         height="480"
         width="520"
      ></iframe>
   </h3>


.. raw:: html

   <h3 style="text-align:center;">
      <iframe 
         id="GermanyPredfiFrame"
         style="border:none;"
         src="slider_DE.html"
         height="480"
         width="520"
      ></iframe>
   </h3>



Nosso modelo aprende com algoritmos de otimização os parâmetros da estrutura SIR, juntamente 
com a proporção da população que está sendo registrada pelo sistema de saúde. No caso, ele 
aprende três parâmetros fundamentais do modelo: :math:`\beta` (contatos por dia), :math:`r` 
(em que :math:`1/r` é o tempo médio de recuperação da doença), e o :math:`S(0)` (quantidade 
inicial de suscetíveis), para que a epidemia tenha o comportamento que os dados mostram. No 
caso os valores ajustados para cada país foram:


.. raw:: html

   <h3 style="text-align:center;">
      <blockquote>
      <div><table class="docutils align-default">
      <colgroup>
      <col style="text-align:center;width: 39%" />
      <col style="text-align:center;width: 34%" />
      <col style="text-align:center;width: 27%" />
      </colgroup>
      <thead>
      <tr class="row-odd"><th class="head"><p>País</p></th>
      <th class="head"><p><span class="math notranslate nohighlight">\(\beta\)</span></p></th>
      <th class="head"><p><span class="math notranslate nohighlight">\(r\)</span></p></th>
      </tr>
      </thead>
      <tbody>
      <tr class="row-even"><td><p>Itália 🇮🇹</p></td>
      <td><p>0.2038</p></td>
      <td><p>0.0233</p></td>
      </tr>
      <tr class="row-odd"><td><p>China 🇨🇳</p></td>
      <td><p>0.3133</p></td>
      <td><p>0.0445</p></td>
      </tr>
      <tr class="row-even"><td><p>Alemanha 🇩🇪</p></td>
      <td><p>0.2195</p></td>
      <td><p>0.0576</p></td>
      </tr>
      </tbody>
      </table>
      </div></blockquote>
   </h3>


**Caso você mesmo queira se divertir e tentar ajustar os parâmetros, é possível, clicando no botão abaixo!**

.. raw:: html

   <h3 style="text-align:center;">
      <a href="SIR-sliders.html">
         <!DOCTYPE html>
            <html>
               <head>
                  <style>
                     .button {
                     border: none;
                     color: white;
                     border-radius: 32px;
                     padding: 16px 32px;
                     text-align: center;
                     text-decoration: none;
                     display: inline-block;
                     font-size: 16px;
                     margin: 4px 2px;
                     cursor: pointer;
                     border-radius: 45px;
                     box-shadow: 0px 8px 15px rgba(0, 0, 0, 0.1);
                     transition: all 0.3s ease 0s;
                     }

                     .button1 {
                     background-color: white;
                     color: black;
                     border: 2px solid #4CAF50;
                     }

                     .button1:hover {
                     background-color: #4CAF50;
                     color: white;
                     box-shadow: 0px 15px 20px rgba(46, 229, 157, 0.4);
                     transform: translateY(-7px);
                     }
                  </style>
               </head>
               <body>
                  <button class="button button1">Tente você mesmo!</button>
               </body>
         </html> 
      </a>
   </h3>


.. raw:: html

   <br><br><br><br><br><br><br>



Determinação do :math:`R_0`
---------------------------

Note que o parâmetro :math:`R_0`, é determinado a partir dos dois outros característicos do 
modelo SIR, :math:`R_0 = \beta / r`. Aqui utilizamos um modelo SIR que pondera a quantidade 
de suscetíveis, uma vez que nem toda a população pode ser considerada suscetível, visto que 
nem todas as pessoas infectadas, e recuperadas são notificadas ao sistema público. E nem toda 
a população é alcançavel ao vírus, devido a políticas públicas, isolamentos ... 

.. note::
   Desta forma note, que o modelo desenvolvido somente modela as pessoas notificadas pelo sistema
   de saúde, sendo assim, representativo de uma parte da verdade situação do país.

Dito isso, é possível definir os valores encontrados pelo algoritmo de aprendizagem para o 
parâmetro :math:`R_0` a medida que os dias da pandemia passaram:


.. raw:: html

   <h3 style="text-align:center;">
      <iframe 
         id="ItalyRofiFrame"
         style="border:none;"
         src="Ro_estimate_IT.html"
         height="460"
         width="750"
      ></iframe>
   </h3>

.. raw:: html

   <h3 style="text-align:center;">
      <iframe 
         id="ItalyRofiFrame"
         style="border:none;"
         src="Ro_estimate_CN.html"
         height="460"
         width="750"
      ></iframe>
   </h3>

.. raw:: html

   <h3 style="text-align:center;">
      <iframe 
         id="GermanyRofiFrame"
         style="border:none;"
         src="Ro_estimate_DE.html"
         height="460"
         width="750"
      ></iframe>
   </h3>



Previsões do consumo do sistema público
---------------------------------------

Um dos parâmetros que nosso algoritmo aprende durante seu processo de treinamento, é um parâmetro 
que pondera a quantidade da população de suscetíveis inicial (simplesmente uma técnica para 
melhorar o condicionamento númerico do algoritmo). Porém, com esse parâmetro tende sempre a 
estimar o valor de :math:`S(0)` igual ao valor de :math:`R(\infty)`. Note que sempre é verdade  
:math:`S(0) \geq R(\infty)`. Como os dados medidos são somente das pessoas notificadas e acompanhadas 
pelo sistema de saúde, podemos concluir que o valor de :math:`R(\infty)` é a quantidade de pessoas 
que foram contamindas, e frequentaram o sistema de saúde para o diagnóstico, e por isso estão na 
base de dados. Nosso algoritmo prevê a quantidade de :math:`S(0) = R(\infty)`, desta forma para cada 
novo dia de dados temos uma nova previsão de qual será a quantidade de pessoas que consumirão o sistema 
de saúde. Nos gráficos a seguir conseguimos mostrar o erro percentual entre o real valor de :math:`R(\infty)`
e o valor estimado por nosso modelo a cada dia da epidemia:


.. raw:: html

   <h3 style="text-align:center;">
      <iframe 
         id="ItalyPSfiFrame"
         style="border:none;"
         src="Public_usage_IT.html"
         height="460"
         width="750"
      ></iframe>
   </h3>

.. raw:: html

   <h3 style="text-align:center;">
      <iframe 
         id="ChinaPSfiFrame"
         style="border:none;"
         src="Public_usage_CN.html"
         height="460"
         width="750"
      ></iframe>
   </h3>

.. raw:: html

   <h3 style="text-align:center;">
      <iframe 
         id="GermanyPSfiFrame"
         style="border:none;"
         src="Public_usage_DE.html"
         height="460"
         width="750"
      ></iframe>
   </h3>




Previsões dos picos epidêmicos do COVID
---------------------------------------

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




Modelos COVID Brasil |:br:|
============================


.. admonition:: And, by the way...

   Em construção...





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


.. raw:: html

   <h3 style="text-align:center;">
   <iframe width="600" height="338" src="http://datastudio.google.com/embed/reporting/1WhloLyiBE-pOP0xw8Pee1Mamekc-CGgH/page/D1hT"></iframe>
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