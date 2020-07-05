
# ======== SETUP VARIABLES ==========

#'big-query' / 'corona-api'
DATA_SOURCE = 'big-query'
PRED_SOURCE = 'big-query'  
COUNTRY = 'BR'

# PLOT 
BOKEH_THEME = 'Dark'       #'Light' / 'Dark'  
HEIGHT = 250
WIDTH = 550
# ===================================

import requests
import pandas as pd
import numpy as np
import pickle
from datetime import datetime, timedelta

import pandas_gbq
from google.oauth2 import service_account

from bokeh.layouts import column, row
from bokeh.models import CustomJS, Slider
from bokeh.plotting import ColumnDataSource, figure, output_file, show
from bokeh.io import curdoc
from bokeh.themes import Theme
from bokeh.io import output_notebook
from bokeh.models import Div
output_notebook()

title_dict = {'CN': '🇨🇳 China',
              'IT': '🇮🇹 Itália',
              'BR': '🇧🇷 Brasil',
              'DE': '🇩🇪 Alemanha'}

start_days = {'IT':8,
              'DE':8,
              'CN':8,
              'BR':8}

credential_path = '../../app/services/update-countries/keys/epidemicapp-62d0d471b86f.json'
project_id = "epidemicapp-280600"
credentials = service_account.Credentials.from_service_account_file(    
                                credential_path
                                )

def get_corona_api_data(Country_A2):
    # Import Data
    covid_api = 'https://corona-api.com/countries/'
    data_json =  requests.get(covid_api + Country_A2).json()
    country = requests.get(covid_api + Country_A2).json()
    N = country['data']['population']

    # Organize Data
    df = pd.DataFrame(data_json['data']['timeline'])
    df = df.sort_values('date').reset_index()
    df['date'] = [datetime.fromisoformat(f) for f in df['date']]
    df['date'] = df['date'].dt.tz_localize(None)
    df = df.drop_duplicates(subset='date', keep = 'last')

    # Date Vector
    first_date = df['date'].iloc[0]
    size_days = (df['date'].iloc[-1] - df['date'].iloc[0]).days
    date_vec = [first_date + timedelta(days=k) for k in range(size_days)]

    new_df = pd.DataFrame(date_vec, columns=['date'])
    new_df = pd.merge(new_df, df, how='left', on= 'date')
    new_df = new_df.drop(columns= ['index',  'updated_at', 'is_in_progress'])

    for col in new_df.columns[1:]:
        new_df[col] = new_df[col].interpolate(method='polynomial', order=1)
    df = new_df.dropna()

    df.loc['date'] = df['date'].dt.tz_localize(None)
    first_date = df['date'].iloc[0]

    I = df['active'].to_numpy()
    R = df['recovered'].to_numpy()
    S = N - R - I
    t = np.linspace(0, len(I), len(I))
    return S, I, R, t, N, first_date

def get_prediction_pickle(Country_A2):
    pickle_path = './MonteCarloRuns/' + Country_A2 + '_mc_runs.pickle'

    with open(pickle_path, 'rb') as pickle_file:
        content = pickle.load(pickle_file)
        
    saved_prediction = content['pred']
    saved_param = content['pars']

    return saved_prediction, saved_param

def define_custom_theme(background_fill_color, border_fill_color):
    theme = Theme(json={
        'attrs': {
            'Figure': {
                'background_fill_color': background_fill_color,
                'border_fill_color': border_fill_color,
                'outline_line_color': border_fill_color
                },
            'Axis': {
                'axis_line_color': "white",
                'axis_label_text_color': "white",
                'major_label_text_color': "white",
                'major_tick_line_color': "white",
                'minor_tick_line_color': "white",
                'minor_tick_line_color': "white"
                },
            'Grid': {
                'grid_line_dash': [6, 4],
                'grid_line_alpha': .3
                },
            'Circle': {
                'fill_color': 'lightblue',
                'size': 10,
                },
            'Title': {
                'text_color': "white"
                }
            }
        })
    return theme


