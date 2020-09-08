import requests
from flask import request
from flask_restx import Namespace, Resource, fields
from flask_jwt_extended import jwt_required, get_jwt_claims, get_jwt_identity

from models.application import ApplicationModel
from models.license import LicenseModel 
from schemas.license import LicenseSchema
from user_functions.record_user_log import record_user_log

api = Namespace('license', description='Manage Application Licenses')

license_schema = LicenseSchema()
license_schemas = LicenseSchema(many=True)

license_model = api.model('License', {
    'application_id': fields.Integer(required=True, description='Application ID'),
    'license_key': fields.String(required=True, description='License Key')
})
update_license_model = api.model('LicenseKey', {
    'license_key': fields.String(required=True, description='License Key')
})

# ''
# get all licenses - Admin
# post new license - Admin
@api.route('')
class LicenseList(Resource):
    @classmethod
    @api.doc('Get all licenses')
    @jwt_required
    def get(cls):
        '''Get All Licenses'''
        try:
            claims = get_jwt_claims()
            if not claims['is_admin']:
                return {'message': 'You are not authorised to use this resource'}, 403

            licenses = LicenseModel.fetch_all()
            if licenses:
                # Record this event in user's logs
                log_method = 'get'
                log_description = 'Fetched all licenses'
                authorization = request.headers.get('Authorization')
                auth_token  = {"Authorization": authorization}
                record_user_log(auth_token, log_method, log_description)
                return license_schemas.dump(licenses), 200
            return {'message': 'There are no licenses yet.'}, 404            
        except Exception as e:
            print('========================================')
            print('Error description: ', e)
            print('========================================')
            return{'message':'Could not fetch licenses.'}, 500

    @classmethod
    @api.doc('Post License')
    @api.expect(license_model)
    @jwt_required
    def post(cls):
        '''Post License'''
        try:
            claims = get_jwt_claims()
            if not claims['is_admin']:
                return {'message': 'You are not authorised to use this resource'}, 403

            data = api.payload
            if not data:
                return {'message': 'No input data detected'}, 400

            application_id = data['application_id']
            license_key = data['license_key']

            if license_key == '':
                return {'message': 'You have not specified any key.'}, 400

            application = ApplicationModel.fetch_by_id(id=application_id)
            if application:
                new_license = LicenseModel(application_id=application_id, license_key=license_key)
                new_license.insert_record()

                # Record this event in user's logs
                log_method = 'post'
                log_description = f'Added license to application <{application_id}>'
                authorization = request.headers.get('Authorization')
                auth_token  = {"Authorization": authorization}
                record_user_log(auth_token, log_method, log_description)

                return {'message': 'Successfully added license'}, 201
            return {'message': 'The specified application does not exist.'}, 400
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
class LicenseDetail(Resource): # enable user who has bought the license to get
    @classmethod
    @api.doc('Get single license key')
    @jwt_required
    def get(cls, id:int):
        '''Get single license key'''
        claims = get_jwt_claims()
        authorised_user = get_jwt_identity()
        try:

            # Check if user is authorised to use this route
            # Either if the user is an admin
            # or the user is a salesman credited to this license key
            # or if the user has already purchased this license
            authorization = request.headers.get('Authorization')
            auth_token  = {"Authorization": authorization}
            
            # sales_url = f'http://172.18.0.1:3104/api/license_sale/license/{id}
            # req = requests.get(sales_url, headers=auth_token)
            # if req.status_code == 200 or claims['is_admin']:

            #     Paste all the code below here

            # return {'message': 'You are not authorised to use this resource.'}, 403

            license_key = LicenseModel.fetch_by_id(id)
            if license_key:
                license_item = license_schema.dump(license_key)

                price = license_key.application.price
                license_item['price'] = price

                # Record this event in user's logs
                log_method = 'get'
                log_description = f'Fetched license <{id}>'
                record_user_log(auth_token, log_method, log_description)
                return license_item, 200
            return {'message':'This license does not exist.'}, 404
        except Exception as e:
            print('========================================')
            print('Error description: ', e)
            print('========================================')
            return{'message':'Could not fetch license.'}, 500

    @classmethod
    @api.doc('Update license key')
    @jwt_required
    @api.expect(update_license_model)
    def put(cls, id:int):
        '''Update license key'''
        try:
            claims = get_jwt_claims()
            if not claims['is_admin']:
                return {'message': 'You are not authorised to use this resource'}, 403

            data = api.payload
            if not data:
                return {'message': 'No input data detected'}, 400

            license_key = data['license_key']

            if license_key == '':
                return {'message': 'You have not specified any key.'}, 400

            license_key = LicenseModel.fetch_by_id(id)
            if license_key:
                LicenseModel.update_license(id, license_key=license_key)

                # Record this event in user's logs
                log_method = 'put'
                log_description = f'Updated license <{id}>'
                authorization = request.headers.get('Authorization')
                auth_token  = {"Authorization": authorization}
                record_user_log(auth_token, log_method, log_description)

                return license_schema.dump(license_key), 200
            return {'message': 'This license does not exist.'}, 404
        except Exception as e:
            print('========================================')
            print('Error description: ', e)
            print('========================================')
            return{'message':'Could not update license.'}, 500

    @classmethod
    @api.doc('Delete license key')
    @jwt_required
    def delete(cls, id:int):
        '''Delete license key'''
        try:
            claims = get_jwt_claims()
            if not claims['is_admin']:
                return {'message': 'You are not authorised to use this resource'}, 403

            license_key = LicenseModel.fetch_by_id(id)
            if license_key:
                LicenseModel.delete_by_id(id)

                # Record this event in user's logs
                log_method = 'delete'
                log_description = f'Deleted license <{id}>'
                authorization = request.headers.get('Authorization')
                auth_token  = {"Authorization": authorization}
                record_user_log(auth_token, log_method, log_description)

                return {'message': f'Deleted license <{id}>'}, 200
            return {'message': 'This license does not exist.'}, 404
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
    @classmethod
    @api.doc('Get licenses by application')
    @jwt_required
    def get(cls, application_id:int):
        '''Get licenses by application'''
        claims = get_jwt_claims()
        if not claims['is_admin']:
            return {'message': 'You are not authorised to use this resource.'}, 403

        try:
            licenses = LicenseModel.fetch_by_application_id(application_id)
            if licenses:
                # Record this event in user's logs
                log_method = 'get'
                log_description = f'Fetched licenses by application <{application_id}>'
                authorization = request.headers.get('Authorization')
                auth_token  = {"Authorization": authorization}
                record_user_log(auth_token, log_method, log_description)

                return license_schemas.dump(licenses), 200
            return {'message':'There are no licenses under this application.'}, 404
        except Exception as e:
            print('========================================')
            print('Error description: ', e)
            print('========================================')
            return{'message':'Could not fetch licenses.'}, 500


