import os

from werkzeug.utils import secure_filename
from werkzeug.datastructures import FileStorage
from flask import request
from flask_restx import Namespace, Resource, fields
from flask_jwt_extended import jwt_required, get_jwt_claims, get_jwt_identity, jwt_optional

from models.application import ApplicationModel
from models.software import SoftwareModel
from schemas.application import ApplicationSchema
from user_functions.record_user_log import record_user_log
from user_functions.validate_logo import allowed_file

api = Namespace('application', description='Manage Antivirus Applications')

application_schema = ApplicationSchema()
application_schemas = ApplicationSchema(many=True)

upload_parser = api.parser()
upload_parser.add_argument('logo', location='files', type=FileStorage, required=True, help='Application Logo') # location='headers'
upload_parser.add_argument('description', location='form', type=str, required=True, help='Description')
upload_parser.add_argument('download_link', location='form', type=str, required=True, help='Download Link')
upload_parser.add_argument('price', location='form', type=float, required=True, help='Price')
upload_parser.add_argument('software_id', location='form', type=int, required=True, help='Software ID')


logo_parser = api.parser()
logo_parser.add_argument('logo', location='files', type=FileStorage, required=True, help='Application Logo') # location='headers'

application_model = api.model('Application', {
    'description': fields.String(required=True, description='Description'),
    'download_link': fields.String(required=True, description='Download Link'),
    'price': fields.Float(required=True, description='Price')
})

@api.route('')
class ApplicationList(Resource):
    @classmethod
    @jwt_optional
    @api.doc('Get all applications')
    def get(cls):
        '''Get All Applications'''
        try:
            claims = get_jwt_claims()
            if claims:
                if claims['is_admin']:
                    applications = ApplicationModel.fetch_all()
                    if applications:
                        return application_schemas.dump(applications), 200
                    return {'message': 'There are no antivirus applications yet.'}, 404
            applications = ApplicationModel.fetch_all()
            if applications:
                application_list = application_schemas.dump(applications)
                for application in application_list:
                    license_count = len(application['licenses'])
                    application['licenses'] = license_count
                return application_list, 200
            return {'message': 'There are no antivirus applications yet.'}, 404
                
        except Exception as e:
            print('========================================')
            print('Error description: ', e)
            print('========================================')
            return{'message':'Could not retrieve any applications.'}, 500

    @classmethod
    @jwt_required
    @api.expect(upload_parser)
    @api.doc('Post Application')
    def post(cls):
        '''Post Application'''
        try:
            claims = get_jwt_claims()
            if not claims['is_admin']:
                return {'message':'You are not authorised to access this resource!'}, 403

            args = upload_parser.parse_args()
            description = args['description'].title()
            software_id = args['software_id']

            image_file = args.get('logo')  # This is FileStorage instance

            if description == '':
                return {'message':'You never included a description.'}, 400

            software = SoftwareModel.fetch_by_id(id=software_id)
            if software:
                price = args['price']
                download_link = args['download_link']

                if image_file.filename == '':
                    return {'message':'No logo was found.'}, 400
                        
                if image_file and allowed_file(image_file.filename):
                    logo = secure_filename(image_file.filename)
                    image_file.save(os.path.join( 'uploads', logo))

                    new_application = ApplicationModel(logo=logo,description=description, download_link=download_link, price=price, software_id=software_id)
                    new_application.insert_record()

                    # Record this event in user's logs
                    log_method = 'post'
                    log_description = f'Added application <{description}> to software <{software_id}>'
                    authorization = request.headers.get('Authorization')
                    auth_token  = {"Authorization": authorization}
                    record_user_log(auth_token, log_method, log_description)

                    return {'application':description}, 201
                return {'message':'The logo you uploaded is not recognised.'}, 400
            return {'message': 'The specified software does not exist for this application!'}, 400

            
        except Exception as e:
            print('========================================')
            print('Error description: ', e)
            print('========================================')
            return{'message':'Could not submit application.'}, 500
        

