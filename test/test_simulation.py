import pytest

from flow3d import Simulation

version = 0

@pytest.fixture(scope="module")
def s():
    return Simulation()

def test_init(s):
    """
    Tests initialization of Simulation class
    """

    assert s.version == version
    assert s.name == None

    # Process Parameters
    assert s.power == None
    assert s.velocity == None
    assert s.lens_radius == None
    assert s.spot_radius == None
    assert s.beam_diameter == None
    assert s.mesh_size == None

def test_set_process_parameters(s):
    """
    Tests the update of process parameters
    """
    
    s.set_process_parameters(0, 0, 0, 0, 0)
    assert s.power == 0
    assert s.velocity == 0
    assert s.lens_radius == 0
    assert s.spot_radius == 0
    assert s.beam_diameter == 0
    assert s.mesh_size == 0
    assert s.name == "0_0000_00.0_0.0E-5_0.0E-5"

    s.set_process_parameters(100, 1)
    assert s.power == 100
    assert s.velocity == 1
    assert s.lens_radius == 0.005
    assert s.spot_radius == 0.005
    assert s.beam_diameter == 0.010
    assert s.mesh_size == 0.002
    assert s.name == "0_0100_01.0_10.0E-5_2.0E-5"

def test_generate_name_v0(s):
    """
    Ensures the the generated names match what is expected.
    """
    assert s.generate_name_v0(0, 0, 0, 0) == "0_0000_00.0_0.0E-5_0.0E-5"



