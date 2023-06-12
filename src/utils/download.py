import gzip
import shutil
import os
import requests


def download_file(url, destination):
    response = requests.get(url)
    if response.status_code == 200:
        with open(destination, 'wb') as file:
            for chunk in response.iter_content(chunk_size=1024):
                if chunk:
                    file.write(chunk)
        print(f"Download complete: {destination}")
        expanded_file = unzip_gz(destination)
        return expanded_file
    else:
        print(f"Failed to download file from {url}")


def unzip_gz(filepath, output_dir=None):
    if output_dir is None:
        output_dir = os.path.dirname(filepath)

    try:
        filename = os.path.basename(filepath)
        output_path = os.path.join(output_dir, filename[:-3])  # Remove the '.gz' extension

        with gzip.open(filepath, 'rb') as gz_file:
            with open(output_path, 'wb') as unzipped_file:
                shutil.copyfileobj(gz_file, unzipped_file)

        return output_path
    except IOError as e:
        print(f"Failed to unzip .gz file: {e}")

    return None

