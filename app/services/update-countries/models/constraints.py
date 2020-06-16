


def Ro_decimal_constr(x_par):
  """
    The function to compute the non linear contraint of the Ro parameter.
    
    :param list x_par: list of parameters, beta, r and pop.
  
    :return: the Ro value.
    :rtype: float
  """
  if len(x_par) == 3:
    return x_par[0] * x_par[2] / x_par[1]
  else:
    return x_par[0] / x_par[1]