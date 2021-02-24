from flask import Flask, request
from flask_restful import Resource
from marshmallow import ValidationError
from datetime import date, datetime, timedelta
from sqlalchemy.sql.expression import and_

from config import db, base, app
from .booking_service import BookingService
from models.book_hotel import BookHotelReservationSchema, BookHotel
from models.book_status import BookStatus
from common.util import Util
from resources.property.property_service import PropertyService
from resources.carta.emailTemplate import EmailTemplate

class BookingOnHoldReminder(Resource):
    def post(self):
        todays_datetime = datetime(datetime.utcnow().year, datetime.utcnow().month, datetime.utcnow().day,\
            datetime.utcnow().hour, datetime.utcnow().minute)
        
        """
            todays_end add 8hrs and 1 minute to consider the bookings will expired in that time
            todays_start subtracts 5 minutes (or more, dependence of the background process) to cover the range of each background
            process
        """
        todays_end = todays_datetime + timedelta(hours = 8, minutes = 1)
        todays_start = todays_end - timedelta(minutes = 5)
        
        bookings = BookHotel.query.filter(BookHotel.estado == 1, BookHotel.idbook_status == BookStatus.on_hold,\
            BookHotel.expiry_date <= todays_end,
            BookHotel.expiry_date >= todays_start).all()

        booking_service = BookingService()
        total = 0
        for book_hotel in bookings:
            try:
                booking_data = booking_service.format_booking_info(book_hotel)
                email_template = EmailTemplate()
                subject = email_template.getSubject(booking_data, booking_data["lang_code"], True)
                email_data = {
                    "email_list": booking_data["customer"]["email"],
                    "sender": booking_data["sender"],
                    "group_validation": False,
                    "html": email_template.get(booking_data),
                    "email_subject": subject
                }

                Util.send_notification(email_data, email_template.email_tag, "bengine_process")

                total += 1
                if base.environment == "pro":
                    #retrieve email cc to send a email copy
                    email_cc = PropertyService.get_email_contact(book_hotel.iddef_property, ";")
                    email_data["email_list"] = email_cc
                    Util.send_notification(email_data, email_template.email_tag, "bengine_process")
            except Exception as e:
                app.logger.error("Booking on hold cancel process Error: "+ str(e))
        
        return {
            "Code": 200,
            "Msg": "Booking reminders: " + str(total),
            "Error": True,
            "data": {}
        }

class BookingOnHoldCancel(Resource):
    def post(self):
        todays_datetime = datetime(datetime.utcnow().year, datetime.utcnow().month, datetime.utcnow().day,\
            datetime.utcnow().hour, datetime.utcnow().minute)
        
        """
            todays_end add 1 minute to consider the seconds
            todays_start subtracts 5 minutes (or more, dependence of the background process) to cover the range of each background
            process
        """
        todays_end = todays_datetime + timedelta(minutes = 1)
        todays_start = todays_end - timedelta(minutes = 5)
        
        #looking for on hold bookings
        bookings = BookHotel.query.filter(BookHotel.estado == 1, BookHotel.idbook_status == BookStatus.on_hold,\
            BookHotel.expiry_date <= todays_end,
            BookHotel.expiry_date >= todays_start).all()
        
        booking_service = BookingService()
        total = 0
        for book_hotel in bookings:
            """
                if the booking expired, change the status and save, after we send the email to notify
            """
            book_hotel.idbook_status = BookStatus.expired
            book_hotel.usuario_ultima_modificacion = "bengine_process"
            db.session.add(book_hotel)
            db.session.commit()
            
            try:
                booking_data = booking_service.format_booking_info(book_hotel)
                email_template = EmailTemplate()
                subject = email_template.getSubject(booking_data, booking_data["lang_code"])
                email_data = {
                    "email_list": booking_data["customer"]["email"],
                    "sender": booking_data["sender"],
                    "group_validation": False,
                    "html": email_template.get(booking_data),
                    "email_subject": subject
                }

                Util.send_notification(email_data, email_template.email_tag, "bengine_process")
                total += 1
                if base.environment == "pro":
                    #retrieve email cc to send a email copy
                    email_cc = PropertyService.get_email_contact(book_hotel.iddef_property, ";")
                    email_data["email_list"] = email_cc
                    Util.send_notification(email_data, email_template.email_tag, "bengine_process")
            except Exception as e:
                app.logger.error("Booking on hold cancel process Error: "+ str(e))
        
        return {
            "Code": 200,
            "Msg": "Booking reminders: " + str(total),
            "Error": True,
            "data": {}
        }