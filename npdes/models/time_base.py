from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Dict, List

if TYPE_CHECKING:
    import numpy as np


class TimeModelBase(ABC):
    def __init__(self, conditions=):
        # Check if model has analytic solution.
        try:
            self.analytic = True
            self.solution(None, None)
        except NotImplementedError:
            self.analytic = False
        except Exception:
            pass

    @abstractmethod
    def derivative(self, grid, time, derivatives):
        pass

    def solution(self, grid, time):
        raise NotImplementedError()


class TimeModelBase(ABC):
    def __init__(self, dimensions: int, derivatives: Dict[str, object]):
        # Set base attributes.
        self.dimensions = dimensions
        self.derivatives = derivatives

    def _require_derivative(self, name: str, dimensions: List[int] = None):
        """Check that a derivative by a specified name was provided.

        Arguments:
            name {str} -- The name of the required derivative.

        Keyword Arguments:
            dimensions {list[int]} -- A list of dimensions to check for the specified derivative. If none, all dimensions are checked. (default: {None})

        Raises:
            ValueError: Raised if the specified derivative was not provided.
        """

        # Either check for the specified dimensions or all the dimensions.
        dimensions = dimensions or range(self.dimensions)
        names = [f"{name}{d}" for d in dimensions]

        # Raise an appropriate error if the required derivative was not passed in.
        for deriv_name in names:
            if deriv_name not in self.derivatives:
                raise ValueError(
                    f"Required derivative named {deriv_name} was not passed in.")

    @abstractmethod
    def transform(self) -> 'np.ndarray':
        pass

    @abstractmethod
    def solution(self, x: 'np.ndarray', t: float) -> 'np.ndarray':
        pass
