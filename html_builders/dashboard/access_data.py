
import plotly.graph_objects as go

from google.oauth2 import service_account
import pandas as pd
import pandas_gbq
import numpy as np


key_path = "../../app/gkeys/epidemicapp-62d0d471b86f.json"
CREDENTIALS  = service_account.Credentials.from_service_account_file(key_path)
pandas_gbq.context.credentials = CREDENTIALS

# Gcloud project constants
PROJECT_ID = "epidemicapp-280600"

# Content queries for the graph
query_history = """
  select 
    date, 
    country, 
    confirmed, 
    active, 
    recovered, 
    deaths, 
    new_confirmed, 
    new_recovered,
    new_deaths
  from countries.real_data
  where country = "{}"
"""

def_colors = {
  "active": "#ff8f00",
  "recovered": "#43a047",
  "deaths": "#e53935",
  "confirmed": "#1e88e5" }



def access_graph_hystory(country="BR"):
  """
  """
  
  country_df = pandas_gbq.read_gbq(query_history.format(country), project_id=PROJECT_ID)
  
  fig = go.Figure()
  # Plotting the infected data
  
  fig.add_trace(go.Scatter(
    x=country_df["date"],
    y=country_df["recovered"],
    mode="lines",
    line_shape="spline",
    name="Recuperados",
    line=dict(color=def_colors["recovered"], width=2)
  ))
  
  fig.add_trace(go.Scatter(
    x=country_df["date"],
    y=country_df["deaths"],
    mode="lines",
    line_shape="spline",
    name="Mortes",
    line=dict(color=def_colors["deaths"], width=2)
  ))
  
  fig.add_trace(go.Scatter(
    x=country_df["date"],
    y=country_df["active"],
    mode="lines",
    line_shape="spline",
    name="Casos Ativos",
    line=dict(color=def_colors["active"], width=3)
  ))
  
  fig.update_layout(
    template='plotly_dark',
    font_family="Rockwell",
    title_text="Dados históricos do país",
    legend=dict(
      title=None, 
      orientation="h", 
      y=1, x=0.5,
      yanchor="bottom", 
      xanchor="center"
    ),
    height=500,
  )
  fig.update_xaxes(showgrid=False)
  
  return fig
  

  
  
def access_graph_last_variation(country="BR"):
  """
  """
  
  country_df = pandas_gbq.read_gbq(query_history.format(country), project_id=PROJECT_ID)
  
  last_variation = country_df.where(country_df["date"] == country_df["date"].max()).dropna()
  
  
  labels = ['Novos confirmados','Novas mortes','Novos recuperados']
  colors = [def_colors["active"], def_colors["deaths"], def_colors["recovered"]]
  values = [last_variation["new_confirmed"].tolist()[0], 
            last_variation["new_deaths"].tolist()[0],
            last_variation["new_recovered"].tolist()[0]]

  # pull is given as a fraction of the pie radius
  fig = go.Figure()
  fig.add_trace(go.Pie(
    labels=labels, 
    values=values, 
    marker_colors=colors
  ))
  fig.update_layout(
    template='plotly_dark',
    font_family="Rockwell",
    title_text="Últimas variações")
  fig.update_layout(
    showlegend=False,
    margin=dict(
        b=150, t=70
    )
  )
  return fig


def access_graph_history_variation(country="BR"):
  """
  """
  
  country_df = pandas_gbq.read_gbq(query_history.format(country), project_id=PROJECT_ID)
  
  
  variations = np.diff(country_df["active"].tolist()).tolist()
  variations = [0] + variations
  
  fig = go.Figure()
  fig.add_trace(go.Bar(
    x=country_df["date"].iloc[-60:], 
    y=variations[-60:],
    marker_color=def_colors["active"],
    name="Variação de ativos"
  ))
  
  fig.update_layout(
    template='plotly_dark',
    font_family="Rockwell",
    height=500, #width=300,
    xaxis=dict(showgrid=False, zeroline=True),
    yaxis=dict(showgrid=False, zeroline=False),
    showlegend=False,
    margin=dict(
        b=200, t=0, l=10, r=10
    )
  )
  
  fig.update_xaxes(showticklabels=False)
  fig.update_yaxes(showticklabels=False)
  
  return fig
  
  