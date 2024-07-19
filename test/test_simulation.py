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
    assert s.mesh_x_start == None
    assert s.mesh_x_end == None
    assert s.mesh_y_start == None
    assert s.mesh_y_end == None
    assert s.mesh_z_start == None
    assert s.mesh_z_end == None
    assert s.fluid_region_x_start == None
    assert s.fluid_region_x_end == None
    assert s.fluid_region_y_start == None
    assert s.fluid_region_y_end == None
    assert s.fluid_region_z_start == None
    assert s.fluid_region_z_end == None

    # Prepin
    assert s.prepin == None

def test_set_process_parameters(s):
    """
    Tests the update of process parameters
    """
    
    s.set_process_parameters(0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0)
    assert s.power == 0
    assert s.velocity == 0
    assert s.lens_radius == 0
    assert s.spot_radius == 0
    assert s.beam_diameter == 0
    assert s.mesh_size == 0
    assert s.mesh_x_start == 0 
    assert s.mesh_x_end == 0
    assert s.mesh_y_start == 0
    assert s.mesh_y_end == 0
    assert s.mesh_z_start == 0
    assert s.mesh_z_end == 0
    assert s.fluid_region_x_start == 0
    assert s.fluid_region_x_end == 0
    assert s.fluid_region_y_start == 0
    assert s.fluid_region_y_end == 0
    assert s.fluid_region_z_start == 0
    assert s.fluid_region_z_end == 0
    assert s.name == "0_0000_00.0_0.0E+1_0.0E+1"

    s.set_process_parameters(100, 1)
    assert s.power == 100
    assert s.velocity == 1
    assert s.lens_radius == 5E-5
    assert s.spot_radius == 5E-5
    assert s.beam_diameter == 1E-4
    assert s.mesh_size == 2E-5
    assert s.mesh_x_start == 5E-4
    assert s.mesh_x_end == 3E-3
    assert s.mesh_y_start == 0
    assert s.mesh_y_end == 6E-4
    assert s.mesh_z_start == 0 
    assert s.mesh_z_end == 6E-4
    assert s.fluid_region_x_start == 0
    assert s.fluid_region_x_end == 2.8E-3
    assert s.fluid_region_y_start == 0
    assert s.fluid_region_y_end == 6E-4
    assert s.fluid_region_z_start == 0
    assert s.fluid_region_z_end == 4E-4
    assert s.name == "0_0100_01.0_1.0E-4_2.0E-5"

def test_cgs(s):
    """
    Test centimeter-gram-second conversion of meter-gram-second values.
    """
    assert s.cgs("power") == 100 * 1E7
    assert s.cgs("velocity") == 1 * 1E2

    assert s.cgs("lens_radius") == 5E-3
    assert s.cgs("spot_radius") == 5E-3
    assert s.cgs("beam_diameter") == 1E-2
    assert s.cgs("mesh_size") == 2E-3
    assert s.cgs("mesh_x_start") == 5E-2
    assert s.cgs("mesh_x_end") == 3E-1
    assert s.cgs("mesh_y_start") == 0
    assert s.cgs("mesh_y_end") == 6E-2
    assert s.cgs("mesh_z_start") == 0 
    assert s.cgs("mesh_z_end") == 6E-2
    assert s.cgs("fluid_region_x_start") == 0
    assert s.cgs("fluid_region_x_end") == 2.8E-1
    assert s.cgs("fluid_region_y_start") == 0
    assert s.cgs("fluid_region_y_end") == 6E-2
    assert s.cgs("fluid_region_z_start") == 0
    assert s.cgs("fluid_region_z_end") == 4E-2

def test_generate_name_v0(s):
    """
    Ensures the the generated names match what is expected.
    """
    assert s.generate_name_v0(0, 0, 0, 0) == "0_0000_00.0_0.0E+1_0.0E+1"
    assert s.generate_name_v0(100, 1) == "0_0100_01.0_1.0E-4_2.0E-5"
    assert s.generate_name_v0(100, 10) == "0_0100_10.0_1.0E-4_2.0E-5"
    assert s.generate_name_v0(1000, 10) == "0_1000_10.0_1.0E-4_2.0E-5"

