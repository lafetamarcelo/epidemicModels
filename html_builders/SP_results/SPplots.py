
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



if __name__ == "__main__":

  # Lendo os dados online
  data_path = 'https://raw.githubusercontent.com/wcota/covid19br/master/cases-brazil-states.csv'

  SPdata = pd.read_csv(data_path, delimiter=",") 
  SPdata.head()

  is_state = SPdata['state']=="SP"
  SPdata = SPdata[is_state]

  SPdata = SPdata[SPdata.recovered.notnull()]
  SPdata.head()

  first_date = SPdata["date"].iloc[0]
  first_date = datetime.fromisoformat(first_date)

  N = 11869660
  I = SPdata["totalCases"].to_numpy()
  M = SPdata["deaths"].to_numpy()
  R = SPdata["recovered"].to_numpy()

  sir_model = ss.SIR()

  S = N - I - R
  time = np.linspace(0, len(I), len(I))

  # Estimando os parâmetros
  sir_model.fit(S, I, None, time, beta_sens=[1000,1], r_sens=[100,10])

  initial = [S[0], I[0]] 
  results = sir_model.predict(initial, time)


  # Criando os valores de tempo para previsão - 70 dias
  t_sim = np.linspace(0, len(I) + 70, len(I) + 70)
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
  source = ColumnDataSource(data={
    'Data'       : date_vec,
    'd': day, 'm': month, 'y': year,
    'Infectados' : I,
    'Removidos'  : R,
    'Mortes'     : M,
    'InfecModelo' : prediction[1],
    'DataModelo'  : date_vec_sim,
    'ds': day_sim, 'ms': month_sim, 'ys': year_sim
  })

      
  # Criando a figura
  p = figure(
    plot_height=500,
    plot_width=600,
    x_axis_type="datetime", 
    tools="", 
    toolbar_location=None,
    y_axis_type="log",
    title="Previsão do COVID - São Paulo")

  # Preparando o estilo
  p.grid.grid_line_alpha = 0
  p.ygrid.band_fill_color = "olive"
  p.ygrid.band_fill_alpha = 0.1
  p.yaxis.axis_label = "Indivíduos"
  p.xaxis.axis_label = "Dias"

  # Incluindo as curvas
  i_p = p.line(x='Data', y='Infectados', legend_label="Infectados", line_cap="round", line_width=3, color="#ffd885", source=source)
  m_p = p.line(x='Data', y='Mortes', legend_label="Mortes", line_cap="round", line_width=3, color="#de425b", source=source)
  r_p = p.line(x='Data', y='Removidos', legend_label="Removidos", line_cap="round", line_width=3, color="#99d594", source=source)

  mp_p = p.line(x='DataModelo', y='InfecModelo', legend_label="Infectados - Modelo", line_dash="dashed", line_cap="round", line_width=4, color="#f57f17", source=source)

  renders = [i_p, m_p, r_p, mp_p]
      
  # Colocando as legendas
  p.legend.click_policy="hide"
  p.legend.location = "bottom_right"

  # Incluindo a ferramenta de hover
  p.add_tools(HoverTool(
      tooltips=[
          ( 'Indivíduos', '$y{0.00 a}' ),
          ( 'Data',       '@ds/@ms/@ys'),
      ],
      renderers=renders
  ))

  output_file("SP_result.html", title="SP Predições")

  show(p)
