import pickle

import requests
import pandas as pd

from bokeh.models   import Legend, ColumnDataSource, RangeTool, LinearAxis, Range1d, HoverTool
from bokeh.palettes import brewer, Inferno256
from bokeh.plotting import figure, show, output_file
from bokeh.layouts  import column

if __name__ == '__main__':

    saved_param = pickle.load( open( "IT_saved_param.p", "rb" ) )
    saved_prediction = pickle.load( open( "IT_saved_prediction.p", "rb" ) )['pred']
    td, Id, Rd, N, t, pred_t = pickle.load( open( "IT_API_values.p", "rb" ) )['API']
    country = {'data':{'name':'Itália'}}

    p2 = figure(plot_height=500,
           plot_width=600, 
           tools="", 
           toolbar_location=None,
           title="Previsão Infectados - " + country['data']['name'])

    x = t[35:]
    index = 20

    # Preparando o estilo
    p2.grid.grid_line_alpha = 0
    p2.ygrid.band_fill_color = "olive"
    p2.ygrid.band_fill_alpha = 0.1
    p2.yaxis.axis_label = "Indivíduos"
    p2.xaxis.axis_label = "Dias"

    # Incluindo as curvas
    for data in saved_prediction[:45]:
        p2.line(pred_t, data[1],
            legend_label="Previsão Infectados", 
            line_cap="round", line_width=4, color="#42a5f5", line_alpha = 0.1)
        
    p2.line(td, Id,
        legend_label="Infectados", 
        line_cap="round", line_width=5, color="#c62828")

    # Colocando as legendas
    p2.legend.click_policy="hide"
    p2.legend.location = "top_right"

    output_file("IT_infectados_COVID.html", title="Predições Infectados Itália")

    show(p2)
