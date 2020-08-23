from flask import request
from flask_restx import Namespace, Resource, fields
from flask_jwt_extended import jwt_required, get_jwt_claims, get_jwt_identity

from models.application_model import Application, ApplicationSchema
from models.license_model import License, LicenseSchema
from user_functions.record_user_log import record_user_log

api = Namespace('license', description='Manage Application Licenses')

license_schema = LicenseSchema()
license_schemas = LicenseSchema(many=True)
application_schema = ApplicationSchema()
application_schemas = ApplicationSchema(many=True)

license_model = api.model('License', {
    'application_id': fields.Integer(required=True, description='Application ID'),
    'key': fields.String(required=True, description='License Key')
})

# ''
# get all licenses - Admin
# post new license - Admin
@api.route('')
class LicenseList(Resource):
    @api.doc('Get all licenses')
    @jwt_required
    def get(self):
        '''Get All Licenses'''
        try:
            pass
        except Exception as e:
            print('========================================')
            print('Error description: ', e)
            print('========================================')
            return{'message':'Could not fetch licenses.'}, 500

    @api.doc('Post License')
    @api.expect(license_model)
    @jwt_required
    def post(self):
        '''Post License'''
        try:
            pass
        except Exception as e:
            print('========================================')
            print('Error description: ', e)
            print('========================================')
            return{'message':'Could not fetch licenses.'}, 500
        


# '<int:id>'
# get single license - jwt_required(if sales.user_id = authorised_user['id']) or claims = Admin
# delete - claims- Admin
@api.route('/<int:id>')
@api.param('id', 'The license identifier')
class LicenseOperations(Resource):
    @api.doc('Delete license key')
    @jwt_required
    def delete(self, id):
        '''Delete license key'''
        try:
            pass
        except Exception as e:
            print('========================================')
            print('Error description: ', e)
            print('========================================')
            return{'message':'Could not delete license.'}, 500

# '/credit/<int:id>'
# put on credit - claims - Admin
@api.route('/credit/<int:id>')
@api.param('id', 'The license identifier')
class LicenseOperations(Resource):
    @api.doc('Update status to on credit')
    @jwt_required
    def put(self, id):
        '''Update status to on credit'''
        try:
            pass
        except Exception as e:
            print('========================================')
            print('Error description: ', e)
            print('========================================')
            return{'message':'Could not update license status.'}, 500

# '/sell/<int:id>'
# put as sold - jwt_required(if sales.user_id = authorised_user['id'])
@api.route('/credit/<int:id>')
@api.param('id', 'The license identifier')
class LicenseOperations(Resource):
    @api.doc('Update status to sold')
    @jwt_required
    def put(self, id):
        '''Update status to sold'''
        try:
            pass
        except Exception as e:
            print('========================================')
            print('Error description: ', e)
            print('========================================')
            return{'message':'Could not update license status.'}, 500

# '/avail/<int:id>'
# put as available - claims- Admin (only if license is not in sales.license_id)
@api.route('/credit/<int:id>')
@api.param('id', 'The license identifier')
class LicenseOperations(Resource):
    @api.doc('Update status to avaliable')
    @jwt_required
    def put(self, id):
        '''Update status to available'''
        try:
            pass
        except Exception as e:
            print('========================================')
            print('Error description: ', e)
            print('========================================')
            return{'message':'Could not update license status.'}, 500