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

    # Process Parameters (meter-gram-second)
    assert s.power == None
    assert s.velocity == None
    assert s.lens_radius == None
    assert s.spot_radius == None
    assert s.beam_diameter == None
    assert s.mesh_size == None

    # Process Parameters (centimeter-gram-second)
    assert s.power_cgs == None
    assert s.velocity_cgs == None
    assert s.lens_radius_cgs == None
    assert s.spot_radius_cgs == None
    assert s.beam_diameter_cgs == None
    assert s.mesh_size_cgs == None

    # Prepin
    assert s.prepin == None

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
    assert s.power_cgs == 0
    assert s.velocity_cgs == 0
    assert s.lens_radius_cgs == 0
    assert s.spot_radius_cgs == 0
    assert s.beam_diameter_cgs == 0
    assert s.mesh_size_cgs == 0
    assert s.name == "0_0000_00.0_0.0E+1_0.0E+1"

    s.set_process_parameters(100, 1)
    assert s.power == 100
    assert s.velocity == 1
    assert s.lens_radius == 5E-5
    assert s.spot_radius == 5E-5
    assert s.beam_diameter == 1E-4
    assert s.mesh_size == 2E-5
    assert s.power_cgs == 1E9
    assert s.velocity_cgs == 100
    assert s.lens_radius_cgs == 0.005 
    assert s.spot_radius_cgs == 0.005 
    assert s.beam_diameter_cgs == 0.01
    assert s.mesh_size_cgs == 0.002
    assert s.name == "0_0100_01.0_1.0E-4_2.0E-5"

def test_generate_name_v0(s):
    """
    Ensures the the generated names match what is expected.
    """
    assert s.generate_name_v0(0, 0, 0, 0) == "0_0000_00.0_0.0E+1_0.0E+1"
    assert s.generate_name_v0(100, 1) == "0_0100_01.0_1.0E-4_2.0E-5"
    assert s.generate_name_v0(100, 10) == "0_0100_10.0_1.0E-4_2.0E-5"
    assert s.generate_name_v0(1000, 10) == "0_1000_10.0_1.0E-4_2.0E-5"

