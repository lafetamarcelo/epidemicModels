import numpy as np

def SIR(self, y, time, parameters, *args):
  """
  """
  # Build the model parameters
  if len(parameters) == 3:
    Beta = parameters[0] / (parameters[1] * parameters[2])
    r = 1 / parameters[1]
  else:
    Beta = parameters[0] / parameters[1]
    r = 1 / parameters[1]

  # Compute the Suceptible and the 
  # infected data
  if len(y) == 2:
    S_, I_ = [y[0]], [y[1]]
    for t1, t2 in zip(time[:-1], time[1:]):
      dt = t2 - t1
      S, I = S_[-1], I_[-1]
      Sdot = -Beta * S * I / self.N
      Idot = Beta * S * I / self.N  - r * I
      S_.append(S_[-1] + dt * Sdot)
      I_.append(I_[-1] + dt * Idot)
    S_ = np.array(S_)
    I_ = np.array(I_)
    return S_, I_

  if len(y) == 3:
    # Initialize the vectors as 
    # numpy float 128 bits
    S_ = [ y[0].astype(np.float128) ]
    I_ = [ y[1].astype(np.float128) ]
    R_ = [ y[2].astype(np.float128) ]

    for t1, t2 in zip(time[:-1], time[1:]):
      # Compute the dT 
      dt = t2 - t1
      # Get the values of x(k-1)
      S, I, R = S_[-1], I_[-1], R_[-1]
      # Compute the differential 
      Sdot = -Beta * S * I / self.N
      Idot = Beta * S * I / self.N - r * I 
      Rdot = r * I
      # Compute the x(k) = x(k-1) + dt * x'(k-1)
      S_.append(S_[-1] + dt * Sdot)
      I_.append(I_[-1] + dt * Idot)
      R_.append(R_[-1] + dt * Rdot)
    # Make the responses numpy arrays
    S_ = np.array(S_, dtype=np.float128)
    I_ = np.array(I_, dtype=np.float128)
    R_ = np.array(R_, dtype=np.float128)
    return S_, I_, R_
