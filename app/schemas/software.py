from . import ma
from models.software import SoftwareModel
from models.application import ApplicationModel
from .application import ApplicationSchema

class SoftwareSchema(ma.SQLAlchemyAutoSchema):
    applications = ma.Nested(ApplicationSchema, many=True)
    class Meta:
        model = SoftwareModel
        dump_only = ('id', 'created', 'updated',)
        include_fk = True

    _links = ma.Hyperlinks({
        'self': ma.URLFor('api.software_software_detail', id='<id>'),
        'logo': ma.URLFor('api.software_logo_detail', id='<id>'),
        'collection': ma.URLFor('api.software_software_list')
    })
