# src/trips_modifier.py

import csv
import os


def modify_trips_file(trips_path: str):
    """Modifica la columna block_id en trips.txt usando una subcadena de trip_id."""
    updated_rows = []
    with open(trips_path, "r", newline="") as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            trip_id = row["trip_id"]
            block_id = trip_id.split("_")[1]  # Asumimos que el separador es '_'
            row["block_id"] = block_id
            updated_rows.append(row)

    # Guardar el nuevo trips.txt modificado
    fieldnames = reader.fieldnames
    updated_trips_path = os.path.join(os.path.dirname(trips_path), "trips_modified.txt")
    with open(updated_trips_path, "w", newline="") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(updated_rows)

    return updated_trips_path
