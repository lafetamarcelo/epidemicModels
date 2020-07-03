import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.express as px
import pandas as pd

# library content support
import access_data as ad


# Creating content styles
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

colors = {
    'background': '#202124',
    'text': '#7FDBFF'
}

# Creating the main app
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)



# Creating the figures for the dashboard

fig_country_summary = ad.access_graph_hystory()
fig_last_variations = ad.access_graph_last_variation()
fig_history_variations = ad.access_graph_history_variation()


# Creating the app content

app.layout = html.Div(
  className='backcontainer', 
  children=[
    html.H1(
        children='Hello Dash',
        style={
            'textAlign': 'center',
            'color': colors['text']
        }
    ),

    html.Div(
      children='Dash: A web application framework for Python.', 
      style={
        'textAlign': 'center',
        'color': colors['text']
      }
    ),
    
    
    html.Div(
      style={
        'height': 50,
      }
    ),
    
    
    ##
    ##  MAIN ROW - 
    ##
    ##
    
    html.Div(
      className='grid-wrapper',
      children=[
        
        html.Div(
          className='grid-history',
          children=[
            html.Div(
              className='container',
              children=dcc.Graph(
                id='fig-country-summary',
                figure=fig_country_summary
              )
            )
          ]
        ),
        
        html.Div(
          className='grid-last-variations',
          children=[
            html.Div(
              className='container',
              children=dcc.Graph(
                id='fig-last-variations',
                figure=fig_last_variations
              )
            ),
          ]
        ),
        
        html.Div(
          className='grid-history-variations',
          children=[
            html.Div(
              className='container',
              children=dcc.Graph(
                id='fig-history-variations',
                figure=fig_history_variations, 
                config={
                  'displayModeBar': False
                }
              )
            ),
          ]
        )
        
        
      ]
    ),
    
    html.Div(
      style={
        'height': 100,
      }
    ),
    
    html.Div(
      className='spacer',
      children="  "
    ),
    
])

# Content routing


if __name__ == '__main__':
    app.run_server(debug=True)