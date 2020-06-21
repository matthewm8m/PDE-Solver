import pytest


def test_version():
    import npdes

    assert npdes.__version__ == '1.1.0'


def test_imports():
    # Package import.
    import npdes

    # Models imports.
    from npdes.models import BaseModel
    from npdes.models import AdvectionDiffusionModel
