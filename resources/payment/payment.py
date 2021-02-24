from flask import Flask, request
from flask_restful import Resource
from marshmallow import ValidationError
from datetime import date
#from sqlalchemy.sql.expression import and_
from config import db, base
from common.card_validation import CardValidation
from models.payment_transaction import CardSchema
from models.book_hotel import BookHotel
from models.payment_transaction import PaymentTransaction, PaymentSchema
from common.public_auth import PublicAuth
from common.util import Util
from .payment_service import PaymentService
from .charges_service import ChargesService

class Payment(Resource):
    @PublicAuth.access_middleware
    def post(self):
        response = {
            "Code": 200,
            "Msg": "Success",
            "Error": False,
            "data": {}
        }
        try:
            pass
        except ValidationError as error:
            response = {
                "Code": 500,
                "Msg": error.messages,
                "Error": True,
                "data": {}
            }
        except Exception as e:
            response = {
                "Code": 500,
                "Msg": str(e),
                "Error": True,
                "data": {}
            }
        
        return response

class PaymentSearch(Resource):
    #api-payment-search-get
    # @base.access_middleware
    def get(self, idbook_hotel):
        try:
            list_payment = PaymentTransaction.query.filter(PaymentTransaction.idbook_hotel == idbook_hotel, \
                PaymentTransaction.estado == 1)

            data = []
            for payment in list_payment:
                payment_info = {
                    "idpayment_transaction": payment.idpayment_transaction, 
                    "idpayment_method": payment.idpayment_method, 
                    "idpayment_transaction_type": payment.idpayment_transaction_type,
                    "card_code": payment.card_code,
                    "transaction_type": payment.payment_type.name, 
                    "payment_method": payment.payment_method.name,
                    "authorization_code": payment.authorization_code, 
                    "merchant_code": payment.merchant_code, 
                    "ticket_code": payment.ticket_code, 
                    "idfin_payment": payment.idfin_payment,
                    "amount": payment.amount, 
                    "exchange_rate": payment.exchange_rate, 
                    "currency_code": payment.currency_code, 
                    "usuario_creacion": payment.usuario_creacion,
                    "fecha_creacion": payment.fecha_creacion,
                }

                data.append(payment_info)
            
            schema = PaymentSchema(many=True)

            if data is None:
                response = {
                    "Code": 200,
                    "Msg": "Success",
                    "Error": False,
                    "data": {}
                }
            else:
                response = {
                    "Code": 200,
                    "Msg": "Success",
                    "Error": False,
                    "data": schema.dump(data)
                }
        except Exception as e:
            response = {
            "Code": 500,
            "Msg": str(e),
            "Error": True,
            "data": {}
            }

        return response

class Validation(Resource):
    @PublicAuth.access_middleware
    def post(self):
        response = {}
        try:
            json_data = request.get_json(force=True)
            schema = CardSchema()
            data = schema.load(json_data)

            card_info = CardValidation(data["card_number"], data["exp_month"], data["exp_year"])
            
            if not card_info.is_valid or card_info.code is None:                
                raise Exception(Util.t("en", "payment_card_not_valid"))
            
            if card_info.is_expired:
                raise Exception(Util.t("en", "payment_card_expired"))
            
            response = {
                "Code": 200,
                "Msg": "Success",
                "Error": False,
                "data": {}
            }
        except ValidationError as error:
            response = {
                "Code": 500,
                "Msg": error.messages,
                "Error": True,
                "data": {}
            }
        except Exception as e:
            response = {
                "Code": 500,
                "Msg": str(e),
                "Error": True,
                "data": {}
            }
        
        return response
    
class LinkPayments(Resource):
    def get(self):
        charge_service = ChargesService()
        data = [
            {
                "code_reservation":"ZHBP-129-BE",
                "pms_confirm_number":"13723098",
                "property_code":"ZHBP",
                "from_date":"2020-10-23",
                "amount":"100",
                "amount_currency":"MXN",
                "user":"BookingEngine",
                "payment": {
                    "card_type": "visa",
                    "card_number": "4111111111111111",
                    "holder_first_name": "Francisco",
                    "holder_last_name": "Mahay",
                    "cvv": "123",
                    "expirity_month": "02",
                    "expirity_year": "24"
                }
            }
        ]

        charge_service.send_booking(data)

    
    def post(self):
        response = {}
        try:
            query = """
            SELECT t.idpayment_transaction_detail, idFin, r.pms_confirm_number
            FROM payment_transaction_detail t
            INNER JOIN book_hotel_room r ON r.idbook_hotel_room = t.idbook_hotel_room
            AND r.pms_confirm_number != "" AND r.iddef_pms = 1 AND r.estado = 1
            WHERE t.estado = 1 AND t.interfaced = 0
            """
            result = db.session.execute(query)

            payment_service = PaymentService()
            total = payment_service.link_room_payment(result, "bengine_process")

            response = {
                "Code": 200,
                "Msg": "Success",
                "Error": False,
                "data": "Payments linked: " + str(total),
            }
        except Exception as e:
            response = {
                "Code": 500,
                "Msg": str(e),
                "Error": True,
                "data": {}
            }
        
        return response

class BookingInfoTransactionId(Resource):
    # @base.access_middleware
    def get(self, idbook_hotel):
        response = {}
        try:
            model = BookHotel.query.filter(BookHotel.idbook_hotel==idbook_hotel, BookHotel.estado==1).order_by(BookHotel.idbook_hotel.desc()).first()

            if model is None:
                raise Exception("Booking not found")

            payment_service = PaymentService()
            info_sum_payments = payment_service.get_info_sum_payments(model.idbook_hotel, model.from_date)

            result = {
                "idbook_hotel":model.idbook_hotel,
                "code_reservation":model.code_reservation,
                "total_transactions":info_sum_payments["total_paid"],
                "total_pending_transactions":info_sum_payments["total_pending"],
                "currency":model.currency.currency_code
            }

            response = {
                "Code": 200,
                "Msg": "Success",
                "Error": False,
                "data": result
            }
        except Exception as e:
            response = {
                "Code": 500,
                "Msg": str(e),
                "Error": True,
                "data": {}
            }

        return response

class BookingInfoTransactionCode(Resource):
    # @base.access_middleware
    def get(self, code_reservation):
        response = {}
        try:
            model = BookHotel.query.filter(BookHotel.code_reservation.like(code_reservation), BookHotel.estado==1).order_by(BookHotel.idbook_hotel.desc()).first()

            if model is None:
                raise Exception("Booking not found")

            payment_service = PaymentService()
            info_sum_payments = payment_service.get_info_sum_payments(model.idbook_hotel, model.from_date)

            result = {
                "idbook_hotel":model.idbook_hotel,
                "code_reservation":model.code_reservation,
                "total_transactions":info_sum_payments["total_paid"],
                "total_pending_transactions":info_sum_payments["total_pending"],
                "currency":model.currency.currency_code
            }

            response = {
                "Code": 200,
                "Msg": "Success",
                "Error": False,
                "data": result
            }
        except Exception as e:
            response = {
                "Code": 500,
                "Msg": str(e),
                "Error": True,
                "data": {}
            }

        return response