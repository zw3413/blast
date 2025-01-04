from pathlib import Path

def add_suffix_to_filename(filename, suffix):
  """
  Adds a suffix to the filename while preserving the original file extension.

  Args:
    filename: The original filename (including path if applicable).
    suffix: The suffix to be added to the filename.

  Returns:
    The new filename with the added suffix and the original extension.
  """
  path = Path(filename)
  new_filename = path.with_name(path.stem + "_" + suffix + path.suffix)
  return new_filename