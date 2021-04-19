from flask import Flask, request, jsonify
from flask_restful import Resource
from marshmallow import ValidationError
from datetime import date, datetime, timedelta
from sqlalchemy.sql.expression import and_
from functools import reduce
from config import db, base
from common.util import Util
from models.book_hotel import BookHotel as Model, BookHotelSchema as bookschema, BookHotelReservationSchema as resschema
from models.prueba import PruebaBookingSchema as bookschema1
import json

class BookHotelCustomerSearch(Resource):
    def get(self):
        try:
            query = """SELECT 
                        ba.iddef_country,
                        pr.property_code,
                        CONCAT_WS(' ',
                                bc.title,
                                bc.first_name,
                                bc.last_name) AS guest_name,
                        bc.email AS guest_email,
                        CONCAT_WS('-', bc.dialling_code, bc.phone_number) AS guest_phone,
                        bhr.iddef_room_type AS room_type_id,
                        CONCAT_WS('-', rtc.room_description, rtc.room_code) AS room_type,
                        pr.trade_name AS hotel_name,
                        bhr.idop_rate_plan AS id_rate_plan,
                        rtp.code AS rate_plan,
                        bh.*
                    FROM
                        book_hotel bh
                            JOIN
                        book_hotel_room bhr ON bh.idbook_hotel = bhr.idbook_hotel
                            AND bhr.estado = 1
                            JOIN
                        def_property pr ON pr.iddef_property = bh.iddef_property
                            JOIN
                        book_customer_hotel bch ON bch.idbook_hotel = bh.idbook_hotel
                            AND bch.estado = 1
                            JOIN
                        book_customer bc ON bc.idbook_customer = bch.idbook_customer
                            JOIN
                        def_room_type_category rtc ON rtc.iddef_room_type_category = bhr.iddef_room_type
                            JOIN
                        book_status bs ON bs.idbook_status = bh.idbook_status
                            JOIN
                        book_address ba ON ba.idbook_customer = bc.idbook_customer
                    		JOIN
                    	op_rateplan rtp ON rtp.idop_rateplan = bhr.idop_rate_plan
                    WHERE
                        bh.estado = 1 """

            book_hotel = db.session.execute(query).fetchall()
            for row in book_hotel:
                print(row)
            schema = bookschema1(many = True)
            response = {
                "Code": 200,
                "Msg": "Success",
                "Error": False,
                "data": schema.dump(book_hotel)
            }
        except Exception as e:
            response = {
                "Code": 500,
                "Msg": str(e),
                "Error": True,
                "data":{}
            }
        return response