if __name__ == '__main__':

    # Get Data
    if DATA_SOURCE == 'corona-api':
        S, I, R, t, _, first_date = get_corona_api_data(COUNTRY)

    elif DATA_SOURCE == 'big-query': 
        _, _, _, _, N, _ = get_corona_api_data(COUNTRY)
        sql_command = 'SELECT * FROM `countries.real_data` WHERE country= "' + COUNTRY + '"'
        df_d = pandas_gbq.read_gbq(
                                         sql_command,
                                         project_id=project_id,
                                         col_order=['date','deaths','confirmed',
                                                    'active','recovered','new_confirmed',
                                                    'new_recovered','new_deaths','country'])


        df_d = df_d.sort_values(by = 'date').reset_index()

        I = df_d['active'].values
        R = df_d['recovered'].dropna().values
        S =  N - R - I
        t = np.linspace(0,len(I), len(I) + 1)
        
        try:
            df_d['date'] = pd.to_datetime(df_d['date'])
        # df_d['date'] = [datetime.fromisoformat(f) for f in df_d['date']]
        except:
            pass
        first_date = df_d['date'].dt.tz_localize(None)[0] 

    # Get prediction
    if PRED_SOURCE == 'pickle':
        START_DAY = start_days[COUNTRY]

        saved_prediction, _ = \
                         get_prediction_pickle(COUNTRY)

        extra_pred_time = len(saved_prediction[0][0,:]) - len(I)
        pred_t = np.array(range(int(t[-1])))

        Sp_l = np.array([s[0,:][:len(S)] for s in saved_prediction])
        Ip_l = np.array([s[1,:][:len(I)] for s in saved_prediction])
        Rp_l = np.array([s[2,:][:len(R)] for s in saved_prediction])

        delta = 0

    elif PRED_SOURCE == 'big-query':
        sql_command = 'SELECT * FROM `countries.predictions_SIRD` WHERE country= "' + COUNTRY + '"'
        df_p = pandas_gbq.read_gbq(
                                 sql_command,
                                 project_id=project_id,
                                 col_order=['S','I','R', 'D','date','at_date','country'],
                                 
                                 )

        df_p = df_p.sort_values(by = ['date','at_date']).reset_index()

        try:
            df_d['date'] = pd.to_datetime(df_d['date'])
        # df_d['date'] = [datetime.fromisoformat(f) for f in df_d['date']]
        except:
            pass
        # df_p['at_date'] = [datetime.fromisoformat(f) for f in df_p['at_date']]
        df_p['at_date'] = df_p['at_date'].dt.tz_localize(None)
        first_pred = df_p['at_date'].iloc[0]

        delta = 8
        START_DAY  = (first_pred - first_date).days - delta 

        Sp_l,Ip_l,Rp_l = [],[],[]
        for d in df_p.at_date.sort_values().unique():
            Sp_l.append(df_p[df_p['at_date'] == d]['S'][:-1].values.tolist())
            Ip_l.append(df_p[df_p['at_date'] == d]['I'][:-1].values.tolist())
            Rp_l.append(df_p[df_p['at_date'] == d]['R'][:-1].values.tolist())

        Sp_l = np.array(Sp_l)
        Ip_l = np.array(Ip_l)
        Rp_l = np.array(Rp_l)

        #extra_pred_time = Sp_l.shape[1] - len(I)
        #extra_pred_time = EXTRA_PRED_TIME
        pred_t = np.array(range(START_DAY, START_DAY + Sp_l.shape[1]))

    dia = START_DAY +  Sp_l.shape[0] + delta - 1

    # Make Graph
    s1 = ColumnDataSource(data={
                            'x':t[:len(I)],
                            'I':I[:len(I)],
                            'R':R[:len(I)]
                               })

    s2 = ColumnDataSource(data={
                                'dia':  np.array([dia]),
                                'start_day':  np.array([START_DAY + delta]),
                                'scS':  np.array([S[dia-1]]),
                                'scI':  np.array([I[dia-1]]),
                                'scR':  np.array([R[dia-1]])
                            })

    s3 = ColumnDataSource(data={
                                'Spl': Sp_l,
                                'Ipl': Ip_l,
                                'Rpl': Rp_l
                            })

    s4 = ColumnDataSource(data={
                                'x':pred_t,
                                'Sp': Sp_l[-1],
                                'Ip': Ip_l[-1],
                                'Rp': Rp_l[-1],
                                })

    title = 'Previsões COVID - ' + title_dict[COUNTRY]
    plot = figure(y_range=(0, np.ceil(max(R)*1.6)), plot_width=WIDTH, plot_height=HEIGHT,
                title=title, tools="", toolbar_location=None)
    
    plot.grid.grid_line_alpha = 0
    plot.yaxis.axis_label = " "
    plot.xaxis.axis_label = "Dias"

    # Real Data
    plot.line('x', 'I', source=s1, line_width=3, color = '#ff9900', legend_label="Infectados")
    plot.line('x', 'R', source=s1, line_width=3, color = '#68a92c', legend_label="Recuperados")
    
    # Prediction
    plot.line('x', 'Ip', source=s4, line_width=3, color = '#c66a00', line_dash  = 'dashed', legend_label="Previsão Infectados")
    plot.line('x', 'Rp', source=s4, line_width=3, color = '#367900', line_dash  = 'dashed', legend_label="Previsão Recuperados")

    # Scatter Selected Date 
    plot.circle('dia', 'scI', source=s2, size=10, color="#ff9900")
    plot.circle('dia', 'scR', source=s2, size=10, color="#68a92c")

    dias_slider = Slider(start=START_DAY + 1 + delta, end= START_DAY + delta +Sp_l.shape[0] - 1,
                         value=START_DAY +  Sp_l.shape[0] + delta - 1, step=1, title="Dia")

    callback = CustomJS(args=dict(s1=s1, s2=s2, s3=s3, s4=s4, dia_s=dias_slider),
                    code="""
                        const d1 = s1.data;
                        const d2 = s2.data;
                        const d3 = s3.data;
                        const d4 = s4.data;
                        
                        const dia_sv = dia_s.value;
                        
                        var I = d1['I'];
                        var R = d1['R'];
                        
                        var Sp = d4['Sp'];
                        var Ip = d4['Ip'];
                        var Rp = d4['Rp'];
                        
                        const len = Sp.length;
                        
                        var dia = d2['dia'];

                        const scS = d2['scS'];
                        const scI = d2['scI'];
                        const scR = d2['scR'];
                        const start = d2['start_day']
                        
                        const lSp = d3['Spl']
                        const lIp = d3['Ipl']
                        const lRp = d3['Rpl']
                        
                        dia[0] = dia_sv - 1;
                        
                        scI[0] = I[dia[0]];
                        scR[0] = R[dia[0]];
                        
                        var j = 0
                        for (var i = ( len * (dia[0] - start)); i < ( len * (dia[0] - start) + len); i++) {
                            Sp[j] = lSp[i]
                            Ip[j] = lIp[i]
                            Rp[j] = lRp[i]
                            j++
                        }
                        
                        s1.change.emit();
                        s2.change.emit();
                    """)


    dias_slider.js_on_change('value', callback)
    plot.legend.location = "top_left"

    if BOKEH_THEME == 'Dark':
        save_name =  './slider' + COUNTRY + 'dark.html'
        my_theme = define_custom_theme('#2C2F38','#2C2F38')
        plot.legend.background_fill_alpha = 0.0
        plot.legend.border_line_alpha = 0
        plot.legend.label_text_color = 'white'
        plot.xaxis.major_tick_line_color = None  # turn off x-axis major ticks
        plot.xaxis.minor_tick_line_color = None  # turn off x-axis minor ticks
        plot.yaxis.major_tick_line_color = None  # turn off y-axis major ticks
        plot.yaxis.minor_tick_line_color = None  # turn off y-axis minor ticks

    elif BOKEH_THEME == 'Light':
        save_name =  './slider' + COUNTRY + '.html'
        my_theme = 'caliber'
        plot.ygrid.band_fill_color = "olive"
        plot.ygrid.band_fill_alpha = 0.1

    doc = curdoc()
    doc.theme = my_theme
    doc.add_root(plot)


    div = Div(text="""<br> <br>""",
            width=90, height=38)

    layout = column(
        plot,
        row(div, dias_slider))

    output_file(save_name, title="Previsões COVID")
    show(layout)