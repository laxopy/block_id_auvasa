import os
import subprocess
import requests
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from datetime import datetime


app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})  # Permitir todas las solicitudes

# Directorios para entrada y salida
UPLOAD_FOLDER = './GTFS-IN'
OUTPUT_FOLDER = './GTFS-OUT'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

def get_timestamped_filename(original_filename, force_extension=None):
    """Generar un nombre de archivo con fecha y hora, y opcionalmente forzar una extensión."""
    timestamp = datetime.now().strftime('%Y%m%d-%H%M%S')
    name, ext = os.path.splitext(original_filename)
    if force_extension:
        ext = force_extension
    return f"{name}_{timestamp}{ext}"

@app.route('/upload', methods=['POST'])
def upload_file():
    file_path = ''
    
    # Verificar si se ha subido un archivo o una URL
    if 'gtfs' in request.files:
        file = request.files['gtfs']
        if file.filename == '':
            return jsonify({'error': 'No selected file'}), 400
        
        # Generar nombre con fecha y hora
        file_name = get_timestamped_filename(file.filename)
        file_path = os.path.join(UPLOAD_FOLDER, file_name)
        file.save(file_path)
        print(f"Archivo subido guardado en: {file_path}")

    elif 'url' in request.form:
        url = request.form['url']
        if not url:
            return jsonify({'error': 'No URL provided'}), 400
        
        try:
            # Descargar el archivo desde la URL
            print(f"Intentando descargar archivo desde URL: {url}")
            response = requests.get(url)
            
            if response.status_code != 200:
                print(f"Error al descargar archivo desde la URL: {url}")
                print(f"Código de estado HTTP: {response.status_code}")
                print(f"Contenido de la respuesta: {response.text}")
                return jsonify({'error': 'Failed to download file from URL'}), 500
            
            # Obtener el nombre del archivo desde la URL y forzar extensión .zip
            file_name = get_timestamped_filename(url.split('/')[-1], force_extension='.zip')
            file_path = os.path.join(UPLOAD_FOLDER, file_name)

            # Guardar el archivo descargado
            with open(file_path, 'wb') as f:
                f.write(response.content)
            print(f"Archivo descargado desde la URL guardado en: {file_path}")

        except Exception as e:
            print(f"Error al descargar desde URL: {e}")
            return jsonify({'error': 'Error downloading file from URL'}), 500

    else:
        return jsonify({'error': 'No file or URL provided'}), 400

    # Verificar si el archivo descargado es un .zip
    if not file_path.endswith('.zip'):
        print(f"No se encontró ningún archivo ZIP en la carpeta GTFS-IN.")
        return jsonify({'error': 'No ZIP file found'}), 500

    # Ejecutar el proceso de transformación
    subprocess.run(['python', 'main.py'])

    # Encontrar el archivo generado en GTFS-OUT
    files = sorted([f for f in os.listdir(OUTPUT_FOLDER) if f.endswith('.zip')], key=lambda x: os.path.getmtime(os.path.join(OUTPUT_FOLDER, x)), reverse=True)
    if not files:
        return jsonify({'error': 'No processed files found'}), 500

    # Obtener el archivo más reciente en GTFS-OUT y renombrarlo con fecha y hora
    modified_file_name = files[0]
    new_modified_file_name = get_timestamped_filename(modified_file_name)
    modified_file_path = os.path.join(OUTPUT_FOLDER, modified_file_name)
    new_modified_file_path = os.path.join(OUTPUT_FOLDER, new_modified_file_name)

    # Renombrar el archivo con el apéndice de fecha y hora
    os.rename(modified_file_path, new_modified_file_path)
    print(f"Archivo renombrado en GTFS-OUT: {new_modified_file_name}")

    # Enviar el archivo modificado usando send_file
    return send_file(new_modified_file_path, as_attachment=True, download_name=new_modified_file_name)

if __name__ == '__main__':
    app.run(debug=True, port=5000)