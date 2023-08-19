import os
import time
import cv2
import numpy as np
import torchvision
from torchvision import transforms
from torchvision.models import DenseNet121_Weights
from neuro.config import MODEL_PATH, TRANS_CROP, WORK_DATA_DIR, HEATMAP_DATA_DIR, CLASS_NAMES
import torch.nn as nn
import torch
from PIL import Image


class DenseNet121(nn.Module):
    def __init__(self, classCount, isTrained):
        super(DenseNet121, self).__init__()
        self.densenet121 = torchvision.models.densenet121(weights=DenseNet121_Weights.IMAGENET1K_V1)
        kernelCount = self.densenet121.classifier.in_features
        self.densenet121.classifier = nn.Sequential(nn.Linear(kernelCount, classCount), nn.Sigmoid())
    def forward(self, x):
        x = self.densenet121(x)
        return x
# Вычисление вероятностей по каждому классу
# Построение тепловой карты по полученным данным
class NeuralOperation():
    def __init__(self):
        self.modelPath = MODEL_PATH
        self.nClassCount = 14
        self.transCrop = TRANS_CROP
        self.dataDir = WORK_DATA_DIR
        self.outDataDir = HEATMAP_DATA_DIR
        self.batchSize = 1
        self.className = CLASS_NAMES
        self.device = torch.device("cpu")
        # Инициализация модели и загрузка весов
        model = DenseNet121(self.nClassCount, True)
        model = model.cpu()
        self.model = torch.nn.DataParallel(model, device_ids=None)

        # Загружает сохраненные веса модели, если они доступны
        if os.path.isfile(MODEL_PATH):
            print(f"=> загрузка контрольной точки предобученной модели {self.modelPath}")
            self.modelCheckpoint = torch.load(MODEL_PATH, map_location=self.device)['state_dict']
            for k in list(self.modelCheckpoint.keys()):
                index = k.rindex('.')
                if (k[index - 1] == '1' or k[index - 1] == '2'):
                    self.modelCheckpoint[k[:index - 2] + k[index - 1:]] = self.modelCheckpoint[k]
                    del self.modelCheckpoint[k]
            self.model.load_state_dict(self.modelCheckpoint)
            print("=> контрольная точка модели загружена")
        else:
            print("=> контрольная точка модели не найдена")

        self.modelTest()
        self.model.eval()
    # тест модели
    def modelTest(self):
        input_size = (3, 224, 224)  # Define the input size
        dummy_input = torch.randn(1, *input_size).to(self.device)  # Create a dummy input tensor on the device
        # Pass the dummy_input through the model for testing
        output = self.model(dummy_input)
        # Print the output
        print(f'Тестовые данные: {output}')
        # Вывод архитектуры модели
        # print(self.model)
        # Проверка наличия ключа с пороговыми значениями в словаре состояния модели
        if 'thresholds' in self.modelCheckpoint:
            thresholds = self.modelCheckpoint['thresholds']
            print("Пороговые значения найдены в модели:")
            print(thresholds)
        else:
            print("Модель не содержит пороговых значений.")

    # предподготовка изображения
    def preprocess_image(self, image_path):
        image = Image.open(image_path).convert("RGB")
        preprocess = transforms.Compose([
            transforms.Resize((self.transCrop, self.transCrop)),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
        ])
        image_tensor = preprocess(image)
        image_tensor = torch.unsqueeze(image_tensor, 0)
        return image_tensor
    # вычисление предсказаний по снимку
    def analyze_xray(self, image_path):
        results = []
        image_tensor = self.preprocess_image(image_path)
        image_tensor = image_tensor.to(self.device)
        outputs = self.model(image_tensor)
        probabilities = outputs
        image_results = []
        for i in range(len(self.className)):
            result = {
                'class': self.className[i],
                'probability': round(probabilities[0][i].item(), 3)
            }
            image_results.append(result)
        # если нужно, тут сортируется максимальный
        max_prediction = max(image_results, key=lambda x: x['probability'])
        results.append({
            'images': image_path,
            'predictions': image_results
        })
        return results
    # работа с тепловой картой
    def plot_heatmap(self, image_path, class_index, outDataDir):
        print(image_path)
        image_tensor = self.preprocess_image(image_path)
        heatmap = self.generate_heatmap(image_tensor, class_index)
        # Загружаем изображение и изменяем его размеры
        img = cv2.imread(image_path)
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        heatmap_resized = cv2.resize(heatmap, (img.shape[1], img.shape[0]))
        # Применяем тепловую карту к изображению
        heatmap_jet = cv2.applyColorMap(np.uint8(255 * heatmap_resized), cv2.COLORMAP_JET)
        # Наложение тепловой карты на изображение
        superimposed_img = cv2.addWeighted(img, 0.7, heatmap_jet, 0.3, 0)
        # Сохраняем тепловую карту
        filename = os.path.basename(image_path)
        out_path = os.path.join(outDataDir, f"{CLASS_NAMES[class_index]}.png")
        cv2.imwrite(out_path, superimposed_img)
    # генератор тепловой карты
    def generate_heatmap(self, image_tensor, class_index):
        self.model = self.model.to(self.device)
        image_tensor = image_tensor.to(self.device)

        # Получаем активации слоя перед последним полносвязным слоем
        features = self.model.module.densenet121.features(image_tensor)
        features = features.to(self.device)

        weights = self.model.module.densenet121.classifier[0].weight[class_index]

        # Умножаем активации на веса, чтобы получить вклад каждого пикселя в предсказание данного класса
        heatmap = torch.sum(features * weights.view(1, -1, 1, 1), dim=1)
        heatmap = torch.relu(heatmap)
        heatmap = heatmap.detach().cpu().numpy()[0]
        # Нормализуем heatmap
        heatmap = (heatmap - np.min(heatmap)) / (np.max(heatmap) - np.min(heatmap) + 1e-8)

        return heatmap
    # вычисление с пороговых значений
    def apply_thresholds(self, predictions, thresholds):
        filtered_predictions = []
        for prediction in predictions:
            filtered_classes = []
            for pred_class in prediction['predictions']:
                class_name = pred_class['class']
                probability = pred_class['probability']
                threshold = thresholds.get(class_name,
                                           0.5)  # Пороговое значение по умолчанию, если класс отсутствует в словаре
                if probability >= threshold:
                    pred_class['prediction'] = 1
                else:
                    pred_class['prediction'] = 0
                filtered_classes.append(pred_class)
            prediction['predictions'] = filtered_classes
            filtered_predictions.append(prediction)
        return filtered_predictions


def main(image_path, outDataDir):
    result_analysis = {}
    neural_operation = NeuralOperation()
    start_time = time.time()
    results = neural_operation.analyze_xray(image_path)
    for result in results:
        print(f"====  Предсказания по images: {result['images']} ====")
        for clas in result['predictions']:
            result_analysis[clas['class']] = clas['probability']
            print(f"{clas['class']}: {clas['probability']}")
        print(f"==================================================")
        for i in range(len(neural_operation.className)):
            neural_operation.plot_heatmap(result['images'], i, outDataDir)
    end_time = time.time()
    total_processing_time = round(end_time - start_time, 3)
    print(f"==== Общее время выполнения: {total_processing_time} seconds ====")
    return result_analysis

if __name__ == '__main__':
    image_path = 'H:/FLASK/Project_chexnet_v1/test_images/uploaded_image.png'
    outDataDir = HEATMAP_DATA_DIR
    print(main(image_path, outDataDir))

















