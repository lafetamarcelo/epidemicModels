
import pickle
import pandas as pd
import numpy as np

from datetime import datetime
from datetime import timedelta

import sys
sys.path.append("../../")

# Importando o modelo SIR
from models import *

from bokeh.models import ColumnDataSource, RangeTool, LinearAxis, Range1d, HoverTool
from bokeh.palettes import brewer, Inferno10
from bokeh.plotting import figure, show, output_file
from bokeh.layouts import column
from bokeh.io import output_notebook

only_SP = False
clean_plot = True


if __name__ == "__main__":

  # Lendo os dados online
  data_path = 'https://raw.githubusercontent.com/wcota/covid19br/master/cases-brazil-states.csv'

  online_data = pd.read_csv(data_path, delimiter=",") 
  online_data.head()

  # Selecionando a região
  if only_SP:
    at_state = online_data['state']=="SP"
  else:
    at_state = online_data['state']=="TOTAL"

  local_data = online_data[at_state]

  local_data = local_data[local_data.recovered.notnull()]
  local_data.head()

  first_date = local_data["date"].iloc[0]
  first_date = datetime.fromisoformat(first_date)

  if only_SP:
    N = 11869660
  else:
    N = 220e6
    
  I = list()                                       # <- I(t)
  R = local_data["recovered"].iloc[1:].to_numpy()  # <- R(t)
  
  M = local_data["newDeaths"].iloc[1:].to_numpy()  # <- dM(t)
  nR = np.diff(local_data["recovered"].to_numpy()) # <- dR(t)
  nC = local_data["newCases"].iloc[1:].to_numpy()  # <- dC(t)
  
  # Condições iniciais
  I = [ local_data["totalCases"].iloc[1] ]         # <- I(0)
  # Calculando cada I(t)
  for t in range(len(M)-1):
    I.append(I[-1] + nC[t] - M[t] - nR[t])         # I(t) <- I(t-1) + newCases(t) - newDeaths(t) - newRecovered(t)
  I = np.array(I)

  sir_model = ss.SIR(pop=N, focus=["I","R"])

  S = N - I - R
  time = np.linspace(0, len(I), len(I))

  # Estimando os parâmetros
  if only_SP:
    sir_model.fit(S, I, None, time, beta_sens=[1000,10], r_sens=[1000,10])
    initial = [S[0], I[0]] 
  else:
    sir_model.fit(S, I, R, time, beta_sens=[10000,10], r_sens=[1000,10])
    initial = [S[0], I[0], R[0]]

  print("Sumarry Ro -> ", sir_model.parameters[0]/sir_model.parameters[1])

  results = sir_model.predict(initial, time)

  # Criando os valores de tempo para previsão - 120 dias
  t_sim = np.linspace(0, len(I) + 120, len(I) + 120)
  date_vec_sim = [first_date + timedelta(days=k) for k in t_sim]

  # Prevendo para os valores selecionados
  prediction = sir_model.predict(initial, t_sim)

  # Criando o gráfico com as predições
  
  # Criando os valores para legenda no plot
  
  # Criando o vetor de tempo
  date_vec = [ first_date + timedelta(days=k) for k in range(len(M))]
  # Criando os valores para legenda no plot
  year =  [str(int(d.year)) for d in date_vec ]
  month = [("0"+str(int(d.month)))[-2:] for d in date_vec ]
  day =   [("0"+str(int(d.day)))[-2:] for d in date_vec ]

  year_sim =  [str(int(d.year)) for d in date_vec_sim ]
  month_sim = [("0"+str(int(d.month)))[-2:] for d in date_vec_sim ]
  day_sim =   [("0"+str(int(d.day)))[-2:] for d in date_vec_sim ]

  # Criando a fonte de dados
  if only_SP:
    source = ColumnDataSource(data={
      'Data'       : date_vec,
      'd': day, 'm': month, 'y': year,
      'Infectados' : I,
      'Mortes'     : M,
      'Removidos'  : R,
      'InfecModelo' : prediction[1],
      'DataModelo'  : date_vec_sim,
      'ds': day_sim, 'ms': month_sim, 'ys': year_sim
    })
  else:
    source = ColumnDataSource(data={
      'Data'       : date_vec,
      'd': day, 'm': month, 'y': year,
      'Infectados' : I,
      'Removidos'  : R,
      'Mortes'     : M,
      'InfecModelo' : prediction[1],
      'RemovModelo' : prediction[2],
      'DataModelo'  : date_vec_sim,
      'ds': day_sim, 'ms': month_sim, 'ys': year_sim
    })

      
  # Criando a figura
  if only_SP:
    title_exp = "São Paulo"
  else:
    title_exp = "Brasil"

  p = figure(
    plot_height=500,
    plot_width=600,
    x_axis_type="datetime", 
    tools="", 
    toolbar_location=None,
    #y_axis_type="log",
    title="Previsão do COVID - " + title_exp)

  # Preparando o estilo
  p.grid.grid_line_alpha = 0
  p.ygrid.band_fill_color = "olive"
  p.ygrid.band_fill_alpha = 0.1
  p.yaxis.axis_label = "Indivíduos"
  p.xaxis.axis_label = "Dias"

  # Incluindo as curvas
  renders = []
  if not clean_plot:
    i_p = p.line(x='Data', y='Infectados', legend_label="Infectados", line_cap="round", line_width=3, color="#ffd885", source=source)
    renders.append(i_p)
    m_p = p.line(x='Data', y='Mortes', legend_label="Mortes", line_cap="round", line_width=3, color="#de425b", source=source)
    renders.append(m_p)
    r_p = p.line(x='Data', y='Removidos', legend_label="Removidos", line_cap="round", line_width=3, color="#99d594", source=source)
    renders.append(r_p)

  mp_p = p.line(x='DataModelo', y='InfecModelo', legend_label="Infectados - Modelo", line_dash="dashed", line_cap="round", line_width=4, color="#f57f17", source=source)
  renders.append(mp_p)

  if not only_SP:
    rp_p = p.line(x='DataModelo', y='RemovModelo', legend_label="Removidos - Modelo", line_dash="dashed", line_cap="round", line_width=4, color="#1b5e20", source=source)
    renders.append(rp_p)

  # Colocando as legendas
  p.legend.click_policy="hide"
  p.legend.location = "top_left"

  # Incluindo a ferramenta de hover
  p.add_tools(HoverTool(
      tooltips=[
          ( 'Indivíduos', '$y{0.00 a}' ),
          ( 'Data',       '@ds/@ms/@ys'),
      ],
      renderers=renders
  ))

  if only_SP:
    output_file("SP_result.html", title="SP Predições")
  else:
    output_file("BR_result.html", title="Brasil Predições")

  show(p)
