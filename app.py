import base64
import functools
import json
import os
import sys
import tempfile
import time
import uuid
from datetime import datetime

from sqlalchemy import create_engine, text
from sqlalchemy.exc import OperationalError
from flask import Flask, render_template, request, redirect, url_for, jsonify

from dicomMove.DicomMove import DicomFindMove
from neuro.NeuralNetworkOperationV2 import main as neuro_analysis

from neuro.model_db import db, OriginalImage, AnalysisResult, SearchResult

app = Flask(__name__)
# app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://userdb:passdb@localhost/dbdicom'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///dbdicom.db'
db.init_app(app)

def load_config():
    # Получаем путь к текущей директории
    current_dir = os.path.dirname(os.path.abspath(__file__))
    # Путь к файлу конфигурации в папке dicomMove
    config_path = os.path.join(current_dir, "dicomMove", "DICOMconfig.json")

    # Проверяем, существует ли файл конфигурации
    if os.path.isfile(config_path):
        with open(config_path, "r") as file:
            dic_config = json.load(file)
        return dic_config
    else:
        print(f"Файл конфигурации не найден. Путь {config_path}")
        return None

@app.cli.command("init-db")
def init_db():
    db.create_all()
    print("OK")

@app.route('/', methods=['GET', 'POST'])
def index():
    # if not is_database_available():
    #     return "Database is not available"
    patient_id = '55'
    study_id = '123.32.55520.321'

    if request.method == 'POST':
        # Здесь  можно обработать загруженный фай
        uploaded_file = request.files['file']
        # Читаем содержимое файла
        file_content = uploaded_file.read()
        file_name = uploaded_file.filename

        original_image_test = OriginalImage(patient_id=patient_id, study_id=study_id, image=file_content)
        db.session.add(original_image_test)
        db.session.commit()


        # Вариант с сокращением имени файла !!!!!
        # file = request.files.get('file')
        # file_name = secure_filename(file.filename)
        # file.save(PurePath.joinpath(Path.cwd(), 'uploads', file_name))

        # # Создаем временный файл из БД и записываем в него содержимое загруженного файла
        temp_dir = tempfile.mkdtemp()
        temp_file_path = os.path.join(temp_dir, 'temp_image.png')
        with open(temp_file_path, 'wb') as temp_file:
            temp_file.write(original_image_test.image)

        output_dir = tempfile.mkdtemp()  # Создаем временную директорию

        # neuro_analysis(temp_file_path, 'H:/FLASK/Project_chexnet_v1/static/heatmaps')

        neuro_analysis(temp_file_path, output_dir)

        heatmap_image = AnalysisResult(patient_id=patient_id, original_images=original_image_test.image)
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
        image_base64 = base64.b64encode(original_image_test.image).decode('utf-8')
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

        print(get_database_size())

        return render_template('index.html',
                               file_name=file_name,
                               table_caption='Тепловые карты вероятных паталогий',
                               patient_id=original_image_test.patient_id,
                               orig_image=image_base64,
                               atelectasis=atelectasis_base64, cardiomegaly=cardiomegaly_base64,
                               effusion=effusion_base64, infiltration=infiltration_base64,
                               mass=mass_base64, nodule=nodule_base64,
                               pneumonia=pneumonia_base64, pneumothorax=pneumothorax_base64,
                               consolidation=consolidation_base64, edema=edema_base64,
                               emphysema=emphysema_base64, fibrosis=fibrosis_base64,
                               pleural_thickening=pleural_thickening_base64, hernia=hernia_base64,
                               loading_message=False) # Передаем параметр для отображения сообщения

    return render_template('index.html', file_name='Имя файла', table_caption='')

# проверка доступности сервера dicom
@app.route('/check_server_status')
def check_pacs_status():
    # код для проверки доступности сервера ПАКС
    dic_config = load_config()
    perform = DicomFindMove(dic_config, client_Id=None)
    start_time = time.time()
    echo = perform.perform_echo()
    end_time = time.time()
    elapsed_time = end_time - start_time
    print(u'C-ECHO: {}'.format(echo), u'| TIME C-ECHO: {}'.format(elapsed_time))

    is_server_available, status = echo

    if is_server_available:
        status_color = 'green'
    else:
        status_color = 'red'

    return jsonify({'status_color': status_color})

