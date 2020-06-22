import requests
import pandas as pd
import numpy as np
from bokeh.models import Div

from bokeh.io       import output_notebook

output_notebook()

covid_api = 'https://corona-api.com/countries/'
rest_countries = 'https://restcountries.eu/rest/v2/alpha/'
country = 'IT' # Alpha-2 ISO3166

data_json =  requests.get(covid_api + country).json()
country = requests.get(covid_api + country).json()

Nr = country['data']['population']

print(country['data']['name'])


from datetime import datetime

df = pd.DataFrame(data_json['data']['timeline'])
df = df.sort_values('date').reset_index()

from datetime import datetime, timedelta
df['date'] = [datetime.fromisoformat(f) for f in df['date']]
df = df.drop_duplicates(subset='date', keep = 'last')

# Criando o vetor de tempo
first_date = df['date'].iloc[0]
size_days = (df['date'].iloc[-1] - df['date'].iloc[0]).days
date_vec = [first_date + timedelta(days=k) for k in range(size_days)]

new_df = pd.DataFrame(date_vec, columns=['date'])
new_df = pd.merge(new_df, df, how='left', on= 'date')
new_df = new_df.drop(columns= ['index',  'updated_at', 'is_in_progress'])

for col in new_df.columns[1:]:
    new_df[col] = new_df[col].interpolate(method='polynomial', order=1)
df = new_df.dropna()

Ir = df['active'].to_numpy()
Rr = df['recovered'].to_numpy()
Mr = df['deaths'].to_numpy()
Sr = Nr - Rr - Ir

# Creating the time vector
tr = np.linspace(0, len(Ir)-1, len(Ir))


Sd, Id, Md, Rd, td = Sr, Ir, Mr, Rr, tr



# ## Generate Data
import numpy as np

from bokeh.layouts import column, row
from bokeh.models import CustomJS, Slider
from bokeh.plotting import ColumnDataSource, figure, output_file, show

length = len(Id)
x = np.linspace(0, length-1, length)

# Valores Italia
N = 60000000
initial_beta = 6.75394656e+01
initial_r    = 2.23313371e-02
initial_I0   = 3
initial_S0   = N * 3.03594922e-03
initial_R0   = 0


S,I,R = np.zeros([length], dtype=np.float64),        np.zeros([length], dtype=np.float64),        np.zeros([length], dtype=np.float64)


S[0], I[0], R[0] = initial_S0,                   initial_I0,                   initial_R0


for i in range(1,length):
    S[i] = S[i-1] - S[i-1]*I[i-1]*initial_beta/N;
    I[i] = I[i-1] + S[i-1]*I[i-1]*initial_beta/N - initial_r*I[i-1];
    R[i] = R[i-1] + I[i-1]*initial_r


# ## IR grahp
source = ColumnDataSource(data=dict(x=x, S=S, I=I, R=R, Id=Id))
plot = figure(y_range=(0, np.ceil(max(R)*1.2)),
              x_range=(0, len(I)-1),
              plot_width=750, plot_height=600,
              tools="", toolbar_location=None,
              title="Ajuste os parâmetros do modelo você mesmo!",)

# Preparando o estilo
plot.grid.grid_line_alpha = 0
plot.ygrid.band_fill_color = "olive"
plot.ygrid.band_fill_alpha = 0.1
plot.yaxis.axis_label = "Indivíduos"
plot.xaxis.axis_label = "Dias"

plot.line('x', 'I', 
          source=source, 
          line_width=4,
          line_alpha=1, 
          color = '#ff6659', 
          legend_label="Ajuste Infectados"
         )

plot.line('x', 'R', source=source,
          line_width=4,
          line_alpha=1,
          color = '#00600f',
          legend_label="Ajuste Recuperados"
         )

plot.line(td, Id,
          line_width=4,
          line_alpha=1,
          color = '#9a0007',
          line_dash='dashed',
          legend_label="Itália Infectados"
         )

