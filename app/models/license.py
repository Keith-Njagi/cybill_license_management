from datetime import datetime
from typing import List

from . import db

class LicenseModel(db.Model):
    __tablename__ = 'licenses'
    id = db.Column(db.Integer, primary_key =True)
    license_key = db.Column(db.String(80), nullable=False)
    license_status = db.Column(db.String(25), default='available', nullable=False) # available, on_credit, sold
    application_id = db.Column(db.Integer, db.ForeignKey('applications.id'), nullable=False)
    application = db.relationship('ApplicationModel')
    created = db.Column(db.DateTime, default=datetime.utcnow(), nullable=False)
    updated = db.Column(db.DateTime, onupdate=datetime.utcnow(), nullable=True)

    def insert_record(self) -> None:
        db.session.add(self)
        db.session.commit()

    @classmethod
    def fetch_all(cls) -> List['LicenseModel']:
        return cls.query.order_by(cls.id.asc()).all()

    @classmethod
    def fetch_by_application_id(cls, application_id:int) -> List['LicenseModel']:
        return cls.query.filter_by(application_id=application_id).all()

    @classmethod
    def fetch_by_id(cls, id:int) -> 'LicenseModel':
        return cls.query.get(id)

    @classmethod
    def update_status(cls, id:int, license_status:str=None) -> None:
        record = cls.fetch_by_id(id)
        if license_status:
            record.license_status = license_status
        db.session.commit()

    @classmethod
    def update_license(cls, id:int, license_key:str=None) -> None:
        record = cls.fetch_by_id(id)
        if license_key:
            record.license_key = license_key
        db.session.commit()

    @classmethod
    def delete_by_id(cls, id:int) -> None:
        record = cls.query.filter_by(id=id)
        record.delete()
        db.session.commit()
