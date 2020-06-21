from typing import TYPE_CHECKING, Dict, Union

from npdes.models import BaseModel

import numpy as np


class AdvectionDiffusionModel(BaseModel):
    def __init__(self, dimensions: int, derivatives=Dict[str, object],
                 velocity: Union[float, 'np.ndarray'] = None,
                 diffusivity: Union[float, 'np.ndarray'] = None):
        # Register base attributes.
        super().__init__(dimensions, derivatives)

        # Check that correct derivatives were passed in.
        # If velocity or diffusivity is zero, we can ignore
        # the corresponding derivatives.
        if not np.all(velocity == 0):
            self._require_derivative('x')

        if not np.all(diffusivity == 0):
            self._require_derivative('xx')

    def transform(self) -> 'np.ndarray':
        pass

    def solution(self, x: 'np.ndarray', t: float) -> 'np.ndarray':
        pass
