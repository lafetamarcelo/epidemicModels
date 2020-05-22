import pickle

from bokeh.models import ColumnDataSource, RangeTool, LinearAxis, Range1d
from bokeh.palettes import brewer, Inferno10
from bokeh.plotting import figure, show, output_file
from bokeh.layouts import column
from bokeh.io import output_notebook


if __name__ == "__main__":


  with open('UK_estimated_data.pickle', 'rb') as handle:
    pickle_data = pickle.load(handle)

  data = pickle_data["data"]
  final_data = pickle_data["final"]

  source = ColumnDataSource(data=dict(date=data["time"].to_numpy(), value=data["cases"].to_numpy()))

  p = figure(plot_height=300, plot_width=600, tools="xpan", toolbar_location=None,
            x_axis_location="above", x_range=(data["time"][5], data["time"][105]))

  p.line('date', 'value', source=source, 
        legend_label="Casos", line_width=2, color="#f4511e", line_cap='round', line_alpha=0.9)

  for dataset in final_data["data"]["resampled"]:
      rsource = ColumnDataSource(data=dict(date=dataset["t"], value=dataset["I"]))
      p.scatter('date', 'value', source=rsource, 
        legend_label="Casos reamostrados", fill_color="#8e44ad", size=4, line_alpha=0)

  p.yaxis.axis_label = 'Indivíduos'
  p.grid.grid_line_alpha = 0
  p.xgrid.band_fill_color = "navy"
  p.xgrid.band_fill_alpha = 0.1
  p.toolbar.autohide = True

  select = figure(title="Drag the middle and edges of the selection box to change the range above",
                  plot_height=130, plot_width=600, y_range=p.y_range,
                  y_axis_type=None, tools="", toolbar_location=None)

  range_tool = RangeTool(x_range=p.x_range)
  range_tool.overlay.fill_color = "navy"
  range_tool.overlay.fill_alpha = 0.2

  select.line('date', 'value', source=source,
              line_width=2, color="#f4511e", line_cap='round', line_alpha=0.9)
  select.ygrid.grid_line_color = None
  select.add_tools(range_tool)
  select.toolbar.active_multi = range_tool
  select.xaxis.axis_label = 'Ano'

  p1 = figure(plot_height=300, plot_width=600, tools="xpan", toolbar_location=None,
              x_axis_location="above", x_range=p.x_range)

  p1.line('date', 'value', source=source, 
        legend_label="Casos", line_width=2, color="#f4511e", line_cap='round', line_alpha=0.9)

  for dataset in final_data["data"]["simulated"]:
      psource = ColumnDataSource(data=dict(date=dataset["t"], value=dataset["I"]))
      p1.line('date', 'value', source=psource, line_dash="dashed",
            legend_label="Modelo estimado", color="#0288d1", 
            line_width=4, line_cap='round', line_alpha=0.9)
      
      window_bound_lower = [dataset["t"][0], dataset["t"][0]]
      window_bound_upper = [dataset["t"][-1], dataset["t"][-1]]
      window_limits = [0, 10000]
      
      p.line(window_bound_lower, window_limits, line_dash="dashed",
            legend_label="Janela da epidemia", color="#455a64", 
            line_width=2, line_cap='round', line_alpha=0.2)
      p.line(window_bound_upper, window_limits, line_dash="dashed",
            legend_label="Janela da epidemia", color="#455a64", 
            line_width=2, line_cap='round', line_alpha=0.2)
      p1.line(window_bound_lower, window_limits, line_dash="dashed",
            legend_label="Janela da epidemia", color="#455a64", 
            line_width=2, line_cap='round', line_alpha=0.2)
      p1.line(window_bound_upper, window_limits, line_dash="dashed",
            legend_label="Janela da epidemia", color="#455a64", 
            line_width=2, line_cap='round', line_alpha=0.2)

  p1.xaxis.axis_line_alpha = 0
  p1.xaxis.major_label_text_color = None
  p1.xaxis.major_tick_line_color = None
  p1.xaxis.minor_tick_line_color = None
  p1.yaxis.axis_label = 'Indivíduos'
  p1.grid.grid_line_alpha = 0
  p1.xgrid.band_fill_color = "navy"
  p1.xgrid.band_fill_alpha = 0.1
  p1.toolbar.autohide = True

  output_file("UK_result.html", title="UK Predições")

  show(column(p, p1, select))