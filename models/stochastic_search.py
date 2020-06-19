

import os
import numpy as np
import scipy.signal as scs

from PyAstronomy import pyasl
from scipy import integrate, interpolate

from scipy.optimize import differential_evolution, dual_annealing
from scipy.optimize import shgo, leastsq, NonlinearConstraint

from bokeh.models   import ColumnDataSource, RangeTool, LinearAxis, Range1d
from bokeh.palettes import brewer, Inferno10
from bokeh.plotting import figure, show
from bokeh.layouts  import column
from bokeh.io       import output_notebook, export_png

from . import differential_models as dm
from . import cost_functions as cm
from . import constraints as ct
from . import discrete_models as dcm

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
      pop=2000000,
      focus=["I","R"],
      algorithm="differential_evolution",
      simulation="discrete",
      stochastic_search=False,
      forced_search_pop=False,
      ode_full_output=False,
      verbose=True):
    # Main constants
    self.N = pop
    self.focus = focus
    self.verbose = verbose
    # Local variables
    self.__mc_props = [0.5, 0.75, 0.9, 1.5]
    self.__search_alg = algorithm
    self.__ssearch = stochastic_search
    # Semi Local variables
    self._iter_error = [10**14]
    self._search_pop = forced_search_pop
    # Simulation type
    self.__sim_type = simulation
    # Algorithm focus variables
    if 'D' in self.focus:
      if self.__sim_type == "discrete":
        self.__class__.differential_model = dcm.SIRD
      else:
        self.__class__.differential_model = dm.SIRD
      self.__class__.cost_function = cm.cost_SIRD
    elif 'E' in self.focus:
      self.__class__.differential_model = dm.SEIR
      self.__class__.cost_function = cm.cost_SEIR
    elif 'N' in self.focus:
      self.__class__.differential_model = dm.NSIR
      self.__class__.cost_function = cm.cost_NSIR
    else:
      if self.__sim_type == "discrete":
        self.__class__.differential_model = dcm.SIR
      else:
        self.__class__.differential_model = dm.SIR
      self.__class__.cost_function = cm.cost_SIR
    # The ODE full output option
    self.__ode_full_output = ode_full_output
    
    # Accumulating variables
    self.acc_error = dict()
    for m in ["S", "E", "I", "R"]:
      self.acc_error[m] = list()
    self.iter_counter = 1
    self.dataset = dict()
    self.ponder = False
    self.pipeline = {}
    self.mc = {
      "results": {}
    }
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


  def cost_wrapper(self, *args):
    """
      The method responsible for wrapping the cost function. 
      This allows differential evolution algorithm to run with parallel processing.
      
      :param tuple *args: cost function parameters
      
      :return: the cost function outputs
      :rtype: float
    """
    response = self.cost_function(*args)
    return response


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

    if self.__sim_type == "continuous":
      result = integrate.odeint(
        self.differential_model, 
        initial, 
        time,
        args=(theta),
        full_output=self.__ode_full_output
      ).T
    elif self.__sim_type == "ivp_continuous":
      result = integrate.solve_ivp(
        self.differential_model,
        (time[0], time[-1]), 
        initial,
        args=(theta),
        t_eval=time
      )
    else:
      result = self.differential_model(
        initial, time, theta)
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
      # Ponder the initial condition
      # if search pop is on...
      if self._search_pop:
        initial = list(initial) # If touple => list
        initial[0] = initial[0] * self.parameters[-1]
      result = self.simulate(initial, t, self.parameters)
      form_result = [r.astype(np.float64) for r in result]
      return form_result
    else:
      print("Error! No parameter estimated!")


  def fit(self, dataset, t,
      search_pop=True,
      Ro_bounds=None,
      pop_sens=[1e-3,1e-4],
      Ro_sens=[0.8,15],
      D_sens=[5,50],
      sigma_sens=None,
      mu_sens=[0.0001, 0.02],
      notified_sens=None,
      sample_ponder=None,
      optim_verbose=False,
      **kwargs):
    """
      The method responsible for estimating a set of beta and r 
      parameters for the provided data set. It assumes that in 
      the data there is only one epidemic period.
      
      :param array dataset: list with the respective arrays of Suceptible, Infected, Recovered and Deaths.
      :param array t: The time respective to each set of samples.
      :param bool search_pop: Flag to set the exposed population search, for better Suceptible extimation values. Default is :code:`True`.
      :param list Ro_bounds: The bounds to build the constraints for :code:`Ro = Beta / r`. With minimun and maximun values, respectivelly.
      :param list pop_sens: The sensibility (boudaries) for the proportion of :code:`N` to be found by the pop parameters.
      :param list beta_sens: The beta parameter sensibility minimun and maximun boundaries, respectivelly. Default is :code:`[100,100]`.
      :param list r_sens: The r parameter sensibility minimun and maximun boundaries, respectivelly. Default is :code:`[100,1000]`.
      :param bool sample_ponder: The flag to set the pondering of the non informative recovered data.
      :param bool optim_verbose: If :code:`True`, after fitting will show the optimization summary.
      :param dict **kwargs: The optimization search algorithms options.
    """
    # Create the data values including
    # the Susceptible, Infected, 
    # Recovered and Death data into 
    # their respective variables
    S, I, R, D = None, None, None, None
    if "S" in dataset:
      S = dataset["S"]
    if "R" in dataset:
      R = dataset["R"]
    if "D" in dataset:
      D = dataset["D"]
    I = dataset["I"]
    # Check for the several possible 
    # pondering variables and create
    # the flags to ensure pondering
    self.ponder = sample_ponder != None
    self.__exposed_flag = sigma_sens != None
    self._search_pop = search_pop
    # Computing the approximate values 
    # of the parameters to build the 
    # parameter boundaries
    lower = [Ro_sens[0], D_sens[0]]
    upper = [Ro_sens[1], D_sens[1]]
    # Create the nonlinear constraints for 
    # the basic parameters. Now only the 
    # Ro parameter contraint is checked.
    constraints = ()
    if Ro_bounds != None:
      nlc = NonlinearConstraint(ct.Ro_decimal_constr, Ro_bounds[0], Ro_bounds[1])
      constraints = (nlc)
    # Create the train data for minimization
    # and compute the initial conditions for 
    # the model simulation and the weights 
    # for pondering each time series
    w = [1/np.mean(S), 1/np.mean(I)]
    datatrain = [S, I]
    y0 = [S[0], I[0]] 
    if "R" in self.focus:
      datatrain.append(R)
      y0.append(R[0])
      w.append(1/np.mean(R))
    if "E" in self.focus:
      lower.append(sigma_sens[0])
      upper.append(sigma_sens[1])
      y0.insert(1, 1.0)
    if "N" in self.focus:
      for item in notified_sens.keys():
        print("\t ├─ Including {} bound!".format(item))
        lower.append(notified_sens[item][0])
        upper.append(notified_sens[item][1])
      y0.insert(2, I[0])
    if "D" in self.focus:
        lower.append(mu_sens[0])
        upper.append(mu_sens[1])
        datatrain.append(D)
        y0.append(D[0])
        w.append(1/np.mean(D))
    # Population proportion boundaries
    if self._search_pop:
      lower.append(pop_sens[0])
      upper.append(pop_sens[1])
    # Provide a summary of the model 
    # so far, and show the optimazation 
    # setup
    if self.verbose:
      print("\t ├─ S(0) ─ I(0) ─ R(0) ─ ", y0)
      print("\t ├─ Ro bound ─  ", lower[0], " ─ ", upper[0])
      print("\t ├─ D  bound ─  ", lower[1], " ─ ", upper[1])
      if self.__exposed_flag:
        print("\t ├─ sigma bound ─  ", lower[2], " ─ ", upper[2])
      print("\t ├─ equation weights ─  ", w)
      print("\t ├─ Running on ─ ", self.__search_alg, "SciPy Search Algorithm")
    # Run the searching algorithm to 
    # minimize the cost function... 
    # There are three possible minimization
    # algorithms to be used. This is 
    # controlled by the flag on the 
    # __init__ method.
    if self.__search_alg == "differential_evolution":
      summary = differential_evolution(
          self.cost_wrapper, 
          list(zip(lower, upper)),
          maxiter=10000,
          popsize=35,
          mutation=(0.5, 1.2),
          strategy="best1exp",
          tol=1e-4,
          args=(datatrain, y0, t, w),
          constraints=constraints,
          updating='deferred',
          workers=-1,
          # disp=True
        )
    elif self.__search_alg == "dual_annealing":
      summary = dual_annealing(
          self.cost_wrapper, 
          list(zip(lower, upper)),
          maxiter=10000,
          args=(datatrain, y0, t, w)
        )
    elif self.__search_alg == "shgo":
      summary = shgo(
          self.cost_wrapper,
          list(zip(lower, upper)),
          n=500, iters=10,
          sampling_method="sobol",
          args=(datatrain, y0, t, w)
        )
    # Saving the estimated parameters
    self.parameters = summary.x
    # Printing summary
    if self.verbose:
      print("\t └─ Defined at: ", self.parameters[0], " ─ ", self.parameters[1], "\n")
    if optim_verbose:
      print(summary)

  def fit_multiple(self, Sd, Id, Bd, td, 
      threshold_prop=1,
      cases_before=10,
      filt_estimate=False,
      filt_window=55,
      beta_sens=[100,10],
      r_sens=[100,10],
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
      :param float threshold_prop: The standard deviation proportion used as threshold for windowing. Default is :code:`1.0`.
      :param int cases_before: The number of back samples to check for the initial window point. Default is :code:`10`.
      :param bool filt_estimate: Flag to use filtered data to estimate the model parameters. Default is :code:`False`.
      :param int filt_window: The window size used on the filtering technique, only if :code:`filt_estimate=True`. Default is :code:`55`.
      :param list beta_sens: The beta parameter sensibility minimun and maximun boundaries, respectivelly. Default is :code:`[100,100]`.
      :param list r_sens: The r parameter sensibility minimun and maximun boundaries, respectivelly. Default is :code:`[100,1000]`.
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
    # Computing the approximate values 
    # of the parameters to build the 
    # parameter boundaries
    beta_approx = 1 
    r_approx = 1 / 10
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
      y0 = int(S[0]), int(I[0])
      # Parameter weights
      w = [max(I)/max(S), 1]
      # Resampling the data
      Sd_res, t_res = scs.resample(S, int(t[-1]), t=t)
      Id_res, t_res = scs.resample(I, int(t[-1]), t=t)
      # Filtering the values
      if filt_estimate:
        Sd_res = pyasl.smooth(Sd_res, filt_window, 'hamming')
        Id_res = pyasl.smooth(Id_res, filt_window, 'hamming')
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
          maxiter=60000,
          popsize=35,
          mutation=(1.5, 1.99),
          strategy="best1exp",
          workers=-1,
          updating='deferred',
          tol=0.00001,
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


  def monteCarlo_multiple(self, Sd, Id, Bd, td, 
      threshold_prop=1,
      cases_before=10,
      minimum_days=60,
      steps_indays=10,
      filt_estimate=False,
      filt_window=55,
      beta_sens=[1000,10],
      r_sens=[1000,10],
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
      :param float threshold_prop: The standard deviation proportion used as threshold for windowing. Default is :code:`1.0`.
      :param int cases_before: The number of back samples to check for the initial window point. Default is :code:`10`.
      :param bool filt_estimate: Flag to use filtered data to estimate the model parameters. Default is :code:`False`.
      :param int filt_window: The window size used on the filtering technique, only if :code:`filt_estimate=True`. Default is :code:`55`.
      :param list beta_sens: The beta parameter sensibility minimun and maximun boundaries, respectivelly. Default is :code:`[100,100]`.
      :param list r_sens: The r parameter sensibility minimun and maximun boundaries, respectivelly. Default is :code:`[100,1000]`.
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
      print("├─ Windows starting at: ", start)
      print("├─ Windows ending at:   ", end)
      print("├─ Window start cases:  ", [Id[s] for s in start])
      print("│")
    # Computing the approximate values 
    # of the parameters to build the 
    # parameter boundaries
    beta_approx = 1 
    r_approx = 1 / 7 
    # For each epidemy window
    for s, e in zip(start, end):
      if self.verbose:
        print("├──┬ ✣✣✣ New window ➙ ", self.iter_counter, " ✣✣✣")
        self.iter_counter += 1
      # Reading the SIR window variables
      B, S = Bd[s:e], Sd[s:e]
      I, t = Id[s:e], td[s:e]
      # Computing variables references 
      year_ref = t[0] # Year reference
      t = (t - year_ref) * 365 # Time in days
      # Initial conditions
      y0 = int(S[0]), int(I[0])
      # Parameter weights
      w = [max(I)/max(S), 1]
      # Resampling the data
      Sd_res, t_res = scs.resample(S, int(t[-1]), t=t)
      Id_res, t_res = scs.resample(I, int(t[-1]), t=t)
      # Filtering the values
      if filt_estimate:
        Sd_res = pyasl.smooth(Sd_res, filt_window, 'hamming')
        Id_res = pyasl.smooth(Id_res, filt_window, 'hamming')
      # Computing the parameter bounds   
      x0 = [beta_approx, r_approx]
      lower = [x0[0]/beta_sens[0], x0[1]/r_sens[0]]
      upper = [beta_sens[1]*x0[0], r_sens[1]*x0[1]]
      if self.verbose:
        print("│  ├─ S(0) ─  ", y0[0], "  I(0) ─  ", y0[1])
        print("│  ├─ beta ─  ", x0[0], "  r ─  ", x0[1])
        print("│  ├─ beta bound ─  ", lower[0], " ─ ", upper[0])
        print("│  ├─ r bound ─  ", lower[1], " ─ ", upper[1])
        print("│  │")
        print("│  ├─┬─ ⨭ Initializing Monte Carlo ⨮")
        self.__prop_ind = 0
      # Create the simulation steps
      initial_indexes = range(minimum_days, int(t[-1]), steps_indays)
      # Estimate for each sample set
      mc_window_data = dict(pars=list(), time=list(), bounds=[s,e])
      for bound in initial_indexes:
        # Get only a fraction of the data
        S_, I_, t_ = Sd_res[:bound], Id_res[:bound], t_res[:bound]
        # Minimize the cost funciton for 
        # the selected window
        c = differential_evolution(
          self.cost_function, 
          list(zip(lower, upper)),
          maxiter=60000, 
          popsize=15,
          mutation=(0.5, 1.5),
          strategy="best1exp",
          workers=-1,
          updating='deferred',
          tol=0.00001,
          args=((S_, I_), y0, t_, w)
        ).x # <- Get only the parameters
        # Print some information
        sim_prop = initial_indexes.index(bound) / len(initial_indexes)
        if self.verbose and (sim_prop > self.__mc_props[self.__prop_ind]):
          print("│  │ ├─ Progress at : {}%".format(int(100*sim_prop)))
          self.__prop_ind += 1
        # Save monte carlo estimated data
        mc_window_data["pars"].append(c)
        mc_window_data["time"].append(t_[-1]*365 + year_ref)
      if self.verbose and (sim_prop > 0.5):
        print("│  │ └─ Finished! ✓")
      # Save the window data
      self.mc["results"][str(self.iter_counter-1)] = mc_window_data
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
        print("│  └─ ✣✣✣ ➙ ", self.iter_counter-1, " ✣✣✣\n│")
    if self.verbose:
      print("│")
      print("└─ Done! ✓")
    return self.mc

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

