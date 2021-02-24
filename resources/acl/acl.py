from flask import Flask, request
from flask_restful import Resource
from marshmallow import ValidationError

from config import db, base
from common.util import Util
from .acl_service import AclService

class Acl(Resource):
    #api-acl-get
    #@base.access_middleware    
    def get(self, controller, method):
        response = {
            "allowed_access": False,
            "message": "YOU ARE NOT AUTHORIZED TO EXCECUTE THIS ACTION [CONTROLLER: {} . METHOD: {}]".format(controller, method)
        }

        try:
            credential_key = base.credential_key

            if not credential_key:
                raise Exception("api_key header is required")
            acl_service = AclService(controller=controller, method=method, credential_key=credential_key)
            response = acl_service.check_access()
            
        except Exception as e:
            response["message"] = str(e)
        
        return response
