import os

from werkzeug.utils import secure_filename
from werkzeug.datastructures import FileStorage
from flask import request
from flask_restx import Namespace, Resource, fields
from flask_jwt_extended import jwt_required, get_jwt_claims, get_jwt_identity

from models.software import SoftwareModel
from schemas.software import SoftwareSchema
from user_functions.record_user_log import record_user_log
from user_functions.validate_logo import allowed_file

api = Namespace('software', description='Manage antiviruses')

software_schema = SoftwareSchema()
software_schemas = SoftwareSchema(many=True)

upload_parser = api.parser()
upload_parser.add_argument('logo', location='files', type=FileStorage, required=True, help='Software Logo') # location='headers'
upload_parser.add_argument('name', location='form', type=str, required=True, help='Software Name') # location='headers'

logo_parser = api.parser()
logo_parser.add_argument('logo', location='files', type=FileStorage, required=True, help='Software Logo') # location='headers'


software_model = api.model('Software', {
    'name': fields.String(required=True, description='Name')
})


@api.route('')
class SoftwareList(Resource):
    @classmethod
    @api.doc('Get all Software')
    def get(cls):
        '''Get all Software'''
        try:
            software = SoftwareModel.fetch_all()
            if software:
                software_list = software_schemas.dump(software)
                for software_item in software_list:
                    application_count = len(software_item['applications'])
                    software_item['application_count'] = application_count
                    for application in software_item['applications']:
                        license_count = len(application['licenses'])
                        application['licenses'] = license_count
                return software_list, 200
            return {'message': 'There are no antivirus software yet.'}, 404
        except Exception as e:
            print('========================================')
            print('Error description: ', e)
            print('========================================')
            return{'message':'Could not retrieve any software.'}, 500

    @classmethod
    @jwt_required
    @api.doc('Post Software')
    @api.expect(upload_parser)
    def post(cls):
        '''Post Software'''
        try:
            claims = get_jwt_claims()
            if not claims['is_admin']:
                return {'message':'You are not authorised to access this resource!'}, 403

            args = upload_parser.parse_args()
            name = args['name'].title()
            image_file = args.get('logo')  # This is FileStorage instance

            if name == '':
                return {'message':'You never included a name.'}, 400

            software = SoftwareModel.fetch_by_name(name)
            if software:
                return {'message': 'This software already exists!'}, 400

            if image_file.filename == '':
                return {'message':'No logo was found.'}, 400
                    
            if image_file and allowed_file(image_file.filename):
                logo = secure_filename(image_file.filename)
                image_file.save(os.path.join( 'uploads', logo))
                new_software = Software(logo=logo,name=name)
                new_software.insert_record()

                # Record this event in user's logs
                log_method = 'post'
                log_description = f'Added software {name}'
                authorization = request.headers.get('Authorization')
                auth_token  = { "Authorization": authorization}
                record_user_log(auth_token, log_method, log_description)
                return {'software': name}, 201
            return {'message':'The logo you uploaded is not recognised.'}, 400
        except Exception as e:
            print('========================================')
            print('Error description: ', e)
            print('========================================')
            return{'message':'Could not submit software.'}, 500

@api.route('/<int:id>')
@api.param('id', 'The software identifier.')
class SoftwareDetail(Resource):
    @classmethod
    @api.doc('Get Single Software')
    def get(cls, id:int):
        '''Get Single Software'''
        try:
            software = SoftwareModel.fetch_by_id(id)
            if software:
                software_item = software_schema.dump(software)
                application_count = len(software_item['applications'])
                software_item['application_count'] = application_count
                for application in software_item['applications']:
                    license_count = len(application['licenses'])
                    application['licenses'] = license_count
                
                return software_item, 200
            return {'message':'This software does not exist!'}, 404 
        except Exception as e:
            print('========================================')
            print('Error description: ', e)
            print('========================================')
            return{'message':'Could not retrieve this software.'}, 500

    @classmethod
    @jwt_required
    @api.doc('Update Software Name')
    @api.expect(software_model)
    def put(cls, id:int):
        '''Update Software Name'''
        try:
            claims = get_jwt_claims()
            if not claims['is_admin']:
                return {'message':'You are not authorised to access this resource!'}, 403

            data = api.payload
            if not data:
                return {'message': 'No input data detected.'}, 400

            name = data['name'].title()

            if name == '':
                return {'message':'You never included a name.'}, 400
            
            software = SoftwareModel.fetch_by_id(id)
            if software:
                software_by_name = SoftwareModel.fetch_by_name(name)
                if software_by_name:
                    if software_by_name.id != id:
                        return {'message':'This record already exists in the database!'}, 400

                SoftwareModel.update_name(id=id, name=name)

                # Record this event in user's logs
                log_method = 'put'
                log_description = f'Updated software <{id}> to {name}'
                authorization = request.headers.get('Authorization')
                auth_token  = { "Authorization": authorization}
                record_user_log(auth_token, log_method, log_description)
                return software_schema.dump(software), 200
            return {'message':'This record does not exist!'}, 404

        except Exception as e:
            print('========================================')
            print('Error description: ', e)
            print('========================================')
            return{'message':'Could not update this software.'}, 500

    @classmethod
    @jwt_required
    @api.doc('Delete Software')
    def delete(cls, id:int):
        '''Delete Software'''
        try:
            claims = get_jwt_claims()
            if not claims['is_admin']:
                return {'message':'You are not authorised to access this resource!'}, 403

            software = SoftwareModel.fetch_by_id(id)
            if software:              
                SoftwareModel.delete_by_id(id)

                # Record this event in user's logs
                log_method = 'delete'
                log_description = f'Deleted software <{id}>'
                authorization = request.headers.get('Authorization')
                auth_token  = { "Authorization": authorization}
                record_user_log(auth_token, log_method, log_description)
                return {'message': f'Deleted software <{id}>'}, 200
            return {'message':'This record does not exist!'}, 404

        except Exception as e:
            print('========================================')
            print('Error description: ', e)
            print('========================================')
            return{'message':'Could not delete this software.'}, 500


@api.route('/logo/<int:id>')
@api.param('id', 'The software identifier.')
class LogoDetail(Resource):
    @classmethod
    @jwt_required
    @api.expect(logo_parser)
    @api.doc('Update Software Logo')
    def put(cls, id:int):
        '''Update Software Logo'''
        try:
            claims = get_jwt_claims()
            if not claims['is_admin']:
                return {'message':'You are not authorised to access this resource!'}, 403

            args = logo_parser.parse_args()
            image_file = args.get('logo')  # This is FileStorage instance


            software = SoftwareModel.fetch_by_id(id)
            if software:
                if image_file.filename == '':
                    return {'message':'No logo was found.'}, 400
                    
                if image_file and allowed_file(image_file.filename):
                    logo = secure_filename(image_file.filename)
                    image_file.save(os.path.join( 'uploads', logo))

                    SoftwareModel.update_logo(id=id, logo=logo)

                    new_db_software = SoftwareModel.fetch_by_id(id)
                    new_software = software_schema.dump(new_db_software)

                    # Record this event in user's logs
                    log_method = 'put'
                    log_description = f'Updated logo for software <{id}>'
                    authorization = request.headers.get('Authorization')
                    auth_token  = { "Authorization": authorization}
                    record_user_log(auth_token, log_method, log_description)
                    return software_schema.dump(software), 200
                return {'message':'The logo you uploaded is not recognised.'}, 400
            return {'message': 'This record does not exist!'}, 404
        
        except Exception as e:
            print('========================================')
            print('Error description: ', e)
            print('========================================')
            return{'message':'Could not update software logo.'}, 500