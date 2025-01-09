from pathlib import Path
import os

def add_suffix_to_filename(filename, suffix, seperator = "_"):
  """
  Adds a suffix to the filename while preserving the original file extension.

  Args:
    filename: The original filename (including path if applicable).
    suffix: The suffix to be added to the filename.

  Returns:
    The new filename with the added suffix and the original extension.
  """
  path = Path(filename)
  new_filename = path.with_name(path.stem + seperator + suffix + path.suffix)
  return new_filename

def temp_video_path(video_path):
  """
  Modify the video_path to include a /temp/ directory before the filename.

  Args:
      video_path (str): The original path of the video file.

  Returns:
      str: The modified video path with /temp/ before the filename.
  """
  directory, filename = os.path.split(video_path)  # Split the path into directory and filename
  temp_directory = os.path.join(directory, 'temp')  # Create the /temp/ subdirectory path
  os.makedirs(temp_directory, exist_ok=True)       # Ensure the /temp/ directory exists
  return os.path.join(temp_directory, filename)    # Combine /temp/ with the filename

def copy_file_non_blocking(src_path, dest_path):
    with open(src_path, 'rb') as src, open(dest_path, 'wb') as dest:
        while chunk := src.read(1024 * 1024):  # Read in 1MB chunks
            dest.write(chunk)
    print(f"File copied from {src_path} to {dest_path}")
