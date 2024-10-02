import os
from src.gtfs_processor import unzip_file, zip_gtfs
from src.trips_modifier import modify_trips_file


def main():
    input_folder = "GTFS-IN"
    extract_folder = "GTFS-IN/extracted"
    output_folder = "GTFS-OUT"

    # Buscar el primer archivo ZIP en la carpeta GTFS-IN
    input_zip = None
    for file in os.listdir(input_folder):
        if file.endswith(".zip"):
            input_zip = os.path.join(input_folder, file)
            break

    if input_zip is None:
        print("No se encontró ningún archivo ZIP en la carpeta GTFS-IN.")
        return

    output_zip = os.path.join(output_folder, "modified_gtfs.zip")

    # 1. Descomprimir el archivo ZIP
    unzip_file(input_zip, extract_folder)

    # 2. Modificar trips.txt
    trips_path = os.path.join(extract_folder, "trips.txt")
    modified_trips_path = modify_trips_file(trips_path)

    # 3. Reemplazar el trips.txt original por el modificado
    os.replace(modified_trips_path, trips_path)

    # 4. Comprimir de nuevo el archivo GTFS
    zip_gtfs(output_zip, extract_folder)


if __name__ == "__main__":
    main()
