# src/gtfs_processor.py

import os
import zipfile


def unzip_file(input_path: str, extract_to: str):
    """Descomprime el archivo ZIP en la carpeta especificada."""
    with zipfile.ZipFile(input_path, "r") as zip_ref:
        zip_ref.extractall(extract_to)


def zip_gtfs(output_zip: str, input_folder: str):
    """Genera un nuevo archivo ZIP con todos los archivos de la carpeta."""
    with zipfile.ZipFile(output_zip, "w") as zipf:
        for foldername, subfolders, filenames in os.walk(input_folder):
            for filename in filenames:
                file_path = os.path.join(foldername, filename)
                zipf.write(file_path, os.path.relpath(file_path, input_folder))
