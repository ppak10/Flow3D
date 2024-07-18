import pytest
import os
import shutil
import warnings

from flow3d import Prepin

template_ids_UNS = []

test_prepin_dir = "test_prepin_dir"

@pytest.fixture(autouse=True, scope="module")
def setup_teardown():
    # Setup

    yield

    # Teardown
    shutil.rmtree(test_prepin_dir)

@pytest.fixture(scope="module")
def p():
    return Prepin(prepin_dir=test_prepin_dir)

def test_init(p):
    """
    Tests initialization of variables for Prepin class
    """

    assert p.keep_in_memory == False
    assert p.verbose == True
    assert p.prepin_dir == test_prepin_dir
    assert p.prepin_dir_path == test_prepin_dir

def test_build_from_template_invalid_template_id_and_template_id_type(p):
    """
    Attempts to build prepin file from non-existing material template or type.
    """

    with pytest.raises(Exception):
        # Invalid `template_id_type` value.
        p.build_from_template("", 0, 0, template_id_type="")

        # Invalid `template_id` value.
        p.build_from_template("", 0, 0, template_id_type="UNS")

def test_build_from_template_prepin_dir(p):
    """
    Creates folder for prepin file using valid template and expects warning
    when folder already exists.
    """
    # Ensure no folders are created if `keep_in_memory` is set to `True`.
    p.build_from_template("R56400", 0, 0, template_id_type="UNS", keep_in_memory = True)
    assert os.path.isdir(test_prepin_dir) == False

    # Sets class variable without method argument to override `keep_in_memory`.
    p.keep_in_memory = True
    p.build_from_template("R56400", 0, 0, template_id_type="UNS")
    assert os.path.isdir(test_prepin_dir) == False

    # Checks that behavior works with both argument and class variable.
    p.build_from_template("R56400", 0, 0, template_id_type="UNS", keep_in_memory = True)
    assert os.path.isdir(test_prepin_dir) == False

    # Resets back to default state.
    p.keep_in_memory = False


    # Test Ti-6Al-4V template.
    p.build_from_template("R56400", 0, 0, template_id_type="UNS")

    # Check that `prepin_dir` is created.
    assert os.path.isdir(test_prepin_dir) == True

    # Expect a warning if `prepin_dir` is already created.
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        p.build_from_template("R56400", 0, 0, template_id_type="UNS")

        assert len(w) == 1
        assert issubclass(w[-1].category, UserWarning)

def test_build_from_template_argument_types(p):
    """
    Checks that arugment matches `int` or `list` type and throws exception if
    not either.
    """

    # Invalid Inputs
    with pytest.raises(Exception):
        for power in ["100 W", ["100 W", "200 W"]]:
            p.build_from_template("R56400", power, 0, template_id_type="UNS", keep_in_memory = True)
        for velocity in ["1 m/s", ["1 m/s", "2 m/s"]]:
            p.build_from_template("R56400", 0, velocity, template_id_type="UNS", keep_in_memory = True)

    # Valid Inputs
    for power in [100, 100.0, [100, 200], [100.0, 200.0]]:
        simulations = p.build_from_template("R56400", power, 0, template_id_type="UNS", keep_in_memory = True)
        if isinstance(power, list):
            assert len(simulations) == len(power)
        else:
            assert len(simulations) == 1

    for velocity in [1, 1.0, [1, 2], [1.0, 2.0]]:
        simulations = p.build_from_template("R56400", 0, velocity, template_id_type="UNS", keep_in_memory = True)
        if isinstance(velocity, list):
            assert len(simulations) == len(velocity)
        else:
            assert len(simulations) == 1
