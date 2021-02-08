# -*- coding: utf-8 -*-
"""
BaseController have common tasks (methods) that will be used in most of all
Resources.
"""
from collections import ChainMap
from flask import request
from functools import wraps
from requests import Timeout
from datetime import datetime
import requests
import base64
import json

__all__ = ["BaseController"]

INFO_CODES = {100: "Continue", 101: "Switching Protocols"}

SUCCESS_CODES = {
    200: "Ok",
    201: "Created",
    202: "Accepted",
    203: "Non-Authoritative Information",
    204: "No Content",
    205: "Reset Content",
    206: "Partial Content",
}

REDIRECTION_CODES = {
    300: "Multiple Choices",
    301: "Moved Permanently",
    302: "Found",
    303: "See Other",
    304: "Not Modified",
    307: "Temporary Redirect",
    308: "Permanent Redirect",
}

CLIENT_ERROR_CODES = {
    400: "Bad Request",
    401: "Unauthorized",
    403: "Forbidden",
    404: "Not Found",
    405: "Method Not Allowed",
    406: "Not Acceptable",
    407: "Proxy Authentication Required",
    408: "Request Timeout",
    409: "Conflict",
    410: "Gone",
    411: "Length Required",
    412: "Precondition Failed",
    413: "Request Entity Too Large",
    414: "Request URI Too Large",
    415: "Unsupported Media Type",
    416: "Range Not Satisfiable",
    417: "Expectation Failed",
    418: "I'm a teapot",
    422: "Unprocessable Entity",
    425: "Too Early",
    426: "Upgrade Required",
    428: "Precondition Required",
    429: "TooManyRequests",
    431: "Request Header Fields Too Large",
    451: "Unavailable For Legal",
}

SERVER_ERROR_CODES = {
    500: "Internal Server Error",
    501: "Not Implemented",
    502: "Bad Gateway",
    503: "Service Unavailable",
    504: "Gateway Timeout",
    505: "HTTP Version Not Supported",
    511: "Network Authentication Required",
}

ERROR_CODES = dict(ChainMap(SERVER_ERROR_CODES, CLIENT_ERROR_CODES))


