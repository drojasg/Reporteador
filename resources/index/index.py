from flask_restful import Resource
from config import base

class Index(Resource):
    """ Index resource """

    def get(self):
        data = {}
        message = "Booking Engine API!"        

        return base.build_success_response(200, data=data, message=message)        
    
    # @base.access_middleware
    def post(self):
        return base.build_success_response(201)
    
    # @base.access_middleware
    def put(self):
        return base.build_success_response(204)
