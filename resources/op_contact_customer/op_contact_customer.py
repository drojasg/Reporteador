from flask import Flask, request
from flask_restful import Resource
from marshmallow import ValidationError

from config import db, base
from models.op_contact_customer import OpContactCustomer as Model, OpContactCustomerSchema as ModelSchema
from common.util import Util
import re
from common.public_auth import PublicAuth
from resources.booking.booking_service import BookingService

class OpContactCustomer(Resource):

    @staticmethod
    def es_correo_valido(correo):
        expresion_regular = r"(?:[a-z0-9!#$%&'*+/=?^_`{|}~-]+(?:\.[a-z0-9!#$%&'*+/=?^_`{|}~-]+)*|\"(?:[\x01-\x08\x0b\x0c\x0e-\x1f\x21\x23-\x5b\x5d-\x7f]|\\[\x01-\x09\x0b\x0c\x0e-\x7f])*\")@(?:(?:[a-z0-9](?:[a-z0-9-]*[a-z0-9])?\.)+[a-z0-9](?:[a-z0-9-]*[a-z0-9])?|\[(?:(?:(2(5[0-5]|[0-4][0-9])|1[0-9][0-9]|[1-9]?[0-9]))\.){3}(?:(2(5[0-5]|[0-4][0-9])|1[0-9][0-9]|[1-9]?[0-9])|[a-z0-9-]*[a-z0-9]:(?:[\x01-\x08\x0b\x0c\x0e-\x1f\x21-\x5a\x53-\x7f]|\\[\x01-\x09\x0b\x0c\x0e-\x7f])+)\])"
        return re.match(expresion_regular, correo) is not None


    @PublicAuth.access_middleware
    def post(self):
        response = {}
        try:
            json_data = request.get_json(force=True)
            schema = ModelSchema(exclude=Util.get_default_excludes())
            data = schema.load(json_data)
            model = Model()

            credential_data = PublicAuth.get_credential_data()
            username = credential_data.name
            #user_data = base.get_token_data()
            #user_name = user_data['user']['username']

            email = self.es_correo_valido(data["email"].lower())

            model.name = data["name"]
            model.contact_time = data["contact_time"]
            model.telephone = data["telephone"]
            if email:
                model.email = data["email"]
            else:
                raise Exception("Please insert a valid email")
            model.iddef_time_zone = 0
            model.estado = 1
            model.usuario_creacion = username
            db.session.add(model)
            db.session.commit()

            # send email contact
            tag_notification = "NOTIFICATION_BENGINE_CONTACT"
            emailTo = "mmoo@palaceresorts.com;fmahay@palaceresorts.com;lunovelo@palaceresorts.com"

            if base.environment == "pro":
                booking_service = BookingService()
                param = booking_service.get_config_param_one("contact_email")
                emailTo = "ECommerce@palaceresorts.com" if not param else param.value
                            
            email_data = {
                "email_list":emailTo,
                "group_validation": False,
                "name":model.name,
                "time":model.contact_time,
                "email":model.email,
                "phone_number":model.telephone,
                "email_subject":tag_notification
            }            
            Util.send_notification(email_data, tag_notification, model.usuario_creacion)

            response = {
                "Code": 200,
                "Msg": "Success",
                "Error": False,
                "data": schema.dump(model)
            }
        except ValidationError as error:
            db.session.rollback()
            response = {
                "Code": 500,
                "Msg": error.messages,
                "Error": True,
                "data": {}
            }
        except Exception as e:
            db.session.rollback()
            response = {
                "Code": 500,
                "Msg": str(e),
                "Error": True,
                "data": {}
            }
        
        return response