# поиск в паксе данных и запись в БД
@app.route('/find_patient_study')
def c_find_pacs():
    # код для проверки доступности сервера ПАКС
    dic_config = load_config()
    start_time = time.time()
    performFind = DicomFindMove(dic_config, client_Id=dic_config['test_id'])
    # Вызов perform_find с передачей параметра callback и additional_param в handle_result
    # Генерация номера запроса
    id_query = str(uuid.uuid4())
    def handle_result(result_seri):
        print(u'{}'.format(result_seri))
        # Сохранение результатов в базе данных

        search_result = SearchResult(
            query_id=id_query,
            study_date=datetime.strptime(result_seri['StudyDate'], "%Y%m%d").strftime("%d.%m.%Y"),
            patient_name=str(result_seri['PatientName']),
            patient_birth=datetime.strptime(result_seri['PatientBirthDate'], "%Y%m%d").strftime("%d.%m.%Y"),
            study_instance_uid=result_seri['StudyInstanceUID']
        )
        db.session.add(search_result)
        db.session.commit()

    performFind.perform_find(full_name=None, callback=handle_result)
    end_time = time.time()
    elapsed_time = end_time - start_time
    print(u'| TIME C-FIND: {}'.format(elapsed_time))

    # Получение данных из базы данных
    with db.session.begin():
        search_results = SearchResult.query.filter_by(query_id=id_query).all()

    print('id_query', id_query)

    # Преобразование данных в список словарей
    results_list = []
    for result in search_results:
        results_list.append({
            'study_date': result.study_date,
            'patient_name': result.patient_name,
            'patient_birth': result.patient_birth,
            'query_id': result.query_id,
            'study_instance_uid': result.study_instance_uid
        })

    return jsonify(results_list)

@app.route('/move_patient_images')
def c_move_pacs():
    dic_config = load_config()
    query_id = request.args.get('query_id')
    study_instance_uid = request.args.get('study_instance_uid')

    print('query_id:', query_id)
    print('study_instance_uid:', study_instance_uid)

    # запуск c_move---------------------
    req_dic_server = DicomFindMove(dic_config, client_Id=None)
    req_dic_server.study_instance_uid = study_instance_uid

    def callback(id_uid, image_paths):
        with app.app_context():
            file_image = image_paths

            image_data = file_image[0].read()

            original_result = OriginalImage(
                query_id=id_uid[0],
                study_instance_uid=id_uid[1],
                image=image_data
            )

            try:
                with db.session.begin():
                    db.session.add(original_result)
                # TEST Выводим данные на экран ---------------
                print('Original Image ID:', original_result.id)
                print('query_id:', original_result.query_id)
                print('study_instance_uid:', original_result.study_instance_uid)
                print('Image Size:', len(original_result.image))
                # TEST ---------------------------------------
            except Exception as e:
                print('Error:', e)

    # req_dic_server.perform_move(callback)
    callback_with_db = functools.partial(callback, [query_id, study_instance_uid])
    req_dic_server.perform_move(callback_with_db)

    # Вернуть какой-либо ответ
    # Преобразование данных в список словарей
    # Получение данных из базы данных
    with db.session.begin():
        search_results = SearchResult.query.filter_by(query_id=query_id).all()
        original_result = OriginalImage.query.filter_by(query_id=query_id).all()

    results_list = []
    for result1 in search_results:
        results_list.append({
            'study_date': result1.study_date,
            'patient_name': result1.patient_name,
            'patient_birth': result1.patient_birth,
            'query_id': result1.query_id,
            'study_instance_uid': result1.study_instance_uid
        })
        for result2 in original_result:
            results_list.append({
                'study_date': " ",
                'patient_name': 'Изображение',
                'patient_birth': result2.id,
                'query_id': " ",
                'study_instance_uid': " "
            })

    return jsonify(results_list)
    # return jsonify({'message': 'c_move_pacs executed successfully'})

@app.route('/upload_image_preview')
def upload_image_preview():
    # Преобразование бинарных данных изображения в Base64 строку
    id_image = request.args.get('id')
    original_image = OriginalImage.query.filter_by(id=id_image).first()
    if original_image:
        image_data = original_image.image
        image_base64 = base64.b64encode(image_data).decode('utf-8')
    else:
        image_data = None
        image_base64 = base64.b64encode(image_data).decode('utf-8')

    return jsonify(orig_image=image_base64)

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

def sizeof_fmt(num, suffix='B'):
    for unit in ['','Ki','Mi','Gi','Ti','Pi','Ei','Zi']:
        if abs(num) < 1024.0:
            return "%3.1f %s%s" % (num, unit, suffix)
        num /= 1024.0
    return "%.1f %s%s" % (num, 'Yi', suffix)

def get_database_size():
    query = text("SELECT page_count * page_size AS size FROM pragma_page_count(), pragma_page_size();")
    result = db.session.execute(query)
    size = result.fetchone()[0]
    return sizeof_fmt(size)

if __name__ == '__main__':
    app.run(debug=True)
