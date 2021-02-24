from flask import Flask, request
from flask_restful import Resource
from marshmallow import ValidationError

from config import db

from models.auth_profile_view import AuthProfileView
from models.credentials import Credentials

class AclService():
    def __init__(self, controller, method, credential_key):
        self.__controller = controller
        self.__method = method
        self.__credential_key = credential_key
    
    @property
    def is_allowed(self):
        '''
            Check if the role has access to endpoint
            return boolean
        '''
        roles = self.__get_credential_roles(is_object_list=False)
        
        found = db.session.query(AuthProfileView.id_profile_view).\
            filter(AuthProfileView.action == self.__method, \
            AuthProfileView.auth_item.in_(roles), AuthProfileView.estado == 1).first() is not None
                
        return found
    
    def __get_credential_roles(self, is_object_list = True):
        credential = Credentials.query.filter(Credentials.api_key == self.__credential_key, Credentials.estado == 1).first()

        if not credential:
            raise Exception("credential key not exists")
        
        if is_object_list:
            return credential.roles
        else:
            return [role.item_name for role in credential.roles]
    
    def check_access(self):
        response = {
            "allowed_access": False,
            "message": "YOU ARE NOT AUTHORIZED TO EXCECUTE THIS ACTION [{}]".format(self.__method)
        }

        try:            
            if self.is_allowed:
                response = {
                    "allowed_access": True,
                    "message": "OK"
                }
        except Exception as e:
            response["message"] = str(e)
        
        return response