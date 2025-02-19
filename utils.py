# -*- coding: utf-8 -*-
"""
Utility functions module.

Author: Brent
"""

import numpy as np
import logging
import os
import shutil
import tkinter as tk
from tkinter import filedialog
import pandas as pd

# Configuration
LOG_PATH = os.getenv("LOG_PATH", "E:/University of Central Florida/UCF_Photovoltaics_GRP - Documents/General/FSEC_PVMCF/module_databases/FSEC_Database_log.log")

def deserialize_array(blob, dtype=np.float64):
    """
    Deserialize arrays encoded during storage.

    Parameters:
    blob (bytes): Serialized array.
    dtype (np.dtype): Data type of the array.

    Returns:
    np.ndarray: Deserialized array.
    """
    return np.frombuffer(blob, dtype=dtype)

def create_logger():
    """
    Set up and configure a logger to track errors and system events.

    Returns:
    logging.Logger: Configured logger object.
    """
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)

    file_handler = logging.FileHandler(LOG_PATH)
    file_handler.setLevel(logging.DEBUG)

    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)
    if not logger.handlers:
        logger.addHandler(file_handler)
    logger.info("Main update database program started.")

    return logger

def get_files(title='Select files.'):
    """
    Prompt user to select file or files.

    Parameters:
    title (str): Title on the dialog box.

    Returns:
    list: Full file paths of selected files.
    """
    root = tk.Tk()
    files = list(filedialog.askopenfilenames(title=title))
    root.destroy()
    return files

def get_dir(title='Select directory.'):
    """
    Prompt user to select a directory.

    Parameters:
    title (str): Title on the dialog box.

    Returns:
    str: Directory path.
    """
    root = tk.Tk()
    found_dir = filedialog.askdirectory(title=title)
    found_dir = f"{found_dir}/"
    root.destroy()
    return found_dir

def copy_files(files_to_copy, dst=None):
    """
    Copies files to specified directory.

    Parameters:
    files_to_copy (list): List of files to copy.
    dst (str): Destination directory to copy the files into.

    Returns:
    list: List of new file names.
    """
    if not os.path.isdir(dst):
        dst = filedialog.askdirectory(title='Select directory to store copied files.')

    newnames = []
    for n, file in enumerate(files_to_copy):
        dst_file = f"{dst}/{os.path.basename(file)}"
        dst_file = dst_file.replace('//', '/')
        if not os.path.isfile(dst_file):
            try:
                shutil.copyfile(file, dst_file)
                newnames.append(dst_file)
                print(f"Copied {n+1} of {len(files_to_copy)}.")
            except:
                pass
    return newnames

def rename_file(full_filename, new_filename):
    """
    Rename a file.

    Parameters:
    full_filename (str): Current file name.
    new_filename (str): New file name.

    Returns:
    None
    """
    os.rename(full_filename, new_filename)
    print(new_filename)

def get_filename_metadata(file, datatype='iv'):
    """
    Extract metadata from the filename string based on FSEC PVMCF filename standards.

    Parameters:
    file (str): File path string.
    datatype (str): Type of measurement data.

    Returns:
    dict: Dictionary of metadata obtained from the filename string.
    """
    metadata_dict = {}
    bn_split = os.path.basename(file).split('_')
    ext = file.split('.')[-1]

    common_metadata = {
        'date': bn_split[0],
        'time': bn_split[1],
        'make': bn_split[2],
        'model': bn_split[3],
        'serial_number': bn_split[4],
        'comment': bn_split[5].split('.')[0]
    }

    if datatype == 'iv':
        metadata_dict.update(common_metadata)
        metadata_dict.update({
            'measurement_number': bn_split[6].replace(f".{ext}", '')
        })
    elif datatype == 'el':
        metadata_dict.update(common_metadata)
        metadata_dict.update({
            'exposure_time': bn_split[6].replace('s', ''),
            'current': bn_split[7].replace('A', ''),
            'voltage': bn_split[8].replace(f"V.{ext}", '')
        })
    elif datatype == 'ir':
        metadata_dict.update(common_metadata)
        metadata_dict.update({
            'exposure_time': bn_split[6].replace('s', ''),
            'current': bn_split[7].replace(f"A.{ext}", '')
        })
    elif datatype == 'dark_iv':
        metadata_dict.update(common_metadata)
    elif datatype == 'uvf':
        metadata_dict.update(common_metadata)
    elif datatype == 'v10':
        metadata_dict = {
            'serial-number': bn_split[4],
            'date': bn_split[0],
            'time': bn_split[1],
            'delay-time-(s)': bn_split[6].split('s')[0],
            'setpoint-total-time-(s)': bn_split[5].replace('s', '')
        }
    elif datatype == 'scanner':
        metadata_dict.update(common_metadata)
        metadata_dict.update({
            'module_id': bn_split[2],
            'exposure_time': bn_split[6],
            'current': bn_split[7],
            'voltage': bn_split[8],
            'image_type': bn_split[10].split('.')[0] if ext == 'jpg' else None,
            'cell_number': bn_split[11] if ext == 'jpg' and bn_split[10].split('.')[0] == 'cell' else None
        })

    return metadata_dict

def search_folders(date_threshold=20000000, parent_folder_path=''):
    """
    Uses a date threshold to select all folders in given parent path that beyond the given date.

    Parameters:
    date_threshold (int): Date threshold.
    parent_folder_path (str): Parent folder path.

    Returns:
    list: List of folders beyond the given date.
    """
    if not os.path.isdir(parent_folder_path):
        parent_folder_path = filedialog.askdirectory(title='Select source of data files to search through.')

    folders = []
    for dirpath, dirnames, filenames in os.walk(parent_folder_path):
        for dirname in dirnames:
            dirname = dirname.replace('-', '')
            try:
                if int(dirname) >= int(date_threshold):
                    new_folder = os.path.join(dirpath, dirname)
                    folders.append(new_folder)
                    print(f'{new_folder} added for processing.')
            except ValueError:
                print(f'{dirname} skipped.')
                pass
    return folders