class BaseController:
    def __init__(self, app=None):
        #: Set logger
        self.__LOGGER = app.logger
        #: Set config
        self.__CONFIG = app.config

    @property
    def environment(self):
        return self.app_config("APP_ENV")

    @property
    def enable_admin_middleware(self):
        return self.app_config("ENABLE_ADMIN_MIDDLEWARE")

    @property
    def enable_public_middleware(self):
        return self.app_config("ENABLE_PUBLIC_MIDDLEWARE")

    @property
    def system_id(self):
        return self.app_config("SYSTEM_ID")

    @property
    def app_name(self):
        return self.app_config("APP_NAME")

    @property
    def sqs_broker_url(self):
        return self.app_config("CELERY_BROKER_URL")
    
    @property
    def dtc_url(self):
        return "http://127.0.0.1:9010"

    # Decorator to validate Bearer Token in request.
    def access_middleware(self, func):
        """ Resource decorator to validate token """

        @wraps(func)
        def wrapper(*args, **kwargs):

            if not self.enable_admin_middleware:
                return func(*args, **kwargs)
            
            error_message = "An error has occurred!"
            if "Authorization" not in request.headers:
                error_message = "EMPTY TOKEN OR NOT RECEIVED"
                return self.build_error_response(400, error_message)
            else:
                # Request auth to validate token
                try:
                    resource = request.endpoint
                    method = request.method.lower()
                    url = self.get_url("auth")
                    system_id = self.system_id
                    auth_url = "%s/acl/acl/%s/%s/%s" % (
                        url,
                        resource,
                        method,
                        system_id,
                    )
                    response, status, header, log_meta_data = self.request(url=auth_url)
                    if response["allowed_access"] is False:
                        error_message = response["message"]
                        return self.build_error_response(403, message=error_message)
                except Exception:
                    error_message = "BAD TOKEN GET A NEW ONE"
                    return self.build_error_response(401, message=error_message)
                # Execute resource function
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    self.__LOGGER.exception(str(e))
                    return self.build_error_response(500, error_message)

        return wrapper

    def decode_base64_json(self, data):
        """ Decodes a base64 data """

        try:
            return json.loads(base64.b64decode(data.decode("utf-8")))
        except Exception:
            return {}

    def encode_base64_json(self, data):
        """ Encode data to base64 """

        return base64.b64encode(data.encode("UTF-8"))

    def app_config(self, key):
        """ Returns Flask.config global variables """

        return self.__CONFIG.get(key, "")

    def build_success_response(self, status, data={}, message="", **kargs):
        """ JSON response for 2XX codes """

        #: Returns nothing if not content
        if status == 204:
            return None, status
        #: Just return 2XX codes
        if status not in SUCCESS_CODES:
            return self.build_error_response(status, message)
        #: Set message code if message is empty
        if message == "":
            message = SUCCESS_CODES.get(status, "")
        #: Response structure
        response = {
            "success": True,
            "status": status,
            "message": message,
            "data": data,
        }
        if len(kargs) == 0 and status == 200:
            return response, status
        for key in kargs:
            response[key] = kargs[key]
        return response, status

    def build_error_response(self, status, errors={}, message="", **kargs):
        """ JSON response for 4XX and 5XX codes """

        if status not in ERROR_CODES:
            status = 500
        if message == "":
            message = ERROR_CODES.get(status, "")
        response = {"success": False, "status": status, "message": message}
        if status == 400:
            response["errors"] = errors
        for key in kargs:
            response[key] = kargs[key]
        return response, status

    def __werkzeug_error_message(self, status=500):
        """ Message to show in werkzeug error """

        response, _ = self.build_error_response(status)
        return response

    def clever_login(self, url, user, password):
        """
            Method to login user in clever auth
        """
        response = None
        try:
            response = requests.post(url, auth= (user, password))
            response = json.loads(response.content)
        except Timeout as e:
            pass
        
        except Exception as e:
            pass
        
        return response
        
    def request(
        self,
        url="",
        method="get",
        data={},
        content_type="application/json",
        timeout=15,
        use_token=True,
        token=None,
        verifi_ssl=True,
        files = []
    ):
        """Make HTTP GET/POST/PUT requests"""

        #: Response
        resp = None
        resp_status = None
        resp_headers = {}
        log_meta_data = {
            "url": None,
            "request_method": None,
            "request_headers": None,
            "request_data": None,
            "request_timestamp": None,
            "response_headers": None,
            "response_data": None,
            "response_timestamp": None
        }
        headers = {}
        
        #: Request headers
        if content_type:
            headers = {"content-type": content_type}
        
        if use_token and "Authorization" in request.headers:
            headers["Authorization"] = request.headers["Authorization"]
        elif not use_token and token is not None:
            headers["Authorization"] = "Bearer {}".format(token)
        
        try:
            #: Parse to JSON if is application/json
            req_data = (
                json.dumps(data)
                if content_type == "application/json"
                else data
            )

            log_meta_data["request_headers"] = headers
            log_meta_data["request_data"] = req_data
            log_meta_data["url"] = url
            log_meta_data["request_timestamp"] = datetime.utcnow()
            log_meta_data["request_method"] = method

            if method == "post":
                response = requests.post(url, data=req_data, verify=verifi_ssl, \
                headers=headers, timeout=timeout, files=files)
            elif method == "put":
                response = requests.put(url, data=req_data, verify=verifi_ssl, headers=headers,\
                timeout=timeout, files=files)
            else:
                response = requests.get(url, headers=headers, timeout=timeout, files=files)
            
            resp_headers = response.headers
            resp_status = response.status_code
            log_meta_data["response_timestamp"] = datetime.utcnow()

            resp = (
                json.loads(response.content)
                if "application/json" in resp_headers["Content-Type"].split(";")
                else response.content
            )
            
            log_meta_data["response_headers"] = resp_headers
            log_meta_data["response_data"] = resp
        except Timeout as e:            
            pass
        except Exception as e:            
            pass
        return resp, resp_status, resp_headers, log_meta_data

    def get_url(self, module, environment=None):
        """ Gets API urls """

        env = self.app_config("APP_ENV") if not environment else environment
        url = self.__CONFIG["URLS"].get(env, "dev").get(module, "")
        return url

    def get_db_uri(self):
        """ Retrieves database secret from AWS """

        secret_name = self.app_config("DB_SECRET_NAME")
        url = "%s/secrets/%s" % (self.dtc_url, secret_name)
        response, status, _, _ = self.request(url, use_token=False)
        if status == 200:
            dbapi = self.app_config("SQLALCHEMY_DBAPI")
            params = self.app_config("SQLALCHEMY_PARAMS")
            if type(params) is dict:
                params = "?%s" % "".join(
                    [
                        "&%s=%s" % (key, value)
                        for (key, value) in params.items()
                    ]
                )
            username = response.get("username", "")
            password = response.get("password", "")
            host = response.get("host", "")
            port = response.get("port", "")
            database = response.get("dbname", "")
            db_uri = "{}://{}:{}@{}:{}/{}{}".format(
                dbapi, username, password, host, port, database, params
            )
            return db_uri
        else:
            return self.app_config("SQLALCHEMY_DATABASE_URI")

    def save_log(self, message):
        """ Saving logs in AWS """

        pass

    def werkzeug_errors(self):
        """ Custom errors for flask_restful """

        errors = {
            "BadRequest": self.__werkzeug_error_message(400),
            "Unauthorized": self.__werkzeug_error_message(401),
            "Forbidden": self.__werkzeug_error_message(403),
            "NotFound": self.__werkzeug_error_message(404),
            "MethodNotAllowed": self.__werkzeug_error_message(405),
            "NotAcceptable": self.__werkzeug_error_message(406),
            "RequestTimeout": self.__werkzeug_error_message(408),
            "Conflict": self.__werkzeug_error_message(409),
            "Gone": self.__werkzeug_error_message(410),
            "RequestEntityTooLarge": self.__werkzeug_error_message(413),
            "RequestURITooLarge": self.__werkzeug_error_message(414),
            "ExpectationFailed": self.__werkzeug_error_message(417),
            "TooManyRequests": self.__werkzeug_error_message(429),
            "InternalServerError": self.__werkzeug_error_message(500),
            "ServiceUnavailable": self.__werkzeug_error_message(503),
        }
        return errors

    def get_username(self):
        """ Retrieve username from the current request """

        username = None
        try:
            data = request.get_json(force=True)
            if "usuario_ultima_modificacion" in data:
                return data["usuario_ultima_modificacion"]
            elif "usuario_ultima_modificacion" in request.form:
                return request.form["usuario_ultima_modificacion"]
            elif "usuario_creacion" in data:
                return data["usuario_creacion"]
            elif "usuario_creacion" in request.form:
                return request.form["usuario_creacion"]
            return username
        except Exception:
            return username

    def get_HTML_codes(self, targets=["SUCCESS"]):
        return (
            dict(
                ChainMap(
                    SUCCESS_CODES if "SUCCESS" in targets else {},
                    REDIRECTION_CODES if "REDIRECTION" in targets else {},
                    CLIENT_ERROR_CODES if "CLIENT_ERROR" in targets else {},
                    SERVER_ERROR_CODES if "SERVER_ERROR" in targets else {},
                )
            )
            if (type(targets) == list)
            else {}
        )

    def get_token_data(self):
        """
            return clever user data by token
        """
        auth_url = self.get_url("auth")
        auth_endoint = "{}/usuario/validatetoken".format(auth_url)
        decode_token = self.request(url=auth_endoint)

        if not decode_token:
            raise Exception("auth token is required")
        
        
        response = decode_token[0]
        if response['error']:
            raise Exception(response("message"))
        
        data = response['data']
        
        return data
    
    @property
    def credential_key(self):
        credential_key = None
        
        if "api-key" in request.headers:
            credential_key = request.headers["api-key"]
        
        return credential_key