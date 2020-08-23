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
update_license_model = api.model('LicenseKey', {
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
            claims = get_jwt_claims()
            if not claims['is_admin']:
                return {'message': 'You are not authorised to use this resource'}, 403

            db_licenses = Licence.fetch_all()
            licenses = license_schemas.dump(db_licenses)
            if len(licenses) == 0:
                return {'message': 'There are no licences yet.'}, 404

            # Record this event in user's logs
            log_method = 'get'
            log_description = 'Fetched all licenses'
            authorization = request.headers.get('Authorization')
            auth_token  = {"Authorization": authorization}
            record_user_log(auth_token, log_method, log_description)
            return {'licenses':licenses}, 200
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
            claims = get_jwt_claims()
            if not claims['is_admin']:
                return {'message': 'You are not authorised to use this resource'}, 403

            data = api.payload
            if not data:
                return {'message': 'No input data detected'}, 400

            application_id = data['application_id']
            key = data['key']

            if key == '':
                return {'message': 'You have not specified any key.'}, 400

            db_application = Application.fetch_by_id(id=application_id)
            application = application_schema.dump(db_application)
            if len(application) == 0:
                return {'message': 'The specified application does not exist.'}, 400

            new_license = License(application_id=application_id, key=key)
            new_license.insert_record()

            # Record this event in user's logs
            log_method = 'post'
            log_description = f'Added license to application <{application_id}>'
            authorization = request.headers.get('Authorization')
            auth_token  = {"Authorization": authorization}
            record_user_log(auth_token, log_method, log_description)

            return {'message': 'Successfully added license'}, 201
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
    @api.doc('Get single license key')
    @jwt_required
    def get(seld, id):
        '''Get single license key'''
        claims = get_jwt_claims()
        if not claims['is_admin']:
            return {'message': 'You are not authorised to use this resource.'}, 403

        try:
            db_license = License.fetch_by_id(id)
            license_key = license_schema.dump(db_license)

            if len(license_key) == 0:
                return {'message':'This license does not exist.'}, 404

            # Record this event in user's logs
            log_method = 'get'
            log_description = f'Fetched license <{id}>'
            authorization = request.headers.get('Authorization')
            auth_token  = {"Authorization": authorization}
            record_user_log(auth_token, log_method, log_description)

            return {'licenses':license_key}, 200
        except Exception as e:
            print('========================================')
            print('Error description: ', e)
            print('========================================')
            return{'message':'Could not fetch license.'}, 500

    @api.doc('Update license key')
    @jwt_required
    @api.expect(update_license_model)
    def put(self, id):
        '''Update license key'''
        try:
            claims = get_jwt_claims()
            if not claims['is_admin']:
                return {'message': 'You are not authorised to use this resource'}, 403

            data = api.payload
            if not data:
                return {'message': 'No input data detected'}, 400

            key = data['key']

            if key == '':
                return {'message': 'You have not specified any key.'}, 400

            this_license = License.fetch_by_id(id)
            license_key = license_schema.dump(this_license)
            if len(license_key) == 0:
                return {'message': 'This license does not exist.'}, 404

            License.update_license(id, key=key)

            db_license = License.fetch_by_id(id)
            license_key = license_schema.dump(db_license)

            # Record this event in user's logs
            log_method = 'put'
            log_description = f'Updated license <{id}>'
            authorization = request.headers.get('Authorization')
            auth_token  = {"Authorization": authorization}
            record_user_log(auth_token, log_method, log_description)

            return {'license': license_key}, 200

        except Exception as e:
            print('========================================')
            print('Error description: ', e)
            print('========================================')
            return{'message':'Could not update license.'}, 500

    @api.doc('Delete license key')
    @jwt_required
    def delete(self, id):
        '''Delete license key'''
        try:
            claims = get_jwt_claims()
            if not claims['is_admin']:
                return {'message': 'You are not authorised to use this resource'}, 403

            this_license = License.fetch_by_id(id)
            license_key = license_schema.dump(this_license)
            if len(license_key) == 0:
                return {'message': 'This license does not exist.'}, 404

            License.delete_by_id(id)

            # Record this event in user's logs
            log_method = 'delete'
            log_description = f'Deleted license <{id}>'
            authorization = request.headers.get('Authorization')
            auth_token  = {"Authorization": authorization}
            record_user_log(auth_token, log_method, log_description)

            return {'message': f'Deleted license <{id}>'}, 200

        except Exception as e:
            print('========================================')
            print('Error description: ', e)
            print('========================================')
            return{'message':'Could not delete license.'}, 500

# '/application/<int:application_id>'
# get licenses by application
@api.route('/application/<int:application_id>')
@api.param('application_id', 'The application identifier')
class ApplicationLicenses(Resource):
    @api.doc('Get licenses by application')
    @jwt_required
    def get(self, application_id):
        '''Get licenses by application'''
        claims = get_jwt_claims()
        if not claims['is_admin']:
            return {'message': 'You are not authorised to use this resource.'}, 403

        try:
            db_licenses = License.fetch_by_application_id(application_id)
            licenses = license_schemas.dump(db_licenses)

            if len(licenses) == 0:
                return {'message':'There are no licenses under this application.'}, 404

            # Record this event in user's logs
            log_method = 'get'
            log_description = f'Fetched licenses by application <{application_id}>'
            authorization = request.headers.get('Authorization')
            auth_token  = {"Authorization": authorization}
            record_user_log(auth_token, log_method, log_description)

            return {'licenses':licenses}, 200
        except Exception as e:
            print('========================================')
            print('Error description: ', e)
            print('========================================')
            return{'message':'Could not fetch licenses.'}, 500


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
            claims = get_jwt_claims()
            if not claims['is_admin']:
                return {'message': 'You are not authorised to use this resource'}, 403

            my_license = License.fetch_by_id(id)
            this_license = license_schema.dump(my_license)
            if len(this_license) == 0:
                return {'message': 'This record does not exist.'}, 404

            status = 'on_credit'
            License.update_status(id, status=status)

            db_license = License.fetch_by_id(id)
            license_key = license_schema.dump(db_license)

            # Record this event in user's logs
            log_method = 'put'
            log_description = f'Updated license <{id}> to on credit'
            authorization = request.headers.get('Authorization')
            auth_token  = {"Authorization": authorization}
            record_user_log(auth_token, log_method, log_description)
            return {'license':license_key}, 200
        except Exception as e:
            print('========================================')
            print('Error description: ', e)
            print('========================================')
            return{'message':'Could not update license status.'}, 500

# '/sell/<int:id>'
# put as sold - jwt_required(if sales.user_id = authorised_user['id'])
@api.route('/sell/<int:id>')
@api.param('id', 'The license identifier')
class LicenseOperations(Resource):
    @api.doc('Update status to sold')
    @jwt_required
    def put(self, id):
        '''Update status to sold'''
        try:

            my_license = License.fetch_by_id(id)
            this_license = license_schema.dump(my_license)
            if len(this_license) == 0:
                return {'message': 'This record does not exist.'}, 404

            status = 'sold'
            License.update_status(id, status=status)

            db_license = License.fetch_by_id(id)
            license_key = license_schema.dump(db_license)

            # Record this event in user's logs
            log_method = 'put'
            log_description = f'Updated license <{id}> to sold'
            authorization = request.headers.get('Authorization')
            auth_token  = {"Authorization": authorization}
            record_user_log(auth_token, log_method, log_description)
            return {'license':license_key}, 200
        except Exception as e:
            print('========================================')
            print('Error description: ', e)
            print('========================================')
            return{'message':'Could not update license status.'}, 500

# '/avail/<int:id>'
# put as available - claims- Admin (only if license is not in sales.license_id)
@api.route('/avail/<int:id>')
@api.param('id', 'The license identifier')
class LicenseOperations(Resource):
    @api.doc('Update status to avaliable')
    @jwt_required
    def put(self, id):
        '''Update status to available'''
        try:
            claims = get_jwt_claims()
            if not claims['is_admin']:
                return {'message': 'You are not authorised to use this resource'}, 403

            my_license = License.fetch_by_id(id)
            this_license = license_schema.dump(my_license)
            if len(this_license) == 0:
                return {'message': 'This record does not exist.'}, 404

            status = 'available'
            License.update_status(id, status=status)

            db_license = License.fetch_by_id(id)
            license_key = license_schema.dump(db_license)

            # Record this event in user's logs
            log_method = 'put'
            log_description = f'Updated license <{id}> to available'
            authorization = request.headers.get('Authorization')
            auth_token  = {"Authorization": authorization}
            record_user_log(auth_token, log_method, log_description)
            return {'license':license_key}, 200
        except Exception as e:
            print('========================================')
            print('Error description: ', e)
            print('========================================')
            return{'message':'Could not update license status.'}, 500