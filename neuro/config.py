CKPT_PATH = 'm-25012018-123527.pth.tar'
N_CLASSES = 14
CLASS_NAMES = ['Atelectasis', 'Cardiomegaly', 'Effusion', 'Infiltration', 'Mass', 'Nodule', 'Pneumonia',
               'Pneumothorax', 'Consolidation', 'Edema', 'Emphysema', 'Fibrosis', 'Pleural_Thickening', 'Hernia']
RU_CLASS_NAMES = ['Ателектаз', 'Кардиомегалия', 'Излияние', 'Проникновение', 'Масса', 'Узелок', 'Пневмония',
               'Пневмоторакс', 'Укрепление', 'Отек', 'Эмфизема', 'Фиброз', 'Плевральное_утолщение', 'Грыжа']
DATA_DIR =        './ChestX-ray14/images/images'
WORK_DATA_DIR =        './test_images/'
OVERLAID_IMAGE_DATA_DIR =        './ChestX-ray14/images/overlaid/'
HEATMAP_DATA_DIR ='H:/FLASK/Project_chexnet_v1/test_images/heatmaps'
DICOM_DATA_DIR = './ChestX-ray14/images/images_dicom'
TEST_IMAGE_LIST = './ChestX-ray14/labels/test_list.txt'
BATCH_SIZE = 1
# calculated using frequentist approach
# based on prevalance of label throughout the dataset
label_baseline_probs = {
    'Atelectasis': 0.103,
    'Cardiomegaly': 0.025,
    'Effusion': 0.119,
    'Infiltration': 0.177,
    'Mass': 0.051,
    'Nodule': 0.056,
    'Pneumonia': 0.012,
    'Pneumothorax': 0.047,
    'Consolidation': 0.042,
    'Edema': 0.021,
    'Emphysema': 0.022,
    'Fibrosis': 0.015,
    'Pleural_Thickening': 0.03,
    'Hernia': 0.002
}
TEST_MOD = True
WORK_MOD = False
WORK2_MOD = False

MODEL_PATH = './neuro/model.pth.tar'
TRANS_CROP = 224