plot.line(td, Rd,
          line_width=4,
          line_alpha=1,
          color = '#6abf69',
          line_dash='dashed',
          legend_label="Itália Recuperados"
         )

sense = [10,10]
n_steps = 100

start_beta,end_beta = 0, 100
start_r   ,end_r    = 0, initial_r*2   
start_S0  ,end_S0   = 0  , 1
        
step_beta = (start_beta- end_beta)/ n_steps  
step_r    = (start_r   - end_r   )/ n_steps    
step_S0   = (start_S0  - end_S0  )/ 1000  
        
beta_slider     = Slider(start= 0, end=10, value=initial_beta/10, step=0.1, title="U")
beta_exp_slider = Slider(start=-9, end=3,  value=1              , step=1,   title="V" , width = 100 )

r_slider    = Slider(start=0 , end=10 , value=2.2   , step=step_r  , title="W")
r_exp_slider= Slider(start=-9, end=3  , value=-2    , step=1       , title="X", width = 100)

S0_slider    = Slider(start=0 , end=10 , value=1.8215 ,step=0.01 , title="Y")
S0_exp_slider= Slider(start=4        , end=7      , value=5      , step=1   , title="Z", width = 100)


I0_slider   = Slider(start=initial_I0-1, end=initial_I0+1, value=initial_I0  , step=1    , title="I0")
R0_slider   = Slider(start=0           , end=10      , value=0           ,step=1         , title="R0")
N_slider    = Slider(start=N-1         , end=N+1     , value=N           ,step=1         , title="N")

callback = CustomJS(args=dict(source=source, beta=beta_slider, r=r_slider,
                              S0=S0_slider, exps0 = S0_exp_slider,I0=I0_slider, R0=R0_slider, N=N_slider,
                              expbs = beta_exp_slider, exprs = r_exp_slider),
                    code="""
    const data = source.data;
    var bv = beta.value;
    const expbv = expbs.value;
    const exprv = exprs.value;
    const exps0v = exps0.value;
    var rv = r.value;
    const I0v = I0.value;
    const S0v = S0.value;
    const R0v = R0.value
    const Nv  = N.value;
    const x = data['x'];
    
    bv = bv*Math.pow(10,expbv);
    rv = rv*Math.pow(10,exprv);
    
    const S = data['S'];
    const I = data['I'];
    const R = data['R'];
    
    
    S[0] = S0v*Math.pow(10,exps0v);
    I[0] = I0v;
    R[0] = R0v;
    
    for (var i = 1; i < S.length; i++) {
        S[i] = S[i-1] - S[i-1]*I[i-1]*bv/Nv;
        I[i] = I[i-1] + S[i-1]*I[i-1]*bv/Nv - rv*I[i-1];
        R[i] = R[i-1] + I[i-1]*rv;
    }
    source.change.emit();
""")



beta_slider.js_on_change('value', callback)
beta_exp_slider.js_on_change('value', callback)
r_slider.js_on_change('value', callback)
r_exp_slider.js_on_change('value', callback)
S0_slider.js_on_change('value', callback)
S0_exp_slider.js_on_change('value', callback)


empty = Div(text=""" <br> <br> <br> <br> <br> <br>""",
          width=200, height=150)

empty2 = Div(text="""<br>""",
          width=38, height=38)

div = Div(text="""Os valores nos sliders
abaixo representam as seguintes grandezas: <br> <br>
<center><img width="100" src="https://raw.githubusercontent.com/lafetamarcelo/epidemicModels/master/docs/images/res/par_equations.png"/></center><br>""",
          width=500, height=120)

plot.legend.location = "top_left"
layout = row(
    plot,
    column(empty,
           row(empty2,div),
           row(beta_slider,empty2, beta_exp_slider),
           row(r_slider,empty2, r_exp_slider),
           row(S0_slider,empty2, S0_exp_slider),
           ),
)


output_file("SIR-sliders.html", title="Modelo SIR")

show(layout)