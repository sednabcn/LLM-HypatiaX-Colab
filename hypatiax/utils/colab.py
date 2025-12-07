#save_model,mv_files,delete_non_empty_directory,files_management
import glob
import logging
import os
import shutil
import zipfile

from google.colab import drive, files

# Initialize logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def save_model(nlp, model_name, location):
    """ Save the SpaCy model to various locations. """
    try:
        folder_path = {
            'drive': '/content/drive/My Drive/MyModels',
            'colab': '/content',
            'disk': os.path.expanduser('~')
        }.get(location)

        if location == 'remote':
            logging.info("Manual steps for saving model remotely provided.")
            return

        if folder_path is None:
            logging.error("Invalid location provided. Use 'drive', 'colab', 'disk', or 'remote'.")
            return

        if location == 'drive':
            drive.mount('/content/drive')

        model_path = os.path.join(folder_path, model_name)
        nlp.to_disk(model_path)
        logging.info(f"Model saved successfully at {model_path}")
    except Exception as e:
        logging.error(f"Failed to save the model: {e}")

def mv_files(source_dir, target_dir):
    """ Move specified types of files from source directory to target directory. """
    try:
        for file_type in ['*.whl', '*.py', '*.txt']:
            for file_path in glob.glob(os.path.join(source_dir, file_type)):
                shutil.move(file_path, target_dir)
                logging.info(f"Moved {file_path} to {target_dir}")
    except Exception as e:
        logging.error(f"Failed to move files from {source_dir} to {target_dir}: {e}")

def delete_non_empty_directory(path):
    """ Delete a non-empty directory. """
    try:
        if os.path.exists(path) and os.path.isdir(path):
            shutil.rmtree(path)
            logging.info(f"Directory {path} has been deleted successfully.")
        else:
            logging.warning(f"The path {path} does not exist or is not a directory.")
    except Exception as e:
        logging.error(f"Failed to delete {path}: {e}")

def files_management(option, filename):
    """ Manage files based on given option and filename. """
    file_path = f'/content/{filename}'
    try:
        if option == 'update':
            # Add logic for update if specific
            logging.info(f"Update option selected for {filename}.")

        # Upload or process files
        if not os.path.exists(file_path):
            files.upload()  # Upload if file doesn't exist

            if file_path.endswith('.zip'):
                with zipfile.ZipFile(file_path, 'r') as zip_ref:
                    zip_ref.extractall('/content/')
                    os.remove(file_path)
                logging.info(f"Extracted {file_path} successfully.")

        mv_files('/content/upload_colab', '/content')
        delete_non_empty_directory('/content/upload_colab')
    except Exception as e:
        logging.error(f"Error managing files: {e}")

    logging.info("Current directory content:")
    logging.info(os.listdir('/content/'))

# Example of using the save_model function
# nlp = spacy.load('en_core_web_sm')
# save_model(nlp, 'my_model', 'drive')

def move_file(file_name, target_path):
    uploaded_file_path = os.path.join('/content', file_name)

    # Check if the file exists in the /content directory
    if os.path.exists(uploaded_file_path):
        # Move the file to the target path
        os.replace(uploaded_file_path, target_path)
        print(f'{file_name} has been moved to {target_path}')
    else:
        print(f'{file_name} does not exist in /content')

def maintenance(file_name, dir_name=None):
    # Define the base path for the package
    base_path = '/usr/local/lib/python3.10/dist-packages/hypatiax/'

    if dir_name is None:
        target_path = os.path.join(base_path, file_name)
    else:
        target_path = os.path.join(base_path, dir_name, file_name)

    # Remove the existing file if it exists
    if os.path.exists(target_path):
        os.remove(target_path)

    # Upload the new file
    uploaded = files.upload()

    move_file(file_name, target_path)
    """
    # Move the uploaded file to the target path
    uploaded_file_path = os.path.join('/content', file_name)
    if os.path.exists(uploaded_file_path):
        os.replace(uploaded_file_path, target_path)
        print(f'{file_name} has been moved to {target_path}')
    else:
        raise FileNotFoundError(f"Uploaded file {file_name} not found in /content.")
    """
    # Return the list of files in the current working directory
    return os.listdir('/content')

# Example usage
# maintenance('example_file.py')  # Adjust the file name and directory name as needed

def cleaning(file_name=None):
   import os
   directory='/content/'
   if isinstance(file_name,list):
      for file in file_name:
         file_path=os.path.join(directory,file)
         !rm "{file_path}"
         print(f'{file} has been deleted from /content/')
      return print(f'{file_name} list have been deleted')
   elif file_name:
      file_path=os.path.join(directory,file_name)
      !rm "{file_path}"
      return print(f'{file_name} has been deleted from /content/')
   else:
      !rm -R /content/

def assert_package_exists(package_name):
    package_dir = '/usr/local/lib/python3.10/dist-packages'
    package_list = os.listdir(package_dir)
    assert package_name in package_list, f"Package '{package_name}' not found in {package_dir}"

def working_in_content(command,version):
    import subprocess

    # Construct the file path
    file_path = f'/content/hypatiax-{version}-py3-none-any.whl'

    # Combine the command and the file path into a single string
    full_command = f"{command} {file_path}"

    # Use subprocess.run to execute the command
    result = subprocess.run([full_command, file_path],shell=True,capture_output=True, text=True)

    # Check if the command was successful
    if result.returncode == 0:
        print(f"{command} {file_path} successful.")
    else:
        print(f"{command} {file_path} failed.")
        print("Error:", result.stderr)

def upload_check_files(task=True):
  import os

  from google.colab import files
  if task:
      files.upload()
  return print(os.listdir('/content'))
