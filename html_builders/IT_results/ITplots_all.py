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

    p3 = figure(plot_height=500,
            plot_width=600, 
            tools="", 
            toolbar_location=None,
            title="Previsão COVID - " + country['data']['name'])

    x = t[35:]
    index = 20
    plot_all = True

    # Preparando o estilo
    p3.grid.grid_line_alpha = 0
    p3.ygrid.band_fill_color = "olive"
    p3.ygrid.band_fill_alpha = 0.1
    p3.yaxis.axis_label = "Indivíduos"
    p3.xaxis.axis_label = "Dias"

    # Incluindo as curvas
    for data in saved_prediction[10:45]:
        p3.line(pred_t, data[1],
            legend_label="Previsão Infectados", 
            line_cap="round", line_width=4, color="#42a5f5", line_alpha = 0.1)

        p3.line(pred_t, data[0],
        legend_label="Previsão Suscetiveis", 
        line_cap="round", line_width=4, color="#ff5722", line_alpha = 0.07)
        
        p3.line(pred_t, data[2],
        legend_label="Previsão Recuperados", 
        line_cap="round", line_width=4, color="#9c27b0", line_alpha = 0.07)
        
        
    p3.line(td, Id,
        legend_label="Infectados", 
        line_cap="round", line_width=5, color="#005cb2", line_dash = 'dashed')

    if plot_all:
        p3.line(td, Rd,
            legend_label="Recuperados", 
            line_cap="round", line_width=5, color="#5e35b1", line_dash = 'dashed')

        p3.line(td, N*saved_param['pop'][-10] - Rd - Id,
            legend_label="Suscetiveis", 
            line_cap="round", line_width=5, color="#b71c1c", line_dash = 'dashed')

    # Colocando as legendas
    p3.legend.click_policy="hide"
    p3.legend.location = "top_right"

    output_file("IT_COVID.html", title="Predições Itália")

    show(p3)

    

    