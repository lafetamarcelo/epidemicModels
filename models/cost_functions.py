
import numpy as np
from PyAstronomy import pyasl


def cost_SIR(self, pars, dataset, initial, t, w):
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
  model_pars = [p for p in pars]
  model_init = [item for item in initial]
  
  S, I, R = dataset[0], dataset[1], dataset[2]

  erro = dict(S=1.0, I=1.0, R=1.0)

  if self._search_pop:
    model_pars = pars[:-1]
    S = pars[-1] * self.N - R - I
    model_init[0] *= pars[-1]
    
  try:
    # Simulate the differential equation system
    result = self.simulate(model_init, t, model_pars)
    # Compute the error for all samples
    erro["S"] = w[0] * ( result[0] - S )**2
    erro["I"] = w[1] * ( result[1] - I )**2
    erro["R"] = w[2] * ( result[2] - R )**2
    # Merging the error
    erro_acc = 0.0
    for item in self.focus:
      erro_acc += np.sqrt(np.mean(erro[item]))
    self._iter_error.append(erro_acc)
  except:
    print("Except da merda")
    erro_acc = self._iter_error[-1]
  return erro_acc


def cost_dSIR(self, pars, dataset, initial, t, w):
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
  model_pars = [p for p in pars]
  model_init = [item for item in initial]
  
  S = pyasl.smooth(dataset[0], 13, "hamming")
  I = pyasl.smooth(dataset[1], 13, "hamming")
  R = pyasl.smooth(dataset[2], 13, "hamming")

  erro = dict(S=1.0, I=1.0, R=1.0)
  
  try:
    # Simulate the differential equation system
    result = [[],[],[]]
    for s, i, r in zip(S,I,R):
      rsim = self.differential_model((s,i,r), t, model_pars[0], model_pars[1])
      for k in range(3):
        result[k].append(rsim[k])
    for k in range(3): 
      result[k] = np.array(result[k])
    # Compute the error for all samples
    #erro["S"] = w[0] * ( result[0] - np.gradient(S) )**2
    erro["I"] = w[1] * ( result[1] - np.gradient(I) )**2
    erro["R"] = w[2] * ( result[2] - np.gradient(R) )**2
    # Merging the error
    erro_acc = 0.0
    for item in self.focus:
      erro_acc += np.sqrt(np.mean(erro[item]))
    self._iter_error.append(erro_acc)
  except:
    print("Except da merda")
    erro_acc = self._iter_error[-1]
  return erro_acc


def cost_SEIR(self, pars, dataset, initial, t, w):
  """
    The function to compute the error to guide the learning
    algorithm. It computes the quadratic error.

    :param tuple pars: Tuple with Beta and r parameters, respectivelly.
    :param list dataset: The dataset with the respective S, I and R arrays.
    :param array initial: The initial values of suceptible and infected, respectivelly.
    :param array t: The time respective to each sample.
    :param array w: The weight respective to the suceptible and infected errors.

    :return: The sum of the quadratic error, between simulated and real data.
    :rtype: float
  """
  model_pars = [p for p in pars]
  model_init = [item for item in initial]
  
  S, I, R = dataset[0], dataset[1], dataset[2]

  erro = dict(S=1.0, E=1.0, I=1.0, R=1.0)
  if self._search_pop:
    model_init[0] *= pars[-1]         
    model_pars = pars[:-1]
    S = pars[-1] * self.N - R - I
  try:
    # Simulate the differential equation system
    result = self.simulate(model_init, t, model_pars)
    # Compute the error for all samples
    erro["S"] = w[0] * ( result[0] + result[1] - S )**2
    erro["I"] = w[1] * ( result[2] - I )**2
    erro["R"] = w[2] * ( result[3] - R )**2
    # Merging the error
    erro_acc = 0.0
    for item in self.focus:
      erro_acc += np.sqrt(np.mean(erro[item]))
    self._iter_error.append(erro_acc)
  except:
    print("Except da merda")
    erro_acc = self._iter_error[-1]
  return erro_acc
