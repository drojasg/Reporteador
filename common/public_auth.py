from functools import wraps
from flask import request
from config import db, base

from resources.acl.acl_service import AclService
from models.credentials import Credentials

'''
    Check the api-key for public apis
'''
class PublicAuth():
    def access_middleware(func):
        """ Resource decorator to validate api-key """

        @wraps(func)
        def wrapper(*args, **kwargs):
            error_message = "An error has occurred!"
            #is_public = re.search("^/api/public/", request.full_path)

            if not base.enable_public_middleware:
                return func(*args, **kwargs)

            #check if header api-key exists
            credential_key = base.credential_key
            if not credential_key:
                return base.build_error_response(400, "api-key header is required")
            
            try:
                resource = request.endpoint
                method = request.method.lower()
                
                if not PublicAuth.allow_credential_use():
                    return base.build_error_response(400, "ip or dns are not allowed to use the api-key credential")

                acl_service = AclService(controller=resource, method=resource, credential_key=credential_key)
                response = acl_service.check_access()

                if "allowed_access" in response:
                    if not response["allowed_access"]:
                        error_message = response["message"]
                        return base.build_error_response(
                            403, message=error_message
                        )
                else:
                    error_message = "BAD TOKEN GET A NEW ONE"
                    return base.build_error_response(
                        401, message=error_message
                    )
            except Exception:
                error_message = "BAD TOKEN GET A NEW ONE"
                return base.build_error_response(401, error_message)
            # Execute resource function
            try:
                return func(*args, **kwargs)
            except Exception as e:
                base.__LOGGER.exception(str(e))
                return base.build_error_response(500, error_message)

        return wrapper
    
    @classmethod
    def get_credential_data(cls):
        """
            retrieve credential info

            :return credential Credentials instance
        """

        #get api-key from headers request
        credential_key = base.credential_key

        if not credential_key:
            return None
        
        credential = Credentials.query.filter(Credentials.api_key == credential_key, \
            Credentials.estado == 1).first()
        
        return credential
    
    @classmethod
    def allow_credential_use(cls):
        """
            check if ip or dns are allowed to use in the client request
        """
        data = cls.get_credential_data()
        request_ip = request.environ['REMOTE_ADDR']
        request_dns = ""
        
        if data.ip_list_allowed or data.dns_list_allowed:
            allow_ip = True
            allow_dns = True

            if data.ip_list_allowed and request_ip not in data.ip_list_allowed:
                allow_ip = False
            
            if data.dns_list_allowed and request_dns not in data.dns_list_allowed:
                allow_dns = False

            return allow_ip and allow_dns
        
        return True
    