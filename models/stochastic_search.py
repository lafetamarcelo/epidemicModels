

import os
import numpy as np
import scipy.signal as scs

from PyAstronomy import pyasl
from scipy.optimize import differential_evolution, leastsq
from scipy import integrate, interpolate

from bokeh.models   import ColumnDataSource, RangeTool, LinearAxis, Range1d
from bokeh.palettes import brewer, Inferno10
from bokeh.plotting import figure, show
from bokeh.layouts  import column
from bokeh.io       import output_notebook, export_png

output_notebook()

# import warnings
# warnings.filterwarnings("error")

# Estimate response structure
GLOBAL_ERROR_CONTROLLER = 10**14

# Default plot configs
TOOLS = "pan,zoom_in,zoom_out,save"
PLOT_WIDTH = 600
PLOT_HEIGHT = 400



class SIR:
  """
    
    This model concentrate all the developed algorithms to 
    represent data driven SIR model. Using the Scipy default 
    model structure.

  """


  def __init__(self,
      verbose=True):
    GLOBAL_ERROR_CONTROLLER = 10**14
    self.verbose = verbose
    self.iter_counter = 1
    self.data = {
      "data": {
        "original": [],
        "resampled": [],
        "simulated": [],
        "full": []
      },
      "pars": { 
        "beta": [], 
        "r": [] 
      },
      "time": []
    }
  
  def cost_function(self, p, Data, initial, t, w):
    """
      The function to compute the error to guide the learning
      algorithm. It computes the quadratic error.
      
      :param tuple p: Tuple with Beta and r parameters, respectivelly.
      :param array S: The suceptible data values.
      :param array I: The infected data values.
      :param array initial: The initial values of suceptible and infected, respectivelly.
      :param array t: The time respective to each sample.
      :param array w: The weight respective to the suceptible and infected errors.
      
      :return: The sum of the quadratic error, between simulated and real data.
      :rtype: float
    """
    # try:
    result = self.simulate(initial, t, p)
    erroS = (w[0] * (result[0]-Data[0])**2)
    erroI = (w[1] * (result[1]-Data[1])**2)
    if len(result) == 3:
      erroR = (w[2] * (result[2]-Data[2])**2)
    # Merging the error
    try:
      error = np.log10(sum(erroI) + sum(erroR))
    except:
      error = np.log10(sum(erroI))
    # print("SOLVED ONCE!!!!")
    # except:
    #   error = 10**14
    return error


  def differential_model(self, y, t, Beta, r):
    """
      The function that computes the diferential set of 
      equations of the SIR Epidemic Model.
      
      :param tuple y: Tuple with the suceptible and infected data.
      :param array t: The time respective to each y set of samples.
      :param float Beta: The Beta parameter.
      :param float r: The r parameter.
      
      :return: The derivative of the suceptible and infected data.
      :rtype: tuple
    """
    if len(y) == 2:
      S, I = y
      Sdot = -Beta * S * I
      Idot = Beta * S * I  - r * I
      return Sdot, Idot
    if len(y) == 3:
      S, I, R = y
      Sdot = -Beta * S * I
      Idot = Beta * S * I  - r * I
      Rdot = r * I
      return Sdot, Idot, Rdot


  def simulate(self, initial, time, theta):
    """
      The function that simulate the differential SIR
      model, by computing the integration of the 
      differential equations.
      
      :param array initial: The initial values of the infected and suceptible data.
      :param array time: The time points to simulate the model.
      :param array theta: The Beta parameter, and r parameter, respectivelly.
      
      :return: The values of the suceptible and infected, at time, respectivelly.
      :rtype: tuple
    """
    result = integrate.odeint(
      self.differential_model, 
      initial, time, 
      args=(
        theta[0], 
        theta[1]
      )
    ).T
    return result

  def predict(self, initial, t):
    """
      The function that uses the estimated parameters of the SIR model
      to predict the epidemy outputs (Suceptible, Infected and Recoverd)
      for the time samples provided, provided the initial conditions.
      
      :param array initial: The initial values of the infected, suceptible and recovered data.
      :param array time: The time points to simulate the model.
      
      :return: The values of the suceptible, infected and recovered, at time, respectivelly.
      :rtype: tuple
    """
    if hasattr(self, 'parameters'):
      return self.simulate(initial, t, self.parameters)
    else:
      print("Error! No parameter estimated!")


  def fit(self, Sd, Id, Rd, td,
      resample=False,
      beta_sens=[10000,1000],
      r_sens=[10000,1000],
      **kwargs):
    """
      The method responsible for estimating a set of beta and r 
      parameters for the provided data set. It assumes that in 
      the data there is only one epidemic period.
      
      :param array Sd: Array with the suceptible data.
      :param array Id: Array with the infected data.
      :param array Rd: Array with the recovered data.
      :param array td: The time respective to each set of samples. \
      :param array resample: The flag to set the resampling of the dataset. Default is :code:`False`. \
      :param list beta_sens: The beta parameter sensibility minimun and maximun boundaries, respectivelly. Default is :code:`[100,100]`. \
      :param list r_sens : The r parameter sensibility minimun and maximun boundaries, respectivelly. Default is :code:`[100,1000]`. \
      :param dict **kwargs: The differential evolution arguments.

    """
    # Computing the approximate values 
    # of the parameters to build the 
    # parameter boundaries
    beta_approx = 1 / Sd.max()
    r_approx = 1 / int(td[-1])
    # Computing the parameter bounds   
    x0 = [beta_approx, r_approx]
    lower = [x0[0]/beta_sens[0], x0[1]/r_sens[0]]
    upper = [beta_sens[1]*x0[0], r_sens[1]*x0[1]]
    # Create the train data for minimization
    # and compute the initial conditions for 
    # the model simulation
    if Rd is None:
      datatrain = (Sd, Id)
      y0 = [Sd[0], Id[0]] 
    else:
      datatrain = (Sd, Id, Rd)
      y0 = [Sd[0], Id[0], Rd[0]]  
    # Compute the error weight for each
    # differential equation resolution
    w = [max(Id)/max(Sd), 1, 1]
    if self.verbose:
      print("\t ├─ S(0) ─ I(0) ─ R(0) ─ ", y0)
      print("\t ├─ beta ─  ", x0[0], "  r ─  ", x0[1])
      print("\t ├─ beta bound ─  ", lower[0], " ─ ", upper[0])
      print("\t ├─ r bound ─  ", lower[1], " ─ ", upper[1])
      print("\t ├─ equation weights ─  ", w)
    # Minimaze the cost function
    summary = differential_evolution(
        self.cost_function, 
        list(zip(lower, upper)),
        maxiter=30000,
        popsize=15,
        mutation=(1.5, 1.99),
        strategy="best1exp",
        args=(datatrain, y0, td, w)
      )
    # Simulando os dados
    c = summary.x
    results = self.simulate(y0, td, c)
    # Printing summary
    if self.verbose:
      print("\t └─ Defined at: ", c[0], " ─ ", c[1], "\n")
    # Save the model parameters
    self.parameters = c

  def fit_multiple(self, Sd, Id, Bd, td, 
      threshold_prop=1,
      cases_before=10,
      filt_estimate=False,
      filt_window=55,
      beta_sens=[100,100],
      r_sens=[100,1000],
      out_type=0,
      **kwargs):
    """
      The method responsible for estimating a set of beta and r 
      parameters for each epidemy period existent in the provided
      dataset. It assumes that in the data there are several epidemic
      periods.
      
      :param array Sd: Array with the suceptible data.
      :param array Id: Array with the infected data.
      :param array Bd: Array with the births data.
      :param array td: The time respective to each set of samples.
      :param float threshold_prop: The standard deviation proportion used as threshold for windowing. Default is :code:`1.0`. \
      :param int cases_before: The number of back samples to check for the initial window point. Default is :code:`10`. \
      :param bool filt_estimate: Flag to use filtered data to estimate the model parameters. Default is :code:`False`. \
      :param int filt_window: The window size used on the filtering technique, only if :code:`filt_estimate=True`. Default is :code:`55`. \
      :param list beta_sens: The beta parameter sensibility minimun and maximun boundaries, respectivelly. Default is :code:`[100,100]`. \
      :param list r_sens : The r parameter sensibility minimun and maximun boundaries, respectivelly. Default is :code:`[100,1000]`. \
      :param int out_type: The output type, it can be :code:`1` or :code:`0`. Default is :code:`0`.
      
      :return: If the :code:`out_type=0`, it returns a tuple with the estimated beta and r, estimated, with the year of each respective window. If `out_type=1` it returns the self.data of the model, a summary with all model information.
      :rtype: tuple
    
    """
    self.data["full"] = {
      "I": Id, "S": Sd, 
      "B": Bd, "t": td }
    # Find the epidemy start and end points
    start, end = findEpidemyBreaks(Id, threshold_prop, cases_before)
    # Check the window sizes
    if len(start) < 2:
      print("The windows are too small!")
    if len(start) != len(end):
      end = end[:-1]
    # Check the window sizes - 2
    if self.verbose:
      print("Windows starting at: ", start)
      print("Windows ending at:   ", end)
      print("Window start cases:  ", [Id[s] for s in start])
    # Computing the reference for the
    # parameters bounds 
    beta_approx = 1 / Sd.max()
    # For each epidemy window
    for s, e in zip(start, end):
      if self.verbose:
        print("New iter::: ", self.iter_counter)
        self.iter_counter += 1
      # Reading the SIR window variables
      B, S = Bd[s:e], Sd[s:e]
      I, t = Id[s:e], td[s:e]
      # Computing variables references 
      year_ref = t[0] # Year reference
      t = (t - year_ref) * 365 # Time in days
      # Initial conditions
      y0 = S[0], I[0]
      # Parameter weights
      w = [max(I)/max(S), 1]
      # Resampling the data
      Sd_res, t_res = scs.resample(S, int(t[-1]), t=t)
      Id_res, t_res = scs.resample(I, int(t[-1]), t=t)
      # Filtering the values
      if filt_estimate:
        Sd_res = pyasl.smooth(Sd_res, filt_window, 'hamming')
        Id_res = pyasl.smooth(Id_res, filt_window, 'hamming')
      # Computing the reference for
      # the parameter bounds
      r_approx = 1 / int(t[-1])
      # Computing the parameter bounds   
      x0 = [beta_approx, r_approx]
      lower = [x0[0]/beta_sens[0], x0[1]/r_sens[0]]
      upper = [beta_sens[1]*x0[0], r_sens[1]*x0[1]]
      if self.verbose:
        print("\t ├─ S(0) ─  ", y0[0], "  I(0) ─  ", y0[1])
        print("\t ├─ beta ─  ", x0[0], "  r ─  ", x0[1])
        print("\t ├─ beta bound ─  ", lower[0], " ─ ", upper[0])
        print("\t ├─ r bound ─  ", lower[1], " ─ ", upper[1])
      #(c, kvg) = leastsq(obj, theta0, args=(Sd_res, Id_res, y0, t_res, w))
      c = differential_evolution(
          self.cost_function, 
          list(zip(lower, upper)),
          maxiter=4000, 
          popsize=15,
          mutation=(0.5, 1.2),
          strategy="best1exp",
          args=((Sd_res, Id_res), y0, t_res, w)
        ).x
      # Simulando os dados
      [Sa, Ia] = self.simulate(y0, t_res, c)
      # Save the year data
      self.data["data"]["original"].append(
        { "I": I, "B": B, "S": S, "t": t/365 + year_ref })
      self.data["data"]["resampled"].append(
        {"I": Id_res, "S": Sd_res, "t": t_res/365 + year_ref})
      self.data["data"]["simulated"].append(
        {"I": Ia, "S": Sa, "t": t_res/365 + year_ref})
      self.data["pars"]["beta"].append( c[0] )
      self.data["pars"]["r"].append( c[1] )
      self.data["time"].append( year_ref )
      # Printing summary
      if self.verbose:
        print("\t └─ Defined at: ", c[0], " ─ ", c[1], "\n")
    if out_type == 0:
      return (
        self.data["pars"]["beta"], 
        self.data["pars"]["r"],  
        self.data["time"] 
      )
    return self.data

  def result_summary(self,
      out_plot=False,
      plot_size=[600,400],
      save_results=False,
      folder_path="./",
      file_name="SIR_result_summary.png"
      ):
    """
      Method responsible for building a proper summary plot of 
      the estimate process of the SIR model.

      :param bool out_plot: Flag to output the bokeh.figure object.
      :param list plot_size: List with the plot size as `[width, height]`.
      :param bool save_results: Flag to save the results as a .png image.
      :param string folder_path: The path to the folder the user wants to save resulted image.
      :param string file_name: The name of the resulted image that will be saved.

      :return: If `out_plot=True`, it returns a bokeh.figure object with the builded plots.
      :rtype: bokeh.figure
    
    """
    # Getting the estimation dataset
    estimation_data = self.data
    #Building the estimated parameter info
    r = estimation_data["pars"]["r"]
    beta = estimation_data["pars"]["beta"]
    years = [int(t) for t in estimation_data["time"]]

    # Creating the parameter plot
    p = figure(
      tools="hover",
      y_range=(min(beta), max(beta)), 
      plot_width=plot_size[0], 
      plot_height=plot_size[1]
    )

    # Plotting the beta parameter
    p.line(years, beta, 
      legend_label="beta", 
      line_width=4, 
      color="#c2185b", 
      line_cap='round', 
      line_alpha=0.9
    )
    # Creating the extra y axis for plotting the r parameter
    p.extra_y_ranges = {"r_axis": Range1d(start=min(r), end=max(r))}
    p.add_layout(LinearAxis(y_range_name="r_axis"), 'left')
    # Plotting the r parameter
    p.line(years, r, 
      y_range_name="r_axis", 
      line_dash='dashed',
      legend_label="r", 
      line_width=3, 
      color="#8e44ad", 
      line_cap='round', 
      line_alpha=0.9
    )
    # Building figure background
    p.grid.grid_line_alpha = 0
    p.ygrid.band_fill_color = "olive"
    p.ygrid.band_fill_alpha = 0.1
    p.xaxis.axis_label = "Ano"
    p.toolbar.autohide = True
    # Creating the estimation plot
    p1 = figure(
      tools="hover",
      x_range=p.x_range,
      plot_width=plot_size[0], 
      plot_height=plot_size[1]
    )
    # Plotting the full data
    p1.line(estimation_data["full"]["t"], estimation_data["full"]["I"],
      legend_label="Casos", 
      line_width=2, 
      color="#f4511e", 
      line_cap='round', 
      line_alpha=0.9
    )
    # Plotting the windowed original data
    for dataset in estimation_data["data"]["original"]:
      p1.line(dataset["t"], dataset["I"], 
        legend_label="Casos", 
        line_width=4, 
        color="#f4511e", 
        line_cap='round', 
        line_alpha=0.9
      )
    # Plotting the estimated data
    for dataset in estimation_data["data"]["simulated"]:
      p1.line(dataset["t"], dataset["I"], 
        line_dash='dashed',
        legend_label="Estimado", 
        line_width=3, 
        color="#0288d1", 
        line_cap='round', 
        line_alpha=0.9
      )
    # Buildging figure background
    p1.grid.grid_line_alpha = 0
    p1.ygrid.band_fill_color = "olive"
    p1.ygrid.band_fill_alpha = 0.1
    p1.yaxis.axis_label = "Indivíduos"
    p1.xaxis.axis_label = "Ano"
    p1.toolbar.autohide = True

    if save_results:
      if not os.path.exists(folder_path):
        os.mkdir(folder_path)
      file_path = folder_path + file_name
      export_png(column(p,p1), filename=file_path)
    if out_plot:
      return column(p,p1)


