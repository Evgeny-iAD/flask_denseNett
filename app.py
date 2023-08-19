import base64
import os
import tempfile
from sqlalchemy import create_engine
from sqlalchemy.exc import OperationalError
from flask import Flask, render_template, request, redirect, url_for
from neuro.NeuralNetworkOperationV2 import main as neuro_analysis

from neuro.model_db import db, OriginalImage, AnalysisResult

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://userdb:passdb@localhost/dbdicom'
db.init_app(app)

def is_database_available():
    try:
        engine = create_engine(app.config['SQLALCHEMY_DATABASE_URI'])
        connection = engine.connect()
        connection.close()
        return True
    except OperationalError:
        return False
@app.route('/', methods=['GET', 'POST'])
def index():
    if not is_database_available():
        return "Database is not available"
    patient_id = '55'
    study_id = '123.32.55520.321'
    if request.method == 'POST':
        # Здесь  можно обработать загруженный фай
        uploaded_file = request.files['file']
        # Читаем содержимое файла
        file_content = uploaded_file.read()
        file_name = uploaded_file.filename

        original_image = OriginalImage(patient_id=patient_id, study_id=study_id, image=file_content)
        db.session.add(original_image)
        db.session.commit()
        print('original_image', original_image)

        # TEST Выводим данные на экран ---------------
        print('Original Image ID:', original_image.id)
        print('Patient ID:', original_image.patient_id)
        print('Study ID:', original_image.study_id)
        print('Image Size:', len(original_image.image))
        # TEST ---------------------------------------

        # Создаем временный файл и записываем в него содержимое загруженного файла
        temp_dir = tempfile.mkdtemp()
        temp_file_path = os.path.join(temp_dir, file_name)
        with open(temp_file_path, 'wb') as temp_file:
            temp_file.write(file_content)

        # Вариант с сокращением имени файла !!!!!
        # file = request.files.get('file')
        # file_name = secure_filename(file.filename)
        # file.save(PurePath.joinpath(Path.cwd(), 'uploads', file_name))

        # Удаляем временный файл и папку
        # os.remove(temp_file_path)
        # os.rmdir(temp_dir)

        neuro_analysis(temp_file_path, 'H:/FLASK/Project_chexnet_v1/static/heatmaps')

        # Преобразование бинарных данных изображения в Base64 строку
        image_base64 = base64.b64encode(original_image.image).decode('utf-8')

        return render_template('index.html',
                               file_name=file_name,
                               table_caption='Тепловые карты вероятных паталогий',
                               patient_id=original_image.patient_id,
                               orig_image=image_base64)

    return render_template('index.html', file_name='Имя файла', table_caption='')

if __name__ == '__main__':
    app.run(debug=True)
