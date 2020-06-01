
import numpy as np


def cost_SIR(self, p, Data, initial, t, w):
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
  # Build the error dictionary for each element
  erro = {"S": [1.0], "I": [1.0], "R": [1.0]}
  ponder = {"S": 1.0, "I": 1.0, "R": 1.0}
  # Compute the indexes of the used samples
  w_ponder = [1, 1, 1]
  if self.ponder:
    dR = np.diff(Data[2])
    nz_ind = np.where(dR != 0)
    w_ponder[2] = len(Data[1]) / len(Data[2][nz_ind])
  try:
    # Simulate the differential equation system
    result = self.simulate(initial, t, p)
    # Compute the error for all samples
    erro["S"] = (w_ponder[0] * w[0] * ( result[0] - Data[0] )**2)
    erro["I"] = (w_ponder[1] * w[1] * ( result[1] - Data[1] )**2)
    if len(result) == 3:
      if self.ponder:
        erro["R"] = (w_ponder[2] * w[2] * ( result[2][nz_ind] - Data[2][nz_ind] )**2)
      else:
        erro["R"] = (w_ponder[2] * w[2] * ( result[2] - Data[2] )**2)
    # Merging the error
    error = 0.0
    for item in self.focus:
      error += sum(erro[item])
    self.__iter_error = error
  except:
    error = self.__iter_error
  return error

def cost_SEIR(self, pars, dataset, initial, t, w):
  """

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

