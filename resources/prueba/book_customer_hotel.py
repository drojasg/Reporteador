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
    def post(self):
        try:
            data = request.get_json(force=True)
            schema = bookschema1(exclude=Util.get_default_excludes())
            data = schema.load(data)
            model = Model()
            from_date = data['date_start']
            to_date = data['date_end']
            idbook_status = data['idbookstatus'] 
            iddef_property = data['propiedades']
            listtest = tuple(idbook_status)
            print(listtest)
            # idbook_status= map(str(status)[1:-1])
            # iddef_property= map(str(properties)[1:-1])
            # def listToStringWithoutBrackets1(idbook_status):
            #     return str(idbook_status).replace('[','').replace(']','')
            # def listToStringWithoutBrackets2(iddef_property):
            #     return str(iddef_property).replace('[','').replace(']','')

            # status = listToStringWithoutBrackets1(idbook_status)
            # properties = listToStringWithoutBrackets2(iddef_property)
            # from_date = datetime.strptime(from_date, '%Y-%m-%d %H:%M:%S')
            # to_date = datetime.strptime(to_date, '%Y-%m-%d %H:%M:%S')

            # from_date = date_start.replace(hour=00, minute=00, second=00)
            # to_date = date_end.replace(hour=23, minute=59, second=59)

            query = ("SELECT\
                        ba.iddef_country,\
                        pr.property_code,\
                        pr.iddef_property,\
                        CONCAT_WS(' ',\
                                bc.title,\
                                bc.first_name,\
                                bc.last_name) AS guest_name,\
                        bc.email AS guest_email,\
                        CONCAT_WS('-', bc.dialling_code, bc.phone_number) AS guest_phone,\
                        bhr.iddef_room_type AS room_type_id,\
                        CONCAT_WS('-', rtc.room_description, rtc.room_code) AS room_type,\
                        pr.trade_name AS hotel_name,\
                        bhr.idop_rate_plan AS id_rate_plan,\
                        rtp.code AS rate_plan,\
                        bs.name as book_status,\
                        bs.description as book_status_description,\
                        bh.*\
                    FROM\
                        book_hotel bh\
                            JOIN\
                        book_hotel_room bhr ON bh.idbook_hotel = bhr.idbook_hotel\
                            AND bhr.estado = 1\
                            JOIN\
                        def_property pr ON pr.iddef_property = bh.iddef_property\
                            JOIN\
                        book_customer_hotel bch ON bch.idbook_hotel = bh.idbook_hotel\
                            AND bch.estado = 1\
                            JOIN\
                        book_customer bc ON bc.idbook_customer = bch.idbook_customer\
                            JOIN\
                        def_room_type_category rtc ON rtc.iddef_room_type_category = bhr.iddef_room_type\
                            JOIN\
                        book_status bs ON bs.idbook_status = bh.idbook_status\
                            JOIN\
                        book_address ba ON ba.idbook_customer = bc.idbook_customer\
                    		JOIN\
                    	op_rateplan rtp ON rtp.idop_rateplan = bhr.idop_rate_plan\
                    WHERE\
                        bh.estado = 1")

            if len(iddef_property) != 0 and len(idbook_status) != 0:
                if idbook_status[0] == 2 : 
                    book_hotel = db.session.execute((query +" AND CONVERT_TZ(bh.cancelation_date, '+00:00', '-05:00') BETWEEN '{from_date}' and '{to_date}'\
                        AND bh.idbook_status in {idbook_status} AND bh.iddef_property in {iddef_property};").format(from_date= from_date, to_date= to_date, idbook_status = tuple(idbook_status), iddef_property = tuple(iddef_property))).fetchall()
                    print("1")
                if idbook_status[0] == 5:
                    book_hotel = db.session.execute((query +" AND CONVERT_TZ(bh.modification_date_booking, '+00:00', '-05:00') BETWEEN '{from_date}' and '{to_date}'\
                        AND bh.idbook_status in {idbook_status} AND bh.iddef_property in {iddef_property};").format(from_date= from_date, to_date= to_date, idbook_status = tuple(idbook_status), iddef_property = tuple(iddef_property))).fetchall()
                    print("1.1")
                if idbook_status[0] != 2 and idbook_status[0] != 5:
                    book_hotel = db.session.execute((query +" AND CONVERT_TZ(bh.fecha_creacion, '+00:00', '-05:00') BETWEEN '{from_date}' AND '{to_date}'\
                        AND bh.idbook_status in {idbook_status} AND bh.iddef_property in {iddef_property};").format(from_date= from_date, to_date= to_date, idbook_status = tuple(idbook_status), iddef_property = tuple(iddef_property))).fetchall()
                    print("1.2")

            if len(iddef_property) != 0 and len(idbook_status) == 0:
                    book_hotel = db.session.execute((query +" AND CONVERT_TZ(bh.fecha_creacion, '+00:00', '-05:00') BETWEEN '{from_date}' AND '{to_date}'\
                        AND bh.iddef_property in {iddef_property};").format(from_date= from_date, to_date= to_date, idbook_status = tuple(idbook_status), iddef_property = tuple(iddef_property))).fetchall()
                    print("2")

            if len(idbook_status) != 0 and len(iddef_property) == 0:
                if idbook_status[0] != 2 and  idbook_status[0] != 5:
                    book_hotel = db.session.execute((query +" AND CONVERT_TZ(bh.fecha_creacion, '+00:00', '-05:00') BETWEEN '{from_date}' AND '{to_date}'\
                        AND bh.idbook_status in {idbook_status};").format(from_date= from_date, to_date= to_date, idbook_status = tuple(idbook_status), iddef_property = tuple(iddef_property))).fetchall()
                    print("3")
                if idbook_status[0] == 2:
                    book_hotel = db.session.execute((query +" AND CONVERT_TZ(bh.cancelation_date, '+00:00', '-05:00') BETWEEN '{from_date}' and '{to_date}'\
                        AND bh.idbook_status in {idbook_status};").format(from_date= from_date, to_date= to_date, idbook_status = tuple(idbook_status), iddef_property = iddef_property)).fetchall()
                    print("3.1")
                if idbook_status[0] == 5:
                    book_hotel = db.session.execute((query +" AND CONVERT_TZ(bh.modification_date_booking, '+00:00', '-05:00') BETWEEN '{from_date}' and '{to_date}'\
                        AND bh.idbook_status in {idbook_status};").format(from_date= from_date, to_date= to_date, idbook_status = tuple(idbook_status), iddef_property = tuple(iddef_property))).fetchall()
                    print("3.2")

            if len(idbook_status) == 0 and len(iddef_property) == 0:
                    book_hotel = db.session.execute((query +" AND CONVERT_TZ(bh.fecha_creacion, '+00:00', '-05:00') BETWEEN '{from_date}' AND '{to_date}';").format(from_date = from_date, to_date = to_date)).fetchall()
                    print("4")
            count = 0
            for row in book_hotel:
                count += 1
                print(count)
            response = {
                "Code": 200,
                "Msg": "Success",
                "Error": False,
                "data": schema.dump(book_hotel, many = True)
            }
        except Exception as e:
            response = {
                "Code": 500,
                "Msg": str(e),
                "Error": True,
                "data":{}
            }
        return response