def findEpidemyBreaks(cases, 
    threshold_prop=1.0, 
    cases_before=10):
  """
    The function responsible for determining the initial 
    and final points of the epidemies windows.

    :param array cases: The array with the cases values along time.
    :param float threshold_prop: The standard deviation proportion used as threshold for windowing. Default is `1.0`.
    :param int cases_before: The number of back samples to check for the initial window point. Default is `10`.
    
    :return: With the list of window's starting points and window's final points, respectively.
    :rtype: tuple
  """
  # Filtering the data
  filt_cases = pyasl.smooth(cases, 11, 'hamming')
  # Compute the derivative and standard deviation
  cases_variation = np.diff(filt_cases).tolist()
  threshold = threshold_prop * np.std(cases_variation)
  # Initializing the variables
  start_points, end_points = [], []
  in_epidemy = False
  for k, value in enumerate(cases_variation):
    if not in_epidemy:
      # Check value
      if value > threshold:
        in_epidemy = True
        # Find the start point
        start_index = 0 if k-cases_before < 0 else k-cases_before
        window = [abs(v) for v in cases_variation[start_index:k]]
        ref_index = window.index(min(window))
        start_index = k - (cases_before - ref_index)
        if cases[start_index] == 0:
          while cases[start_index] == 0:
            start_index += 1
        start_points.append(start_index)
    else:
      check_1 = (cases_variation[k-1] < 0)
      check_2 = (value >= 0)
      if check_1 and check_2:
        in_epidemy = False
        end_points.append(k)
  return start_points, end_points