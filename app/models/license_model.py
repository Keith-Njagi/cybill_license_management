from datetime import datetime

from . import db, ma
from .software_model import Software

class License(db.Model):
    __tablename__ = 'licenses'
    id = db.Column(db.Integer, primary_key =True)
    application_id = db.Column(db.Integer, db.ForeignKey('applications.id'), nullable=False)
    application = db.relationship('Application', backref=db.backref("licences", single_parent=True, lazy=True))
    key = db.Column(db.String(80), nullable=False)
    status = db.Column(db.String(25), default='available', nullable=False) # available, on_credit, sold
    created = db.Column(db.DateTime, default=datetime.utcnow(), nullable=False)
    updated = db.Column(db.DateTime, onupdate=datetime.utcnow(), nullable=True)

    def insert_record(self):
        db.session.add(self)
        db.session.commit()
        return self

    @classmethod
    def fetch_all(cls):
        return cls.query.order_by(cls.id.asc()).all()

    @classmethod
    def fetch_by_id(cls, id):
        return cls.query.get(id)

    @classmethod
    def fetch_by_application_id(cls, application_id):
        return cls.query.filter_by(application_id=application_id).all()

    @classmethod
    def update_status(cls, id, status=None):
        record = cls.fetch_by_id(id)
        if status:
            record.status = status
        db.session.commit()
        return True

    @classmethod
    def update_license(cls, id, key=None):
        record = cls.fetch_by_id(id)
        if key:
            record.key = key
        db.session.commit()
        return True

    @classmethod
    def delete_by_id(cls, id):
        record = cls.query.filter_by(id=id)
        record.delete()
        db.session.commit()
        return True



class LicenseSchema(ma.Schema):
    class Meta:
        fields = ('id','application_id', 'key', 'status', 'created', 'updated')