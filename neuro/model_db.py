
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class OriginalImage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    query_id = db.Column(db.String)
    study_instance_uid = db.Column(db.String(255))
    image = db.Column(db.LargeBinary, nullable=False)
class AnalysisResult(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.String(50), nullable=False)
    original_images = db.Column(db.LargeBinary, nullable=False)
    atelectasis = db.Column(db.LargeBinary)
    cardiomegaly = db.Column(db.LargeBinary)
    effusion = db.Column(db.LargeBinary)
    infiltration = db.Column(db.LargeBinary)
    mass = db.Column(db.LargeBinary)
    nodule = db.Column(db.LargeBinary)
    pneumonia = db.Column(db.LargeBinary)
    pneumothorax = db.Column(db.LargeBinary)
    consolidation = db.Column(db.LargeBinary)
    edema = db.Column(db.LargeBinary)
    emphysema = db.Column(db.LargeBinary)
    fibrosis = db.Column(db.LargeBinary)
    pleural_thickening = db.Column(db.LargeBinary)
    hernia = db.Column(db.LargeBinary)

    def __init__(self, patient_id, original_images):
        self.patient_id = patient_id
        self.original_images = original_images
class SearchResult(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    query_id = db.Column(db.String)
    study_date = db.Column(db.String(8))
    patient_name = db.Column(db.String(255))
    patient_birth = db.Column(db.String(8))
    study_instance_uid = db.Column(db.String(255))




