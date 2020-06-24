
import numpy as np


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
