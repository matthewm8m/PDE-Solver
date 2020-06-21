from typing import Tuple

import numpy as np


class GridDimension():
    def __init__(self, lower_bound: float, upper_bound: float, cells: int):
        # Store parameters.
        self.lower_bound = lower_bound
        self.upper_bound = upper_bound
        self.cells = cells

    @property
    def length(self):
        return self.upper_bound - self.lower_bound

    @property
    def size(self):
        return self.cells


class FiniteStateGrid():
    def __init__(self, dimensions: Tuple[GridDimension]):
        # Store dimensions in a tuple to avoid mutability.
        self.dimensions = tuple(dimension for dimension in dimensions)

        # Create a grid on the domain of the dimensions.
        dimension_spans = tuple(np.linspace(
            dimension.lower_bound,
            dimension.upper_bound,
            dimension.cells + 1)
            for dimension in dimensions
        )
        self.deltas = tuple(
            (dimension.upper_bound - dimension.lower_bound) / dimension.cells
            for dimension in dimensions
        )
        self.domain = np.stack(
            np.meshgrid(*dimension_spans, indexing='ij'), axis=-1)
        self.states = np.zeros(self.domain.shape[:-1])
