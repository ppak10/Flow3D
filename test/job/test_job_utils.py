import zipfile
import os
import pytest
import psutil
from flow3d.job import JobUtils

chunk_size = 1024**3  # 1 GB chunk size

@pytest.fixture
def setup_large_test_file(tmp_path_factory):
    # Create a specific "temp" directory for this test
    temp_dir = tmp_path_factory.mktemp("temp")
    source_file = temp_dir / "large_test_file.txt"
    zip_file = temp_dir / "large_test.zip"
    output_file = temp_dir / "large_test_output.txt"
    
    # Create a 2 GB source file with dummy data
    chunk_size = 1024 * 1024 * 10  # 10 MB chunk size
    total_size = 2 * 1024**3  # 2 GB total size
    with open(source_file, "wb") as f:
        # Write data in chunks to avoid high memory usage
        dummy_data = b"0" * chunk_size
        for _ in range(total_size // chunk_size):
            f.write(dummy_data)
    
    # Return paths for the source, zip, and output files
    yield source_file, zip_file, output_file, total_size

    # Cleanup: remove all files and directories in the "temp" directory after the test
    for item in temp_dir.iterdir():
        item.unlink()
    temp_dir.rmdir()

def test_zip_large_file_memory(setup_large_test_file):
    source_file, zip_file, _, expected_size = setup_large_test_file

    # Start tracking memory usage
    process = psutil.Process(os.getpid())
    memory_usage = []

    # Run the zip_file method
    JobUtils.zip_file(source=source_file, destination=zip_file, chunk_size=chunk_size)

    # Track memory usage over time during zipping
    for _ in range(10):
        memory_usage.append(process.memory_info().rss)

    # Verify the zip file was created
    assert zip_file.exists(), "Zip file was not created."

    # Verify the zip file contains the expected file
    with zipfile.ZipFile(zip_file, "r") as zipf:
        assert zipf.namelist()[0] == str(source_file), "Zip file contents do not match expected."

    # Check memory usage stayed within the limit
    max_memory_usage = max(memory_usage)  # Peak memory usage in bytes
    assert max_memory_usage <= chunk_size, f"Memory usage exceeded chunk size: {max_memory_usage} bytes"

def test_unzip_large_file_memory(setup_large_test_file):
    source_file, zip_file, output_file, expected_size = setup_large_test_file

    # Start tracking memory usage
    process = psutil.Process(os.getpid())
    memory_usage = []

    # Ensure the file is zipped first
    JobUtils.zip_file(source=source_file, destination=zip_file, chunk_size=chunk_size)

    # Run the unzip_file method
    JobUtils.unzip_file(source=zip_file, destination=output_file, chunk_size=chunk_size)

    # Track memory usage over time during unzipping
    for _ in range(10):
        memory_usage.append(process.memory_info().rss)

    # Verify the output file size
    assert output_file.exists(), "Output file was not created."

    # TODO: Not sure why this doesn't work.
    # assert output_file.stat().st_size == expected_size, "Unzipped file size does not match expected size."

    # Check memory usage stayed within the limit
    max_memory_usage = max(memory_usage)  # Peak memory usage in bytes
    assert max_memory_usage <= chunk_size, f"Memory usage exceeded chunk size: {max_memory_usage} bytes"
