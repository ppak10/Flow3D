import pytest
import os
import re
import shutil
import warnings

from flow3d import Flow3D 

test_output_dir = "test_output_dir"
test_job_name = "test_job_name"
timestamp_format = r'^\d{8}_\d{6}$'

prepin_dir = "prepin"

@pytest.fixture(autouse=True, scope="module")
def setup_teardown():
    # Setup

    yield

    # Teardown
    shutil.rmtree(test_output_dir)

@pytest.fixture(scope="module")
def f3d():
    return Flow3D(output_dir=test_output_dir)

def test_init(f3d):
    """
    Tests initializtion of variables in main class export.
    """

    # Tests initialization without arguments except `output_dir`.
    assert f3d.num_proc == 1
    assert f3d.keep_in_memory == False
    assert f3d.output_dir == test_output_dir
    assert f3d.job_name == None
    assert f3d.job_dir_path == None 

    # Inherited prepin init values.
    assert f3d.verbose == False

    assert f3d.prepin_dir_path == prepin_dir
    assert f3d.prepin_dir == prepin_dir

    # Checks that `output_dir` is created.
    assert os.path.isdir(test_output_dir)

def test_build_prepin_without_creating_job_first(f3d):
    """
    Test building of prepin files without creating job first.
    """

    with pytest.raises(Exception):
        # Expects Ti-6Al-4V to raise job not created exception.
        f3d.prepin_build_from_template("R56400", 0, 0, template_id_type="UNS")

def test_create_job(f3d):
    """
    Tests creation of job folder and checks it existence.
    """

    # Creates job directory with provided arugment and verifies existence
    job_name = f3d.create_job(test_job_name)
    job_dir_path = os.path.join(f3d.output_dir, job_name)
    assert os.path.isdir(job_dir_path) == True
    assert job_name == test_job_name

    # Create job direction without argument and fallback to timestamp.
    job_name_no_arg = f3d.create_job()
    job_dir_path_no_arg = os.path.join(f3d.output_dir, job_name_no_arg)

    # Check that job folder with name of timestamp is created.
    assert os.path.isdir(job_dir_path_no_arg)

    # Assert that the timestamp matches regex pattern.
    assert re.match(timestamp_format, job_name_no_arg)

    # Expects warning if creating a job with the name of existing job.
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        f3d.create_job(test_job_name)

        assert len(w) == 1
        assert issubclass(w[-1].category, UserWarning)

def test_build_prepin(f3d):
    """
    Test building of prepin files.
    """

    # Test Ti-6Al-4V template.
    f3d.prepin_build_from_template("R56400", 0, 0, template_id_type="UNS")

    # Check that prepin folder within job directory is created.
    prepin_dir_path = os.path.join(f3d.job_dir_path, prepin_dir)
    assert os.path.isdir(prepin_dir_path)

    # Expects that `prepin_dir` remains the same
    assert f3d.prepin_dir == prepin_dir

    # Expects that `prepin_dir_path` is within job folder.
    assert f3d.prepin_dir_path == prepin_dir_path

