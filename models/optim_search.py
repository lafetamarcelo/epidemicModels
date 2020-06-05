
from . import cost_functions as cf
from . import differential_models as dm

from scipy.optimize import differential_evolution, dual_annealing
from scipy.optimize import shgo, leastsq, NonlinearConstraint



class epidemic:


  def __init__(self,
    focus=["I", "R"],
    population=200000,
    verbose=False,
    algorithm="differential_evolution"):

    self.verbose = verbose
    self.N = population
    self.focus = focus
    self.__search_alg = algorithm
    
    self.__class__.simulate = dm.discSIR
    self.__class__.cost_function = cf.cost_discSIR


  def fit(self, 
      dataset, 
      time, 
      constrained=False,
      ro_bounderies=[0.5, 2],
      pop_sens=[1e-5,1e-1],
      beta_sens=[1000,10],
      r_sens=[1000,10]):

    # Compute the parameters boundaries
    x = [1/self.N, 1/21] # Approx values of beta and r
    lower = [x[0]/beta_sens[0], x[1]/r_sens[0]]
    upper = [beta_sens[1]*x[0], r_sens[1]*x[1]]
    # Checking the constraints
    constraints = ()
    if constrained:
      nlc = NonlinearConstraint(self.__ro_constraint_builder, ro_bounderies[0], ro_bounderies[1])
      constraints = (nlc)

    if self.verbose:
      print("\t ├─ beta ─  ", x[0], "  r ─  ", x[1])
      print("\t ├─ beta bound ─  ", lower[0], " ─ ", upper[0])
      print("\t ├─ r bound ─  ", lower[1], " ─ ", upper[1])
      if self.__exposed_flag:
        print("\t ├─ sigma bound ─  ", lower[2], " ─ ", upper[2])
      print("\t ├─ Running on ─ ", self.__search_alg, "SciPy Search Algorithm")
    # Minimize the cost function
    summary = differential_evolution(
      self.cost_wrapper, 
      list(zip(lower, upper)),
      maxiter=10000,
      popsize=35,
      mutation=(0.5, 1.2),
      strategy="best2exp",
      tol=0.0000001,
      args=(dataset, time),
      constraints=constraints,
      updating='deferred',
      workers=-1,
      # disp=True
    )

    # summary = dual_annealing(
    #   self.cost_wrapper, 
    #   list(zip(lower, upper)),
    #   maxiter=10000,
    #   args=(dataset, time),
    #   # updating='deferred',
    #   # workers=-1,
    #   disp=True
    # )

    self.parameters = summary.x
  
  def predict(self, initial, time):

    return self.simulate(initial, time, self.parameters)
    

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

  def __ro_constraint_builder(self, pars):
    """
      The function to compute the non linear contraint of the Ro parameter.
      
      :param list pars: list of parameters, beta, r and pop.
    
      :return: the Ro value.
      :rtype: float
    """
    return pars[0] / pars[1]



