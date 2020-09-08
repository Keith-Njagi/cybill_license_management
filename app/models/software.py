from datetime import datetime
from typing import List

from . import db

class SoftwareModel(db.Model):
    __tablename__ = 'software'
    id = db.Column(db.Integer, primary_key =True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    logo = db.Column(db.String(80), nullable=False)
    created = db.Column(db.DateTime, default=datetime.utcnow(), nullable=False)
    updated = db.Column(db.DateTime, onupdate=datetime.utcnow(), nullable=True)

    applications = db.relationship('ApplicationModel', lazy='dynamic')

    def insert_record(self) -> None:
        db.session.add(self)
        db.session.commit()      

    @classmethod
    def fetch_all(cls) -> List['SoftwareModel']:
        return cls.query.order_by(cls.id.asc()).all()

    @classmethod
    def fetch_by_id(cls, id:int) -> 'SoftwareModel':
        return cls.query.get(id)

    @classmethod
    def fetch_by_name(cls, name:str) -> 'SoftwareModel':
        return cls.query.filter_by(name=name).first()

    @classmethod
    def update_name(cls, id:int, name:str=None, logo:str=None) -> None:
        record = cls.fetch_by_id(id)
        if name:
            record.name = name
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
        
