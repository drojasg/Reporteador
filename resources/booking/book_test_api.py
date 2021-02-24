from flask import Flask, request
from flask_restful import Resource
from marshmallow import ValidationError
from datetime import date, datetime, timedelta
from sqlalchemy.sql.expression import and_
from config import db, base
from common.util import Util
from models.book_hotel import BookHotel as booking
from .booking_service import BookingService as bkService, WireRequest, WireService

class test_book_apis(Resource): 
    #api-test-booking-send-pms
    #@base.access_middleware
    def get(self,idbook):

        book_detail = booking.query.get(idbook)

        service = bkService()

        book_detail.code_reservation = service.get_booking_code(book_detail.idbook_hotel,\
        book_detail.iddef_property,book_detail.idbook_status)

        response = bkService.create_booking(book_hotel=book_detail)

        return response

class request_to_pms(Resource):

    #@base.access_middleware
    def get(self,idbook):
        response = {
            "msg":"success",
            "data":{}
        }
        try:
            # user_data = base.get_token_data()
            # username = user_data['user']['username']
            username = "Test"

            book_detail = booking.query.get(idbook)

            service = bkService()

            book_detail.code_reservation = service.get_booking_code(book_detail.idbook_hotel,\
            book_detail.iddef_property,book_detail.idbook_status)
            
            wire_request = WireRequest()

            service._check_customer_profile(book_detail.customers[0].customer,username=username)
            response_data = wire_request.create_request(book_detail,is_update=True,\
            send_notification=False,username=username)
            
            response["data"] = response_data

        except Exception as api_error:
            response["msg"]= str(api_error)

        return response