import os
import zipfile

from tqdm import tqdm

class SimulationUtilsCompression():
    """
    Compression methods used within simulation class.
    """

    @staticmethod
    def unzip_folder(source, destination):
        """
        Method of unzipping folder if it does not already exist.

        @param source: Path to the zip file, e.g., "flslnk_npz.zip"
        @param destination: Path to the output folder, e.g., "flslnk_npz"
        """
        if not os.path.exists(destination):
            if os.path.exists(source):
                os.makedirs(destination)
                with zipfile.ZipFile(source, "r") as zip_ref:
                    zip_ref.extractall(destination)
            else:
                raise FileNotFoundError(f"`{source}` source file not found")

    @staticmethod
    def unzip_file(source, destination, chunk_size=1024**3):
        """
        Method for unzipping multiple files with the same name into one combined file.

        @param source: Path to the zip file, e.g., "flslnk.zip"
        @param destination: Path to the output file, e.g., "flsgrf.simulation"
        @param chunk_size: Size of each chunk to read (defaults to 10 MB)
        """
        print(f"Unzipping `{source}` to `{destination}`...")

        with zipfile.ZipFile(source) as zip_ref:
            file_names = zip_ref.namelist()

            # Filter to include only files named "flsgrf.simulation"
            # matching_files = [name for name in file_names if name == "flsgrf.simulation"]

            # Open the destination file once and append each matching file's contents to it
            with open(destination, 'wb') as dest_file:
                for file_name in tqdm(file_names):
                    # Get the uncompressed file size for progress tracking
                    uncompressed_size = zip_ref.getinfo(file_name).file_size
                    print(f"Extracting `{file_name}` ({uncompressed_size} bytes)")

                    # Open each file inside the zip archive
                    with zip_ref.open(file_name) as source_file:
                        # Initialize tqdm progress bar
                        # with tqdm(total=uncompressed_size, unit="B", unit_scale=True, desc=f"Extracting {file_name}", position=0, leave=True) as pbar:
                        while True:
                            # Read a chunk of data from the source file
                            chunk = source_file.read(chunk_size)
                            if not chunk:
                                break  # Stop when no more data is read

                            # Append the chunk to the destination file
                            dest_file.write(chunk)

                            # Update the progress bar
                            # pbar.update(len(chunk))

        print(f"All matching files have been combined into `{destination}`.")

    @staticmethod
    def zip_file(source, destination):
        print(f"Zipping `{source}` file to `{destination}`...")
        zip = zipfile.ZipFile(destination, "w", zipfile.ZIP_DEFLATED)
        zip.write(source)
        zip.close()
