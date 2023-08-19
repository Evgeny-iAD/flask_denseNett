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
        # temp_dir = tempfile.mkdtemp()
        # temp_file_path = os.path.join(temp_dir, file_name)
        # with open(temp_file_path, 'wb') as temp_file:
        #     temp_file.write(file_content)

        # Вариант с сокращением имени файла !!!!!
        # file = request.files.get('file')
        # file_name = secure_filename(file.filename)
        # file.save(PurePath.joinpath(Path.cwd(), 'uploads', file_name))

        # # Создаем временный файл из БД и записываем в него содержимое загруженного файла
        temp_dir = tempfile.mkdtemp()
        temp_file_path = os.path.join(temp_dir, 'temp_image.png')
        with open(temp_file_path, 'wb') as temp_file:
            temp_file.write(original_image.image)

        output_dir = tempfile.mkdtemp()  # Создаем временную директорию

        # neuro_analysis(temp_file_path, 'H:/FLASK/Project_chexnet_v1/static/heatmaps')
        neuro_analysis(temp_file_path, output_dir)

        heatmap_image = AnalysisResult(patient_id=patient_id, original_images=original_image.image)
        heatmap_image.atelectasis = get_image(output_dir, 'atelectasis.png')
        heatmap_image.cardiomegaly = get_image(output_dir, 'cardiomegaly.png')
        heatmap_image.effusion = get_image(output_dir, 'effusion.png')
        heatmap_image.infiltration = get_image(output_dir, 'infiltration.png')
        heatmap_image.mass = get_image(output_dir, 'mass.png')
        heatmap_image.nodule = get_image(output_dir, 'nodule.png')
        heatmap_image.pneumonia = get_image(output_dir, 'pneumonia.png')
        heatmap_image.pneumothorax = get_image(output_dir, 'pneumothorax.png')
        heatmap_image.consolidation = get_image(output_dir, 'consolidation.png')
        heatmap_image.edema = get_image(output_dir, 'edema.png')
        heatmap_image.emphysema = get_image(output_dir, 'emphysema.png')
        heatmap_image.fibrosis = get_image(output_dir, 'fibrosis.png')
        heatmap_image.pleural_thickening = get_image(output_dir, 'pleural_thickening.png')
        heatmap_image.hernia = get_image(output_dir, 'hernia.png')
        db.session.add(heatmap_image)
        db.session.commit()
        print('original_image', heatmap_image)


        # Проверить, существует ли директория output_dir
        search_file_dir(output_dir)

        # Удалить временную директорию и файлы
        temp_rmdir(temp_dir)
        temp_rmdir(output_dir)

        # Преобразование бинарных данных изображения в Base64 строку
        image_base64 = base64.b64encode(original_image.image).decode('utf-8')
        atelectasis_base64 = base64.b64encode(heatmap_image.atelectasis).decode('utf-8')
        cardiomegaly_base64 = base64.b64encode(heatmap_image.cardiomegaly).decode('utf-8')
        effusion_base64 = base64.b64encode(heatmap_image.effusion).decode('utf-8')
        infiltration_base64 = base64.b64encode(heatmap_image.infiltration).decode('utf-8')
        mass_base64 = base64.b64encode(heatmap_image.mass).decode('utf-8')
        nodule_base64 = base64.b64encode(heatmap_image.nodule).decode('utf-8')
        pneumonia_base64 = base64.b64encode(heatmap_image.pneumonia).decode('utf-8')
        pneumothorax_base64 = base64.b64encode(heatmap_image.pneumothorax).decode('utf-8')
        consolidation_base64 = base64.b64encode(heatmap_image.consolidation).decode('utf-8')
        edema_base64 = base64.b64encode(heatmap_image.edema).decode('utf-8')
        emphysema_base64 = base64.b64encode(heatmap_image.emphysema).decode('utf-8')
        fibrosis_base64 = base64.b64encode(heatmap_image.fibrosis).decode('utf-8')
        pleural_thickening_base64 = base64.b64encode(heatmap_image.pleural_thickening).decode('utf-8')
        hernia_base64 = base64.b64encode(heatmap_image.hernia).decode('utf-8')

        return render_template('index.html',
                               file_name=file_name,
                               table_caption='Тепловые карты вероятных паталогий',
                               patient_id=original_image.patient_id,
                               orig_image=image_base64,
                               atelectasis=atelectasis_base64,  cardiomegaly=cardiomegaly_base64,
                               effusion=effusion_base64,  infiltration=infiltration_base64,
                               mass=mass_base64,  nodule=nodule_base64,
                               pneumonia=pneumonia_base64,  pneumothorax=pneumothorax_base64,
                               consolidation=consolidation_base64,  edema=edema_base64,
                               emphysema=emphysema_base64,  fibrosis=fibrosis_base64,
                               pleural_thickening=pleural_thickening_base64,  hernia=hernia_base64,
                               )

    return render_template('index.html', file_name='Имя файла', table_caption='')

# удаление временной директории
def temp_rmdir(dir):
    # Проверяем, существует ли папка и она является директорией
    if os.path.exists(dir) and os.path.isdir(dir):
        # Получаем список файлов в папке
        files_in_output_dir = os.listdir(dir)

        # Перебираем файлы и удаляем каждый файл
        for filename in files_in_output_dir:
            full_path = os.path.join(dir, filename)
            if os.path.isfile(full_path):
                os.remove(full_path)

        # После удаления файлов, удаляем пустую папку
        os.rmdir(dir)
    else:
        print("Output directory does not exist or is not a directory")

def search_file_dir(dir):
    # Проверить, существует ли директория output_dir
    if os.path.exists(dir) and os.path.isdir(dir):
        # Получить список файлов в директории
        files_in_output_dir = os.listdir(dir)

        # Перебрать файлы и выполнить нужные действия
        for filename in files_in_output_dir:
            full_path = os.path.join(dir, filename)
            if os.path.isfile(full_path):
                print(f"Found file: {filename}")

def get_image(output_dir, image_filename):
    image_path = os.path.join(output_dir, image_filename)

    # Проверить, существует ли файл
    if os.path.exists(image_path) and os.path.isfile(image_path):
        # Открыть файл и прочитать его содержимое
        with open(image_path, 'rb') as image_file:
            image_content = image_file.read()


        print(type(image_content))
        return image_content
    else:
        return None


if __name__ == '__main__':
    app.run(debug=True)
