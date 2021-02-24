from flask import Flask, request
from flask_restful import Resource
from marshmallow import ValidationError

from config import db, base
from common.util import Util
from common.public_auth import PublicAuth

class PermissionPublic(Resource):
    #api-acl-get
    @PublicAuth.access_middleware
    def post(self):
        json_data = request.get_json(force=True)
        base_response = {
            "Code": 500,
            "Msg": "",
            "Error": True,
            "data": {}
        }
        
        try:
            #credential_key = base.credential_key
            if not json_data["token"]:
                raise Exception("token is required")

            base_url = base.get_url("auth")
            resource = "api-allow-select-market"
            method = "post"
            system_id = base.system_id
            url = "%s/acl/acl/%s/%s/%s" % (base_url, resource, method, system_id)

            response, status, header, log_meta_data = base.request(url=url, use_token=False, token=json_data["token"])

            if response["allowed_access"] is False:
                raise Exception("Access denied")

            base_response["Code"] = 200
            base_response["Error"] = False
        except Exception as e:
            base_response["Msg"] = str(e)
        
        return base_response
    