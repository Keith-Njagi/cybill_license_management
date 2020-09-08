from . import ma
from models.software import SoftwareModel
from models.application import ApplicationModel
from models.license import LicenseModel
from .license import LicenseSchema

class ApplicationSchema(ma.SQLAlchemyAutoSchema):
    licenses = ma.Nested(LicenseSchema, many=True)
    class Meta:
        model = ApplicationModel
        load_only = ('software',)
        dump_only = ('id', 'created', 'updated',)
        include_fk = True

    _links = ma.Hyperlinks({
        'self': ma.URLFor('api.application_application_detail', id='<id>'),
        'logo': ma.URLFor('api.application_logo_detail', id='<id>'),
        'collection': ma.URLFor('api.application_application_list')
    })




