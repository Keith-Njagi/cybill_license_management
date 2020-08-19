import os

from werkzeug.utils import secure_filename
from werkzeug.datastructures import FileStorage
from flask import request
from flask_restx import Namespace, Resource, fields
from flask_jwt_extended import jwt_required, get_jwt_claims, get_jwt_identity

from models.software_model import Software, SoftwareSchema
from user_functions.record_user_log import record_user_log
from user_functions.validate_logo import allowed_file


