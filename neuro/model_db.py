from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class OriginalImage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.String(50), nullable=False)
    study_id = db.Column(db.String(50))
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


