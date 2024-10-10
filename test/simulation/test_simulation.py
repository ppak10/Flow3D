import math
import pytest

from flow3d import Simulation

VERSION = 0

def test_init_default():
    """
    Tests initialization of Simulation class
    """

    s = Simulation()

    # Check default variables assigned to `self`. 
    name = s.generate_name_v0(
        power = s.default_parameters["power"],
        velocity = s.default_parameters["velocity"],
        beam_diameter = s.default_parameters["beam_diameter"],
        mesh_size = s.default_parameters["mesh_size"],
    )

    # Check explictily defined arguments.
    assert s.version == VERSION
    assert s.name == name
    assert s.filename == "simulation"
    assert s.use_template == True
    assert s.verbose == False

    # Check simulation parameters (meter-gram-second) are assigned to `self`.
    for key, value in s.default_parameters.items():
        assert getattr(s, key) == value

    # TODO: Add checks for initial prepin.

def test_init_non_default():
    """
    Tests simple non-default initialization arguments.
    """

    # TODO: Add checks for version
    # Probably requires a list of valid versions.

    # Check `name` initialization
    s = Simulation(name = "test_init")
    assert s.name == "test_init"

    # Check `filename` initialization
    s = Simulation(filename = "test_init")
    assert s.filename == "test_init"

    # TODO: Add check for `use_template` initialization
    # Implment it when `use_template == False` behavior is implemented

    # Check `verbose` initialization
    s = Simulation(verbose = True)
    assert s.verbose == True 


# def test_set_process_parameters(s):
#     """
#     Tests the update of process parameters
#     """

#     s = Simulation(s)

#     # Set all parameter values to zero and check name.
#     zero_parameters = dict()
#     for key in default_parameters.keys():
#         zero_parameters[key] = 0
    
#     s.set_process_parameters(**zero_parameters)

#     for key in default_parameters.keys():
#         assert getattr(s, key) == 0

#     assert s.name == "0_0000_00.0_0.0E+1_0.0E+1"

#     # Update only the power and velocity parameters and check name.
#     s.set_process_parameters(power = 100, velocity = 1)
#     assert s.power == 100
#     assert s.velocity == 1

#     for key in default_parameters.keys():
#         if key == "power":
#             assert s.power == 100
#         elif key == "velocity":
#             assert s.velocity == 1
#         else:
#             assert getattr(s, key) == 0

#     assert s.name == "0_0100_01.0_0.0E+1_0.0E+1"

#     # Set all parameters back to default and check name.
#     s.set_process_parameters(**default_parameters)

#     for key in default_parameters.keys():
#         assert getattr(s, key) == default_parameters[key]

#     assert s.name == "0_0100_01.0_1.0E-4_2.0E-5"

def test_cgs():
    """
    Test centimeter-gram-second conversion of meter-gram-second values.
    """
    s = Simulation()
    assert s.cgs("power") == 100 * 1E7
    assert s.cgs("velocity") == 1 * 1E2

    assert s.cgs("lens_radius") == 5E-3
    assert s.cgs("spot_radius") == 5E-3
    assert s.cgs("gauss_beam") == pytest.approx(5E-3 / math.sqrt(2))
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

def test_generate_name_v0():
    """
    Ensures the the generated names match what is expected.
    """
    s = Simulation()
    assert s.generate_name_v0(0, 0, 0, 0) == "0_0000_00.0_0.0E+1_0.0E+1"
    assert s.generate_name_v0(100, 1) == "0_0100_01.0_1.0E-4_2.0E-5"
    assert s.generate_name_v0(100, 10) == "0_0100_10.0_1.0E-4_2.0E-5"
    assert s.generate_name_v0(1000, 10) == "0_1000_10.0_1.0E-4_2.0E-5"

def test_lt():
    s_100 = Simulation(power=100)
    s_200 = Simulation(power=200)
    s_300 = Simulation(power=300)
    simulations_power = [s_300, s_200, s_100]
    assert sorted(simulations_power) == [s_100, s_200, s_300]

    s_04 = Simulation(velocity=0.4)
    s_06 = Simulation(velocity=0.6)
    s_08 = Simulation(velocity=0.8)
    simulations_velocity = [s_08, s_06,  s_04]
    assert sorted(simulations_velocity) == [s_04,  s_06,  s_08]