def get_directory_names(source):
    """
    Uses os.walk to return a list of directories.

    Parameters:
    source (str): Source directory path.

    Returns:
    list: List of directory names.
    """
    directory_names = []
    for dirpath, dirnames, filenames in os.walk(source):
        for name in dirnames:
            directory_names.append(name)
            print(name)
    return directory_names

def search_files(serial_numbers=None, instrument_data_path=''):
    """
    Search for files based on serial numbers.

    Parameters:
    serial_numbers (list): List of serial numbers.
    instrument_data_path (str): Instrument data path.

    Returns:
    dict: Dictionary of measurement data.
    """
    if not serial_numbers:
        raise ValueError('Serial numbers list was empty.')

    if not os.path.isdir(instrument_data_path):
        instrument_data_path = filedialog.askdirectory(title='Select source of data files to search through.')

    src_dict = {
        'iv': f"{instrument_data_path}/Sinton_FMT/Results/MultiFlash/",
        'el': f"{instrument_data_path}/EL_DSLR_CMOS/",
        'darkiv': f"{instrument_data_path}/Dark_IV_Data/",
        'ir': f"{instrument_data_path}/IR_ICI/",
        'uvf': f"{instrument_data_path}/UVF_Images/",
        'spire': f"{instrument_data_path}/Spire/Data/",
        'v10': f"{instrument_data_path}/V10/"
    }

    instrument_data_dict = {}
    for measurement, measurement_data_src in src_dict.items():
        all_files = []
        print(f"Searching for {measurement} files.")

        for (dirpath, dirnames, filenames) in os.walk(measurement_data_src):
            [all_files.append(f"{dirpath}/{f}") for f in filenames if any(sn in f for sn in serial_numbers)]
            all_files = [a.replace('//', '/') for a in all_files]
            instrument_data_dict[measurement] = all_files

    return instrument_data_dict

def retrieve_module_data(serial_number, instrument_data_path):
    """
    Retrieve data for a specific module based on its serial number.

    Parameters:
    serial_number (str): Serial number of the module.
    instrument_data_path (str): Instrument data path.

    Returns:
    tuple: Serial number and dictionary of measurement data.
    """
    src_dict = {
        'iv': f"{instrument_data_path}/Sinton_FMT/Results/MultiFlash/",
        'el': f"{instrument_data_path}/EL_DSLR_CMOS/",
        'darkiv': f"{instrument_data_path}/Dark_IV_Data/",
        'ir': f"{instrument_data_path}/IR_ICI/",
        'uvf': f"{instrument_data_path}/UVF_Images/",
        'spire': f"{instrument_data_path}/Spire/Data/",
        'v10': f"{instrument_data_path}/V10/"
    }
    instrument_data_dict = {}

    for measurement, measurement_data_src in src_dict.items():
        all_files = []
        print(f"Searching for {measurement} files.")

        for (dirpath, dirnames, filenames) in os.walk(measurement_data_src):
            [all_files.append(f"{dirpath}/{f}") for f in filenames if serial_number in f]
            all_files = [a.replace('//', '/') for a in all_files]
            instrument_data_dict[measurement] = all_files
    return serial_number, instrument_data_dict

def copy_data_to_folder(instrument_data_dict=None, dst=None, raw_el_images=True):
    """
    Copy data to the specified folder.

    Parameters:
    instrument_data_dict (dict): Dictionary of measurement data.
    dst (str): Destination folder.
    raw_el_images (bool): Whether to include raw EL images.

    Returns:
    None
    """
    if not dst:
        dst = filedialog.askdirectory(title='Select folder where files will be copied to.')

    if not raw_el_images:
        instrument_data_dict['el'] = [image_file for image_file in instrument_data_dict['el'] if image_file[-3:].upper() == 'JPG']

    for measurement in instrument_data_dict:
        dst_measurement_dir = f"{dst}/{measurement.upper()}/"
        dst_measurement_dir = dst_measurement_dir.replace('//', '/')
        if not os.path.isdir(dst_measurement_dir):
            os.mkdir(dst_measurement_dir)
        print(f"Begin copying {measurement} files: {len(instrument_data_dict[measurement])} found.")
        copy_files(instrument_data_dict[measurement], dst=dst_measurement_dir)
        print(f"Finished copying {len(instrument_data_dict[measurement])} {measurement.upper()} files.")

def search_and_copy_files(serial_numbers=None, instrument_data_path='', dst=None, raw_el_images=True):
    """
    Search and copy files based on serial numbers.

    Parameters:
    serial_numbers (list): List of serial numbers.
    instrument_data_path (str): Instrument data path.
    dst (str): Destination folder.
    raw_el_images (bool): Whether to include raw EL images.

    Returns:
    None
    """
    instrument_data_dict = search_files(serial_numbers, instrument_data_path)
    copy_data_to_folder(instrument_data_dict, dst, raw_el_images)

def get_files_in_directory(source_dir=None):
    """
    Get a list of all files in a directory.

    Parameters:
    source_dir (str): Source directory path.

    Returns:
    list: List of file paths.
    """
    if not source_dir:
        source_dir = get_dir('Select source directory from which you want to load all files.')

    all_files = []
    for (dirpath, dirnames, filenames) in os.walk(source_dir):
        [all_files.append(f"{dirpath}/{f}") for f in filenames]
        all_files = [a.replace('//', '/') for a in all_files]

    return all_files