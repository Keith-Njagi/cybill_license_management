
from . import ma
from models.license import LicenseModel
from models.application import ApplicationModel



class LicenseSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model =LicenseModel
        load_only = ('application',)
        dump_only = ('id', 'created', 'updated',)
        include_fk = True

    _links = ma.Hyperlinks({
        'self': ma.URLFor('api.license_license_detail', id='<id>'),
        'collection': ma.URLFor('api.license_license_list')
    })

