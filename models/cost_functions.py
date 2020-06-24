
import numpy as np
from PyAstronomy import pyasl

import sys
import os

def PrintException(e):
  exc_type, exc_obj, exc_tb = sys.exc_info()
  fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
  print(e, ' - line:', exc_tb.tb_lineno)


def cost_NSIR(self, pars, dataset, initial, t, w):
  """
  """
  model_pars = [p for p in pars]
  model_init = [item for item in initial]

  erro = dict(N=1.0, S=1.0, I=1.0, R=1.0)
  S, I, R = dataset[0], dataset[1], dataset[2]

  try:
    # Simulate the differential equation system
    result = self.simulate(model_init, t, model_pars)
    # Compute the error for all samples
    erro["S"] = w[0] * ( result[0].astype(np.float128) - S.astype(np.float128) )**2
    erro["I"] = w[1] * ( result[2].astype(np.float128) - I.astype(np.float128) )**2
    erro["R"] = w[2] * ( result[3].astype(np.float128) - R.astype(np.float128) )**2
    # Merging the error
    erro_acc = 0.0
    for item in self.focus:
      erro_acc += np.sqrt(np.mean(erro[item]))
    self._iter_error.append(erro_acc)
  except Exception as e:
    print("Overflow exception -> ", e)
    erro_acc = self._iter_error[-1]
  return erro_acc




def cost_SIR(self, pars, dataset, initial, t, w):
  """
    The function to compute the error to guide the learning
    algorithm. It computes the quadratic error.

    :param tuple pars: Tuple with Beta and r parameters, respectivelly.
    :param array dataset: The suceptible data values.
    :param array initial: The initial values of suceptible and infected, respectivelly.
    :param array t: The time respective to each sample.
    :param array w: The weight respective to the suceptible and infected errors.

    :return: The sum of the quadratic error, between simulated and real data.
    :rtype: float
  """
  model_pars = list(pars)
  model_init = list(initial)
  datatest = dataset
  for i, data in enumerate(datatest):
    if type(data) == type(list()):
      datatest[i] = np.array(data)
  error = 0.0

  if self._search_pop:
    datatest[0] = pars[-1]*self.N*np.ones(datatest[0].shape)
    for data in datatest[1:]:
      datatest[0] += -data
    model_init[0] *= pars[-1]
  try:
    # Simulate the differential equation system
    result = self.simulate(model_init, t, model_pars)
    # Compute the error for all samples
    for d, r, p, i in zip(datatest, result, w, self._consider_points):
      error_agg = (np.sqrt(p) * r[i].astype(np.float128) - np.sqrt(p) * d[i].astype(np.float128))**2
      error += np.sqrt(np.mean(error_agg))
    self._iter_error.append(error)
  except Exception as e:
    print("Overflow exception -> {}".format(e))
    error = self._iter_error[-1]
  return error


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
  except Exception as e:
    print("Overflow exception -> ", e)
    erro_acc = self._iter_error[-1]
  return erro_acc


def cost_SIRD(self, pars, dataset, initial, t, w):
  """
    The function to compute the error to guide the learning
    algorithm. It computes the quadratic error.

    :param tuple pars: Tuple with Beta and r parameters, and other parameters, if exists, respectivelly.
    :param list dataset: The list with the data components of the model.
    :param list initial: The initial values of suceptible and infected, respectivelly.
    :param array t: The time respective to each sample.
    :param array w: The weight respective to the suceptible and infected errors.

    :return: The sum of the quadratic error, between simulated and real data.
    :rtype: float
  """
  model_pars = list(pars)
  model_init = list(initial)
  datatest = dataset
  for i, data in enumerate(datatest):
    if type(data) == type(list()):
      datatest[i] = np.array(data)
  error = 0.0

  datatest = dataset

  if self._search_pop:
    datatest[0] = pars[-1]*self.N*np.ones(datatest[0].shape)
    for data in datatest[1:]:
      datatest[0] += -data
    model_init[0] *= pars[-1]
  try:
    # Simulate the differential equation system
    result = self.simulate(model_init, t, model_pars)
    # Compute the error for all samples
    for d, r, p, i in zip(datatest, result, w, self._consider_points):
      error_agg = (np.sqrt(p) * r[i].astype(np.float128) - np.sqrt(p) * d[i].astype(np.float128))**2
      error += np.sqrt(np.mean(error_agg))
    self._iter_error.append(error)
  except Exception as e:
    print("Overflow exception -> ", e)
    error = self._iter_error[-1]
  return error
