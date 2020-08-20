from datetime import datetime

from . import db, ma
from .software_model import Software

class Application(db.Model):
    __tablename__ = 'applications'
    id = db.Column(db.Integer, primary_key =True)
    # name = db.Column(db.String(80), nullable=False)
    software_id = db.Column(db.Integer, db.ForeignKey('software.id'), nullable=False)
    software = db.relationship('Software', backref=db.backref("applications", single_parent=True, lazy=True))
    description = db.Column(db.String, nullable=False)
    logo = db.Column(db.String(80), nullable=False)
    price = db.Column(db.Float(precision=2), nullable=False)
    download_link = = db.Column(db.String, nullable=False)
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
    def fetch_by_software_id(cls, software_id):
        return cls.query.filter_by(software_id=software_id).all()

    @classmethod
    def update_application(cls, id, description=None, price=None, download_link=None):
        record = cls.fetch_by_id(id)
        if description:
            record.description = description
        if price:
            record.price = price
        if download_link:
            record.download_link = download_link
        db.session.commit()
        return True

    @classmethod
    def update_logo(cls, id, logo=None):
        record = cls.fetch_by_id(id)
        if logo:
            record.logo = logo
        db.session.commit()
        return True

    @classmethod
    def delete_by_id(cls, id):
        record = cls.query.filter_by(id=id)
        record.delete()
        db.session.commit()
        return True



class ApplicationSchema(ma.Schema):
    class Meta:
        fields = ('id','software_id', 'description', 'logo', 'price', 'download_link', 'created', 'updated')