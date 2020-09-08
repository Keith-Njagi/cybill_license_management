from datetime import datetime
from typing import List

from . import db

class ApplicationModel(db.Model):
    __tablename__ = 'applications'
    id = db.Column(db.Integer, primary_key =True)
    software_id = db.Column(db.Integer, db.ForeignKey('software.id'), nullable=False)
    software = db.relationship('SoftwareModel')
    description = db.Column(db.String, nullable=False)
    logo = db.Column(db.String(80), nullable=False)
    price = db.Column(db.Float(precision=2), nullable=False)
    download_link = db.Column(db.String, nullable=False)
    created = db.Column(db.DateTime, default=datetime.utcnow(), nullable=False)
    updated = db.Column(db.DateTime, onupdate=datetime.utcnow(), nullable=True)

    licenses = db.relationship('LicenseModel', lazy='dynamic')

    def insert_record(self) -> None:
        db.session.add(self)
        db.session.commit()

    @classmethod
    def fetch_all(cls) -> List['ApplicationModel']:
        return cls.query.order_by(cls.id.asc()).all()

    @classmethod
    def fetch_by_software_id(cls, software_id:int) -> List['ApplicationModel']:
        return cls.query.filter_by(software_id=software_id).all()

    @classmethod
    def fetch_by_id(cls, id:int) -> 'ApplicationModel':
        return cls.query.get(id)

    @classmethod
    def update_application(cls, id:int, description:str=None, price:float=None, download_link:str=None) -> None:
        record = cls.fetch_by_id(id)
        if description:
            record.description = description
        if price:
            record.price = price
        if download_link:
            record.download_link = download_link
        db.session.commit()

    @classmethod
    def update_logo(cls, id:int, logo:str=None) -> None:
        record = cls.fetch_by_id(id)
        if logo:
            record.logo = logo
        db.session.commit()

    @classmethod
    def delete_by_id(cls, id:int) -> None:
        record = cls.query.filter_by(id=id)
        record.delete()
        db.session.commit()



