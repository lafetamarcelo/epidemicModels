
import numpy as np

def SIR_regressor(self,dataset,dt=1):
  """
  """
  
  S, I, R = dataset["S"], dataset["I"], dataset["R"]

  s_phi, i_phi, r_phi = [], [], []
  s_out, i_out, r_out = [], [], []

  for s,i,r, s_,i_,r_ in zip(S[:-1], I[:-1], R[:-1], S[1:], I[1:], R[1:]):
    
    s_phi.append([ -s*i/self.N, 0,  s])
    i_phi.append([  s*i/self.N, -i, i])
    r_phi.append([    i,        0,  r])
    
    s_out.append(s_)
    i_out.append(i_)
    r_out.append(r_)

  Phi = np.array(s_phi + i_phi + r_phi)
  Y = np.array(s_out + i_out + r_out)

  if self.verbose:
    print("Sizes of data:", len(S), len(I), len(R))
    print("Sizes of regression:", Phi.shape, Y.shape)

  return Y, Phi