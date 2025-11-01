#save_model,mv_files,delete_non_empty_directory,files_management
import os
import shutil
import zipfile
import glob
import logging
from google.colab import files, drive

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
