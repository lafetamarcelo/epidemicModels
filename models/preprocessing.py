
import numpy as np
from PyAstronomy import pyasl
from scipy.interpolate import UnivariateSpline
from scipy import integrate


def define_learning_points(self, dataset=None):
  """
    The method responsible for finding the
    points that will be used to in the learning
    algorithm.

    :param dataset dict: The dictionary with the model's components arrays.
    :param time list: The time array respective with dataset measures

    :returns: The respective components with the flags
    :dtype: tuple
  """

  component_names = dataset.keys()

  indexes = []
  for comp in component_names:
    comp_data = dataset[comp]
    indexes.append([True] + (np.diff(comp_data) != 0).tolist())

  return indexes



def basic_reproduction_number(
        using=None,
        z_score=True,
        initial=None,
        time=None,
        window_size=5,
        population=None,
        gamma=1/20,
        sigma=0.05,
        mode="raw"):
    """
    This function is responsible to estimate the time variant basic reproduction
    number (R(t)). Based on active infected data, or the stochastic learning model
    structure.

    :param using object: The object with the infected data (as list) or the stochastic model using epidemicModels library.
    :param mode string: The mode to determine the R(t). If 'raw', it uses the technique defined at [1]. If 'time variant' uses the technique created at [2]. If 'model' it returns one based on the model predictions.

    :returns: A list with the respective values of R(t), for each time instance.
    :dtype: list
    """
    if using is None:
        return "Error, no reference data provided."
    # Define the processing content
    I = using
    # Check if the mode is compatible with the using content
    if ((mode != "model") and (type(using) != np.ndarray)) or ((mode == "model") and (type(using) == np.ndarray)):
        return f"Error, using cannot be {type(using)} when mode is {mode}."
    # Check if it was passed the initial conditions for the model
    if (mode == "model") and ((initial is None) or (time is None)):
        return f"Error, using cannot be {type(using)} when initial is None or time is None."
    if mode == "model":
        sim_res = using.predict(initial, time)
        mode, I = "raw", sim_res[1]
    # Compute the R(t) for each respective mode
    if mode == "raw":
        time = np.linspace(0, len(I)-1, len(I))
        R_t, date = list(), list()
        for k in range(0, len(I) - window_size):
            next_k = k + window_size
            C_now, C_next = I[k], I[next_k]
            at_time = time[k]
            R_t.append(C_next / C_now)
            date.append(at_time)
        R_t, date = np.array(R_t), np.array(date)
    elif mode == "time variant":
        ### Step (1)
        # Create the function to interpolate the I(t)
        time = np.linspace(0, len(I)-1, len(I))
        f_t = UnivariateSpline(time, I)
        # Including some filtering
        ff_t = lambda x: pyasl.smooth(f_t(x), 51, "hamming")
        # Increasing the resolution of time
        time_sim = np.linspace(0, len(I)-1, 10*len(I))
        ### Step (2)
        # Computing the condition values
        r_values = np.diff(ff_t(time_sim)) / ff_t(time_sim[1:])
        # Selecting the value of r from r(t)
        r = abs(1.1 * min(r_values)) # <- Confidence margin of 10%
        ### Step (3)
        # Computing the p(t) values
        f = ff_t(time_sim) # <- Computing f(t)
        df = np.diff(f)    # <- Computing f'(t)
        ddf = np.diff(df)  # <- Computing f''(t)
        # Correcting sizes of the vectors
        df, f = df[1:], f[2:]
        # Computing the p(t) values
        p_t = (ddf*f - df**2) / (f*(df + r*f))
        ### Step (4)
        # Defining the value of P(t)
        P_t = integrate.cumtrapz(p_t, time_sim[2:], initial=0)
        ### Step (5)
        # Defining the condition for \beta(0)
        int_content = np.exp(P_t) * f
        condition = 1 / integrate.cumtrapz(int_content, time_sim[2:], initial=0)
        ### Step (6)
        # Select the estimate of \beta(0)
        population = 2_000_000 if population is None else population
        beta_0 = 1 / population if sum((1/population) < condition) else min(condition)
        # Compute the values of \beta(t)
        beta_t = 1 / ((np.exp(-P_t)/ beta_0) - np.exp(-P_t) * condition)
        ### Step (7)
        # Compute the R(t) from \beta(t)
        if population != None:
            R_t = population * sigma * beta_t / gamma
        else:
            R_t = beta_t / gamma
        date, R_t = time_sim[4:], R_t[2:]
    if z_score:
        R_t = (R_t - np.mean(R_t)) / np.std(R_t)
    return R_t, date
