# Welcome to the epidemicModels Repo!
---

<p align="center">
  <a href="https://discord.gg/EenaYE5" alt="Discord">
    <img src="https://img.shields.io/discord/713442259210600448?label=join%20discord" /></a>
  <a href="https://nseecorot.slack.com/archives/C013Q9068NB" alt="Slack">
    <img src="https://img.shields.io/badge/join%20slack-%23nsee-brightgreen.svg" /></a>
  <a alt="Language used">
    <img src="https://img.shields.io/github/languages/top/lafetamarcelo/epidemicModels" /></a>
  <a href="https://github.com/lafetamarcelo/epidemicModels/" alt="Activity">
    <img src="https://img.shields.io/github/last-commit/lafetamarcelo/epidemicModels" /></a>
  <a href="https://readthedocs.org/projects/epidemicmodels/">
    <img src="https://readthedocs.org/projects/epidemicmodels/badge/?version=latest" alt="build status"></a>
</p>


In this project we present a course on epidemy modelling, resulting in an algorithm capable of estimating the parameters of several types of epidemy models. The course is structured as:

- Analytical Models: for now we have the SIR model.
- Stochastic Models: currently with the Read Frost model.
- Data driven analysis: this set of analysis are differentiated by past epidemy analysis (such as the United Kingdom one), and the currently COVID epidemy.

The final content, a model capable of learning from epidemy`s data the defined model structure parameters, can be used by just clonning this repository, and acessing the [models](/models/) folder as:

```Python

from models import *

# Size of the population
N = 200000
# The model structure
model_type = ("S", "I", "R")

# Create the model
model = ss.epidemicModel(pop=N, focus=model_type)

# Train the model
model.fit( {"S": s_data, "I": i_data, "R": r_data}, time_vec )

# Predict the outputs
S_pred, I_pred, R_pred = model.predict((S_0, I_0, R_0), time_vec)

```

