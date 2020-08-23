import os

from werkzeug.utils import secure_filename
from werkzeug.datastructures import FileStorage
from flask import request
from flask_restx import Namespace, Resource, fields
from flask_jwt_extended import jwt_required, get_jwt_claims, get_jwt_identity

from models.application_model import Application, ApplicationSchema
from models.software_model import Software, SoftwareSchema
from models.license_model import License, LicenseSchema
from user_functions.record_user_log import record_user_log
from user_functions.validate_logo import allowed_file

api = Namespace('application', description='Manage Antivirus Applications')

software_schema = SoftwareSchema()
software_schemas = SoftwareSchema(many=True)
application_schema = ApplicationSchema()
application_schemas = ApplicationSchema(many=True)
license_schemas = LicenseSchema(many=True)

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
    @api.doc('Get all applications')
    def get(self):
        '''Get All Applications'''
        try:
            db_application = Application.fetch_all()
            applications = application_schemas.dump(db_application)
            if len(applications) == 0:
                return {'message': 'There are no antivirus applications yet.'}, 404
            return {'applications':applications}, 200
        except Exception as e:
            print('========================================')
            print('Error description: ', e)
            print('========================================')
            return{'message':'Could not retrieve any applications.'}, 500

    @jwt_required
    @api.expect(upload_parser)
    @api.doc('Post Application')
    def post(self):
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

            this_software = Software.fetch_by_id(id=software_id)
            software = software_schema.dump(this_software)
            if len(software) == 0:
                return {'message': 'The specified software does not exist for this application!'}, 400

            price = args['price']
            download_link = args['download_link']

            if image_file.filename == '':
                return {'message':'No logo was found.'}, 400
                    
            if image_file and allowed_file(image_file.filename):
                logo = secure_filename(image_file.filename)
                image_file.save(os.path.join( 'uploads', logo))
                new_application = Application(logo=logo,description=description, download_link=download_link, price=price, software_id=software_id)
                new_application.insert_record()

                # Record this event in user's logs
                log_method = 'post'
                log_description = f'Added application <{description}> to software <{software_id}>'
                authorization = request.headers.get('Authorization')
                auth_token  = {"Authorization": authorization}
                record_user_log(auth_token, log_method, log_description)

                return {'software': software, 'application':description}, 201
            return {'message':'The logo you uploaded is not recognised.'}, 400
        except Exception as e:
            print('========================================')
            print('Error description: ', e)
            print('========================================')
            return{'message':'Could not submit application.'}, 500
        

@api.route('/<int:id>')
@api.param('id', 'The Application Identifier')
class ApplicationList(Resource):
    @api.doc('Get single application')
    # include the count of application licenses
    def get(self, id):
        '''Get Single Application'''
        try:
            db_application = Application.fetch_by_id(id)
            application = application_schema.dump(db_application)

            db_licenses = License.fetch_by_application_id(application_id=id)
            licenses = license_schemas.dump(db_licenses)
            license_count = len(licenses)

            if len(application) == 0:
                return {'message': 'This antivirus application does not exist.'}, 404
            return {'application':application, 'licenses':license_count}, 200
        except Exception as e:
            print('========================================')
            print('Error description: ', e)
            print('========================================')
            return{'message':'Could not retrieve application.'}, 500
        

    @jwt_required
    @api.expect(application_model)
    @api.doc('Update Application')
    def put(self, id):
        '''Update Application'''
        try:
            claims = get_jwt_claims()
            if not claims['is_admin']:
                return {'message':'You are not authorised to access this resource!'}, 403

            data = api.payload
            if not data:
                return {'message':'No input data detected!'}, 400

            description = data['description']
            download_link = data['download_link']
            price = data['price']

            db_application = Application.fetch_by_id(id)
            application = application_schema.dump(db_application)
            if len(application) == 0:
                return {'message': 'This record does not exist.'}, 404

            Application.update_application(id=id, description=description, download_link=download_link, price=price)

            # Record this event in user's logs
            log_method = 'put'
            log_description = f'Updated application <{id}>'
            authorization = request.headers.get('Authorization')
            auth_token  = {"Authorization": authorization}
            record_user_log(auth_token, log_method, log_description)
            return {'application':description}, 200
        except Exception as e:
            print('========================================')
            print('Error description: ', e)
            print('========================================')
            return{'message':'Could not update application.'}, 500
       

    @jwt_required
    @api.doc('Delete Application')
    def delete(self, id):
        '''Delete Application'''
        try:
            claims = get_jwt_claims()
            if not claims['is_admin']:
                return {'message':'You are not authorised to access this resource!'}, 403

            my_application = Application.fetch_by_id(id)
            application = application_schema.dump(my_application)
            if len(application) == 0:
                return {'message':'This record does not exist!'}, 404

            Application.delete_by_id(id)

            # Record this event in user's logs
            log_method = 'delete'
            log_description = f'Deleted application <{id}>'
            authorization = request.headers.get('Authorization')
            auth_token  = { "Authorization": authorization}
            record_user_log(auth_token, log_method, log_description)
            return {'message': f'Deleted software <{id}>'}, 200

        except Exception as e:
            print('========================================')
            print('Error description: ', e)
            print('========================================')
            return{'message':'Could not delete this application.'}, 500

@api.route('/logo/<int:id>')
@api.param('id', 'The Application Identifier')
class ApplicationList(Resource):
    @jwt_required
    @api.expect(logo_parser)
    @api.doc('Update Logo')
    def put(self, id):
        '''Update Logo'''
        try:
            claims = get_jwt_claims()
            if not claims['is_admin']:
                return {'message':'You are not authorised to access this resource!'}, 403

            args = logo_parser.parse_args()
            image_file = args.get('logo')  # This is FileStorage instance


            db_application = Application.fetch_by_id(id)
            application = application_schema.dump(db_application)

            if len(application) != 0:
                if image_file.filename == '':
                    return {'message':'No logo was found.'}, 400
                    
                if image_file and allowed_file(image_file.filename):
                    logo = secure_filename(image_file.filename)
                    image_file.save(os.path.join( 'uploads', logo))

                    Application.update_logo(id=id, logo=logo)

                    new_db_application = Application.fetch_by_id(id)
                    new_application = application_schema.dump(new_db_application)

                    # Record this event in user's logs
                    log_method = 'put'
                    log_description = f'Updated logo for application <{id}>'
                    authorization = request.headers.get('Authorization')
                    auth_token  = { "Authorization": authorization}
                    record_user_log(auth_token, log_method, log_description)
                    return {'software': new_application}, 200
                return {'message':'The logo you uploaded is not recognised.'}, 400
            return {'message': 'This record does not exist!'}, 404
        
        except Exception as e:
            print('========================================')
            print('Error description: ', e)
            print('========================================')
            return{'message':'Could not submit software logo.'}, 500

@api.route('/software/<int:software_id>')
@api.param('software_id', 'The Software Identifier')
class ApplicationList(Resource):
    @api.doc('Get applications by software')
    def get(self, software_id):
        '''Get Application by software'''
        try:
            db_applications = Application.fetch_by_software_id(software_id)
            applications = application_schemas.dump(db_applications)
            if len(applications) == 0:
                return {'message': 'These records do not exist.'}, 404
            return {'applications':applications}, 200
        except Exception as e:
            print('========================================')
            print('Error description: ', e)
            print('========================================')
            return{'message':'Could not retrieve application.'}, 500