# '/credit/<int:id>'
# put on credit - claims - Admin
@api.route('/credit/<int:id>')
@api.param('id', 'The license identifier')
class CreditLicense(Resource):
    @classmethod
    @api.doc('Update status to on credit')
    @jwt_required
    def put(cls, id:int):
        '''Update status to on credit'''
        try:
            claims = get_jwt_claims()
            if not claims['is_admin']:
                return {'message': 'You are not authorised to use this resource'}, 403

            license_key = LicenseModel.fetch_by_id(id)
            if license_key:
                status = 'on_credit'
                LicenseModel.update_status(id, status=status)

                # Record this event in user's logs
                log_method = 'put'
                log_description = f'Updated license <{id}> to on credit'
                authorization = request.headers.get('Authorization')
                auth_token  = {"Authorization": authorization}
                record_user_log(auth_token, log_method, log_description)

                return license_schema.dump(license_key), 200
            return {'message': 'This record does not exist.'}, 404           
        except Exception as e:
            print('========================================')
            print('Error description: ', e)
            print('========================================')
            return{'message':'Could not update license status.'}, 500

# '/sell/<int:id>'
# put as sold - jwt_required(if sales.user_id = authorised_user['id'])
@api.route('/sell/<int:id>')
@api.param('id', 'The license identifier')
class SellLicense(Resource):
    @classmethod
    @api.doc('Update status to sold')
    @jwt_required
    def put(cls, id:int):
        '''Update status to sold'''
        try:

            license_key = LicenseModel.fetch_by_id(id)
            if license_key:
                status = 'sold'
                LicenseModel.update_status(id, status=status)

                # Record this event in user's logs
                log_method = 'put'
                log_description = f'Updated license <{id}> to sold'
                authorization = request.headers.get('Authorization')
                auth_token  = {"Authorization": authorization}
                record_user_log(auth_token, log_method, log_description)

                return license_schema.dump(license_key), 200
            return {'message': 'This record does not exist.'}, 404           
        except Exception as e:
            print('========================================')
            print('Error description: ', e)
            print('========================================')
            return{'message':'Could not update license status.'}, 500

# '/avail/<int:id>'
# put as available - claims- Admin (only if license is not in sales.license_id)
@api.route('/avail/<int:id>')
@api.param('id', 'The license identifier')
class AvailLicense(Resource):
    @classmethod
    @api.doc('Update status to avaliable')
    @jwt_required
    def put(cls, id:int):
        '''Update status to available'''
        try:
            claims = get_jwt_claims()
            if not claims['is_admin']:
                return {'message': 'You are not authorised to use this resource'}, 403

            license_key = LicenseModel.fetch_by_id(id)
            if license_key:
                status = 'available'
                LicenseModel.update_status(id, status=status)
                
                # Record this event in user's logs
                log_method = 'put'
                log_description = f'Updated license <{id}> to available'
                authorization = request.headers.get('Authorization')
                auth_token  = {"Authorization": authorization}
                record_user_log(auth_token, log_method, log_description)

                return license_schema.dump(license_key), 200
            return {'message': 'This record does not exist.'}, 404            
        except Exception as e:
            print('========================================')
            print('Error description: ', e)
            print('========================================')
            return{'message':'Could not update license status.'}, 500