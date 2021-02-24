from flask import Flask, request
from flask_restful import Resource
from datetime import date, datetime, timedelta

from config import db, base
from models.book_status import BookStatus

from common.util import Util
from .booking_service import BookingService
from common.public_auth import PublicAuth

class BookingPublicV2(Resource):
    @PublicAuth.access_middleware
    def get(self, code_reservation, full_name, lang_code):
        response = {}
        try:
            booking_service = BookingService()
            data = booking_service.get_booking_info_by_code(code_reservation, full_name, lang_code)

            if data["status_code"] not in [BookStatus.confirmed, BookStatus.changed, BookStatus.interfaced, BookStatus.partial_interfaced, BookStatus.on_hold]:
                raise Exception(Util.t(lang_code, "booking_code_not_found", code_reservation))
            
            response = {
                "Code": 200,
                "Msg": "Success",
                "Error": False,
                "data": data
            }
        except Exception as e:
            response = {
                "Code": 500,
                "Msg": str(e),
                "Error": True,
                "data": {}
            }

        return response
