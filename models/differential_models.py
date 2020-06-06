import numpy as np


def discSIR(self, initial, time, pars, dt=1.0, *args):
  """
  """

  if (initial[0] == 0) or (initial[1] == 0):
    print("The provided data is not exciting enough:", initial)

  beta, r = pars[0], pars[1]
  S, I, R = [initial[0]], [initial[1]], [initial[2]]

  for k, t in enumerate(time[1:]):
    S_ = -dt*(beta*S[-1]*I[-1])          + S[-1]
    I_ = dt*(beta*S[-1]*I[-1] + r*I[-1]) + I[-1]
    R_ = dt*(r*I[-1])                           + R[-1]
    S.append(S_)
    I.append(I_)
    R.append(R_)
  
  result = dict()
  result["S"] = np.array(S)
  result["I"] = np.array(I)
  result["R"] = np.array(R)

  return result

  


def SIR(self, y, t, Beta, r, *args):
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
    Sdot = -Beta * S * I / self.N
    Idot = Beta * S * I / self.N  - r * I
    return Sdot, Idot

  if len(y) == 3:
    S, I, R = y
    Sdot = -Beta * S * I / self.N
    Idot = Beta * S * I / self.N - r * I 
    Rdot = r * I
    return Sdot, Idot, Rdot


def SEIR(self, y, t, Beta, r, sigma):
  """
    The function that computes the diferential set of 
    equations of the SEIR Epidemic Model.
    
    :param tuple y: Tuple with the suceptible and infected data.
    :param array t: The time respective to each y set of samples.
    :param float Beta: The Beta parameter.
    :param float r: The r parameter.
    :param float sigma: The sigma parameter.
    
    :return: The derivative of the suceptible and infected data.
    :rtype: tuple
  """

  S, E, I, R = y
  Sdot = -Beta * S * I / self.N
  Edot = Beta * S * I / self.N - sigma * E
  Idot = sigma * E  - r * I
  Rdot = r * I
  return Sdot, Edot, Idot, Rdot



def SIRD(self, y, t, Beta, r, mi):
  """
  The function that computes the diferential set of 
  equations of the SIRD Epidemic Model.

  :param tuple y: Tuple with the suceptible and infected data.
  :param array t: The time respective to each y set of samples.
  :param float Beta: The Beta parameter.
  :param float r: The r parameter.
  :param float mi: The mi parameter.

  :return: The derivative of the suceptible and infected data.
  :rtype: tuple
  """
  S, I, R = y
  Sdot = -Beta * I * S
  Idot = Beta * I * S - r * I - mi * I
  Rdot = r * I
  Ddot = mi* I
  return Sdot, Idot, Rdot, Ddot