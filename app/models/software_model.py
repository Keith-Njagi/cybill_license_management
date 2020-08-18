from datetime import datetime

from . import db, ma

class Software(db.Model):
    __tablename__ = 'software'
    id = db.Column(db.Integer, primary_key =True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    logo = db.Column(db.String(80), nullable=False)
    # status = db.Column(db.String(25), nullable=False)
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
    def fetch_by_name(cls, name):
        return cls.query.filter_by(name=name).first()

    @classmethod
    def update_software(cls, id, name=None, logo=None):
        record = cls.fetch_by_id(id)
        if name:
            record.name = name
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


class SoftwareSchema(ma.Schema):
    class Meta:
        fields = ('id', 'name', 'logo', 'created', 'updated')