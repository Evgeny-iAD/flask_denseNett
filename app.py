import os
import tempfile

from flask import Flask, render_template, request, redirect, url_for
from neuro.NeuralNetworkOperationV2 import main as neuro_analysis

app = Flask(__name__)


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # Здесь  можно обработать загруженный файл
        uploaded_file = request.files['file']
        # Читаем содержимое файла
        file_content = uploaded_file.read()
        file_name = uploaded_file.filename

        # Создаем временный файл и записываем в него содержимое загруженного файла
        temp_dir = tempfile.mkdtemp()
        temp_file_path = os.path.join(temp_dir, file_name)
        with open(temp_file_path, 'wb') as temp_file:
            temp_file.write(file_content)

        neuro_analysis(temp_file_path, 'H:/FLASK/Project_chexnet_v1/static/heatmaps')

        # Удаляем временный файл и папку
        os.remove(temp_file_path)
        os.rmdir(temp_dir)

        return render_template('index.html', file_name=file_name, table_caption='Результаты анализа нейросетью')


    return render_template('index.html', file_name='Имя файла', table_caption='')


if __name__ == '__main__':
    app.run(debug=True)