@api.route('/<int:id>')
@api.param('id', 'The Application Identifier')
class ApplicationDetail(Resource):
    @classmethod
    @api.doc('Get single application')
    # include the count of application licenses
    def get(cls, id:int):
        '''Get Single Application'''
        try:
            application = ApplicationModel.fetch_by_id(id)
            if application:
                app = application_schema.dump(application)
                license_count = len(app['licenses'])
                app['licenses'] = license_count
                return app, 200
            return {'message': 'This antivirus application does not exist.'}, 404
        except Exception as e:
            print('========================================')
            print('Error description: ', e)
            print('========================================')
            return{'message':'Could not retrieve application.'}, 500
        
    @classmethod
    @jwt_required
    @api.expect(application_model)
    @api.doc('Update Application')
    def put(cls, id:int):
        '''Update Application'''
        try:
            claims = get_jwt_claims()
            if not claims['is_admin']:
                return {'message':'You are not authorised to access this resource!'}, 403

            data = api.payload
            if not data:
                return {'message':'No input data detected!'}, 400

            # description = data['description']
            # download_link = data['download_link']
            # price = data['price']

            application = ApplicationModel.fetch_by_id(id)
            if application:
                ApplicationModel.update_application(id=id, **data) # description=description, download_link=download_link, price=price)

                # Record this event in user's logs
                log_method = 'put'
                log_description = f'Updated application <{id}>'
                authorization = request.headers.get('Authorization')
                auth_token  = {"Authorization": authorization}
                record_user_log(auth_token, log_method, log_description)
                return application_schema.dump(application), 200
            return {'message': 'This record does not exist.'}, 404
        except Exception as e:
            print('========================================')
            print('Error description: ', e)
            print('========================================')
            return{'message':'Could not update application.'}, 500
       
    @classmethod
    @jwt_required
    @api.doc('Delete Application')
    def delete(cls, id:int):
        '''Delete Application'''
        try:
            claims = get_jwt_claims()
            if not claims['is_admin']:
                return {'message':'You are not authorised to access this resource!'}, 403

            application = ApplicationModel.fetch_by_id(id)
            if application:
                ApplicationModel.delete_by_id(id)

                # Record this event in user's logs
                log_method = 'delete'
                log_description = f'Deleted application <{id}>'
                authorization = request.headers.get('Authorization')
                auth_token  = { "Authorization": authorization}
                record_user_log(auth_token, log_method, log_description)
                return {'message': f'Deleted software <{id}>'}, 200
            return {'message':'This record does not exist!'}, 404

        except Exception as e:
            print('========================================')
            print('Error description: ', e)
            print('========================================')
            return{'message':'Could not delete this application.'}, 500

@api.route('/logo/<int:id>')
@api.param('id', 'The Application Identifier')
class LogoDetail(Resource):
    @classmethod
    @jwt_required
    @api.expect(logo_parser)
    @api.doc('Update Logo')
    def put(cls, id:int):
        '''Update Logo'''
        try:
            claims = get_jwt_claims()
            if not claims['is_admin']:
                return {'message':'You are not authorised to access this resource!'}, 403

            args = logo_parser.parse_args()
            image_file = args.get('logo')  # This is FileStorage instance

            application = ApplicationModel.fetch_by_id(id)
            if application:
                if image_file.filename == '':
                    return {'message':'No logo was found.'}, 400
                    
                if image_file and allowed_file(image_file.filename):
                    logo = secure_filename(image_file.filename)
                    image_file.save(os.path.join( 'uploads', logo))

                    ApplicationModel.update_logo(id=id, logo=logo)

                    # Record this event in user's logs
                    log_method = 'put'
                    log_description = f'Updated logo for application <{id}>'
                    authorization = request.headers.get('Authorization')
                    auth_token  = { "Authorization": authorization}
                    record_user_log(auth_token, log_method, log_description)
                    return application_schema.dump(application), 200
                return {'message':'The logo you uploaded is not recognised.'}, 400
            return {'message': 'This record does not exist!'}, 404
        
        except Exception as e:
            print('========================================')
            print('Error description: ', e)
            print('========================================')
            return{'message':'Could not submit software logo.'}, 500

@api.route('/software/<int:software_id>')
@api.param('software_id', 'The Software Identifier')
class SoftwareApplicationList(Resource):
    @classmethod
    @api.doc('Get applications by software')
    def get(cls, software_id:int):
        '''Get Application by software'''
        try:
            applications = ApplicationModel.fetch_by_software_id(software_id)
            if applications:
                application_list = application_schemas.dump(applications)
                for application in application_list:
                    license_count = len(application['licenses'])
                    application['licenses'] = license_count
                return application_list, 200   
            return {'message': 'These records do not exist.'}, 404         
        except Exception as e:
            print('========================================')
            print('Error description: ', e)
            print('========================================')
            return{'message':'Could not retrieve application.'}, 500