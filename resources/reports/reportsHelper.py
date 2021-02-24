from flask import Flask, request, jsonify, make_response,send_file
from flask_restful import Resource
from marshmallow import ValidationError
import googlemaps
import gmaps
#import png
import tempfile
import os
import random
import string
from matplotlib import pyplot as plt
import json
import base64
from models.reports import DailySalesSchema, DailySalesDetailedSchema,\
        DailyCancelationConsolidatedSchema, ConsolidatedSalesByRoomCategorySchema,\
        DailyReservationsListSchema, BookingOnHoldConsolidated, PromotionConsolidated,\
        ConsolidatedDailySales, GeneralConsolidatedDailySales
from config import db, base, app
from common.util import Util
from operator import itemgetter
from sqlalchemy import or_, and_, func
from datetime import datetime, timedelta
import datetime as dates
import types
import requests
import json
from datetime import datetime
from sqlalchemy import text
import copy
import pandas as pd
from pandas import DataFrame

MIMEIMG = "image/png"

class ReportsHelper():

    @staticmethod
    def daily_sales_by_market_and_date(from_date, to_date,api):

        from_date = datetime.strptime(from_date,'%Y-%m-%d %H:%M:%S')
        to_date = datetime.strptime(to_date,'%Y-%m-%d %H:%M:%S')

        from_date = from_date.replace(hour=00, minute=00, second=00)
        to_date = to_date.replace(hour=23, minute=59, second=59)

        query = text("SELECT aux.iddef_market_segment, aux.code,\
        FORMAT(aux.total_booking_value,2) AS total_booking_value,\
        aux.bookings, aux.total_room_nights,\
        ROUND(aux.total_booking_value/aux.total_room_nights, 2) AS avg_daily_rate,\
        ROUND(aux.total_room_nights/aux.bookings, 2) AS avg_los\
        FROM ( SELECT t.iddef_market_segment,s.code,\
        SUM(IF(t.iddef_currency=(SELECT c.iddef_currency FROM `def_currency` c WHERE c.currency_code='USD'), t.total, (t.total/t.exchange_rate))) AS total_booking_value,\
        SUM(t.total_rooms) AS bookings, \
        SUM(t.total_rooms*t.nights) AS total_room_nights    \
        FROM book_hotel t \
        INNER JOIN def_market_segment s ON s.iddef_market_segment = t.iddef_market_segment\
        WHERE t.estado = 1\
        AND t.idbook_status IN (4,5,7,8)\
        AND CONVERT_TZ(t.fecha_creacion, '+00:00', '-05:00') BETWEEN '{from_date}' AND '{to_date}'\
        GROUP BY t.iddef_market_segment\
        ) aux;".format(from_date= from_date,  to_date = to_date))
        
        
        #data  = db.session.execute(query).scalar()
        data = db.session.execute(query)

        schema = DailySalesDetailedSchema(many=True)

        if data:
            data = schema.dump(data)

        if api.upper() == 'EXCELL' or api.upper() == 'PDF':
            return query
        else:
            return data

    @staticmethod
    def daily_sales_detailed(from_date, to_date, id_market_segment, api):

        from_date = datetime.strptime(from_date,'%Y-%m-%d %H:%M:%S')
        to_date = datetime.strptime(to_date,'%Y-%m-%d %H:%M:%S')

        from_date = from_date.replace(hour=00, minute=00, second=00)
        to_date = to_date.replace(hour=23, minute=59, second=59)

        query = text( "SELECT aux.iddef_property, aux.property_code,\
        aux.trade_name, aux.channel_name,\
        FORMAT(aux.total_booking_value,2) AS total_booking_value,\
        aux.bookings,aux.total_room_nights,\
        ROUND(aux.total_booking_value/aux.total_room_nights, 2) AS avg_daily_rate,\
        ROUND(aux.total_room_nights/aux.bookings, 2) AS avg_los\
        FROM (\
        SELECT t.iddef_property,\
        p.property_code,\
        p.trade_name,\
        ch.name AS channel_name,\
        SUM(IF(t.iddef_currency=(SELECT c.iddef_currency FROM `def_currency` c \
        WHERE c.currency_code='USD'), t.total, (t.total/t.exchange_rate))) AS total_booking_value,\
        SUM(t.total_rooms) AS bookings, SUM(t.total_rooms*t.nights) AS total_room_nights\
        FROM book_hotel t INNER JOIN def_market_segment s ON s.iddef_market_segment = t.iddef_market_segment\
        INNER JOIN def_property p ON p.iddef_property = t.iddef_property\
        INNER JOIN def_channel ch ON ch.iddef_channel = t.iddef_channel\
                WHERE t.estado = 1 AND t.iddef_market_segment = {id_market_segment}\
                AND t.idbook_status IN (4,5,7,8)\
                AND CONVERT_TZ(t.fecha_creacion, '+00:00', '-05:00') BETWEEN '{from_date}' AND '{to_date}'\
                GROUP BY t.iddef_property, ch.iddef_channel\
        ) aux;".format(from_date= from_date,  to_date = to_date, id_market_segment = id_market_segment ))

        #data  = db.session.execute(query).scalar()
        data = db.session.execute(query)

        schema = DailySalesDetailedSchema(many=True)

        if data:
                data = schema.dump(data)

        if api.upper() == 'EXCELL' or api.upper() == 'PDF':
                return query
        else:
                return data

    @staticmethod
    def daily_cancelations_consolidated(from_date, to_date, api):

        from_date = datetime.strptime(from_date,'%Y-%m-%d %H:%M:%S')
        to_date = datetime.strptime(to_date,'%Y-%m-%d %H:%M:%S')

        from_date = from_date.replace(hour=00, minute=00, second=00)
        to_date = to_date.replace(hour=23, minute=59, second=59)

        query = text( "SELECT t.idbook_hotel, s.code, p.property_code, \
                        FORMAT(IF(t.iddef_currency=(SELECT c.iddef_currency FROM `def_currency` c \
                                WHERE c.currency_code='USD'), t.total, (t.total/t.exchange_rate)),2) \
                                AS total_booking_value, t.total_rooms AS bookings, (t.total_rooms*t.nights) AS total_room_nights,\
                        FORMAT(IF(t.iddef_currency=(SELECT c.iddef_currency FROM `def_currency` c WHERE c.currency_code='USD'), t.total,\
                        (t.total/t.exchange_rate))/t.total_rooms,2) AS avg_daily_rate, t.nights AS avg_los, t.fecha_creacion,\
                        t.cancelation_date FROM book_hotel t INNER JOIN def_market_segment s ON s.iddef_market_segment = t.iddef_market_segment \
                        INNER JOIN def_currency c ON c.iddef_currency = t.iddef_currency\
                        INNER JOIN def_property p ON p.iddef_property = t.iddef_property\
                        WHERE t.estado = 1 AND t.idbook_status IN (2,6)\
                        AND CONVERT_TZ(t.cancelation_date, '+00:00', '-05:00') BETWEEN '{from_date}' AND '{to_date}' ;".format(from_date= from_date,  to_date = to_date ))
        
        #data  = db.session.execute(query).scalar()
        data = db.session.execute(query)

        schema = DailyCancelationConsolidatedSchema(many=True)

        if data:
            data = schema.dump(data)

        if api.upper() == 'EXCELL' or api.upper() == 'PDF':
            return query
        else:
            return data

    @staticmethod
    def consolidated_sales_by_room_category(from_date, to_date, id_property ,api):

        from_date = datetime.strptime(from_date,'%Y-%m-%d %H:%M:%S')
        to_date = datetime.strptime(to_date,'%Y-%m-%d %H:%M:%S')

        from_date = from_date.replace(hour=00, minute=00, second=00)
        to_date = to_date.replace(hour=23, minute=59, second=59)

        #print(",".join(id_property))

        query = text( "SELECT aux.code, aux.property_code, aux.room_code, aux.reserved, \
                        aux.canceled, aux.bookings, aux.total_room_nights,\
                        FORMAT(aux.total_booking_value,2) AS total_booking_value,\
                        CONCAT(ROUND(aux.canceled*100/(aux.bookings),2),'%') AS cancelation_rate, \
                        ROUND(IF(aux.total_room_nights>0, aux.total_booking_value/aux.total_room_nights, 0), 2) AS avg_daily_rate, \
                        ROUND(IF(aux.reserved>0, aux.total_room_nights/aux.reserved, 0), 2) AS avg_los \
                        FROM( SELECT p.property_code,  rtc.room_code,\
                                SUM(IF(bh.idbook_status IN (4,5,7,8), 1, 0)) AS reserved, \
                                SUM(IF(bh.idbook_status IN (2,6), 1, 0)) AS canceled, \
                                SUM(IF(bh.idbook_status IN (2,4,5,6,7,8), 1, 0)) AS bookings,\
                                SUM(IF(bh.idbook_status IN (4,5,7,8), 1, 0)*bh.nights) AS total_room_nights,\
                                SUM(IF(bh.idbook_status IN (4,5,7,8), IF(bh.iddef_currency=(SELECT c.iddef_currency FROM `def_currency` c \
                                        WHERE c.currency_code='USD'), bhr.total, (bhr.total/bh.exchange_rate)), 0)) AS total_booking_value,\
                                        m.code\
                                FROM book_hotel_room bhr\
                                INNER JOIN book_hotel bh ON bhr.idbook_hotel = bh.idbook_hotel AND bh.estado = 1\
                                INNER JOIN def_property p ON p.iddef_property = bh.iddef_property\
                                INNER JOIN def_market_segment m ON m.iddef_market_segment = bh.iddef_market_segment\
                                INNER JOIN def_room_type_category rtc ON rtc.iddef_room_type_category = bhr.iddef_room_type \
                                WHERE bhr.estado=1\
                                and bh.iddef_property in ({property})\
                                AND CONVERT_TZ(bh.fecha_creacion, '+00:00', '-05:00') BETWEEN '{from_date}' AND '{to_date}' \
                        GROUP BY m.iddef_market_segment,p.iddef_property, rtc.iddef_room_type_category) aux;".format(from_date= from_date,  to_date = to_date, property= ",".join(id_property)))
        
        #data  = db.session.execute(query).scalar()
        #print(query)
        data = db.session.execute(query)

        schema = ConsolidatedSalesByRoomCategorySchema(many=True)

        if data:
            data = schema.dump(data)

        if api.upper() == 'EXCELL' or api.upper() == 'PDF':
            return query
        else:
            return data
    
    @staticmethod
    def daily_reservations_list(from_date, to_date, api):

        from_date = datetime.strptime(from_date,'%Y-%m-%d %H:%M:%S')
        to_date = datetime.strptime(to_date,'%Y-%m-%d %H:%M:%S')

        from_date = from_date.replace(hour=00, minute=00, second=00)
        to_date = to_date.replace(hour=23, minute=59, second=59)

        query = text( "SELECT p.property_code,\
                        IF(bhr.no_show = 1, 'No Show', bs.name) AS book_status,\
                        CONVERT_TZ(bh.fecha_creacion, '+00:00', '-05:00') AS booking_date,\
                        Date_format(bh.fecha_creacion, '%M') `month`,\
                        Date_format(bh.fecha_creacion, '%h:%i:%s %p') as 'time',\
                        bh.code_reservation,\
                        CONCAT_WS(' ', bc.first_name, bc.last_name) AS guest_name,\
                        badd.city AS guest_city,\
                        badd.state AS guest_state,\
                        bh.from_date AS arrival_date, bh.to_date AS departure_date,\
                        1 AS bookings,\
                        dc.currency_code,\
                        bh.device_request,\
                        dc2.name as country_name,\
                        dc2.country_code as country_ID,\
                        rtc.room_code,\
                        rtc.room_description AS room_name,\
                        bhr.adults,\
                        bhr.child,\
                        (bhr.adults + bhr.child) AS total_guest,\
                        rp.code AS rateplan_name,\
                        rp.rate_code_clever AS rate_code,\
                        bh.nights AS total_room_nights,\
                        bhr.rate_amount,\
                        IFNULL(voucher.promo_code,'') AS promo_code,\
                        bhr.promo_amount AS promo_code_amount,\
                        bhr.total AS total_room_value,\
                        ROUND(bhr.total/bh.nights, 2) AS avg_daily_rate,\
                        ROUND(bh.nights/1) AS avg_los,\
                        m.code AS user_market,\
                        bc.dialling_code,\
                        bc.phone_number AS guest_phone,\
                        bc.email AS guest_email,\
                        ch.name AS channel,\
                        IF(bh.modification_date_booking = '1900-01-01 00:00:00', bh.fecha_creacion, bh.modification_date_booking) as modified_date,\
                        IFNULL(aux_services.services, '') AS services,\
                        IF(\
                        (SELECT COUNT(*) AS num_past_bookings FROM book_hotel aux_bh\
                        INNER JOIN book_customer_hotel aux_bch ON aux_bch.idbook_hotel = aux_bh.idbook_hotel AND aux_bch.estado = 1\
                        INNER JOIN book_customer aux_bc ON aux_bc.idbook_customer = aux_bch.idbook_customer\
                        WHERE  aux_bc.email = bc.email\
                        AND aux_bh.fecha_creacion < bh.fecha_creacion\
                        AND aux_bh.estado = 1\
                        AND aux_bh.idbook_status IN (4,5,7,8)) > 0, 1, 0\
                        ) AS is_repetitive_customer,\
                        bh.device_request as user_device\
                        FROM book_hotel_room bhr\
                        INNER JOIN book_hotel bh ON bhr.idbook_hotel = bh.idbook_hotel AND bh.estado = 1\
                        INNER JOIN book_customer_hotel bch ON bch.idbook_hotel = bh.idbook_hotel AND bch.estado = 1\
                        INNER JOIN book_customer bc ON bc.idbook_customer = bch.idbook_customer\
                        INNER JOIN book_address badd ON badd.idbook_customer = bc.idbook_customer\
                        INNER JOIN def_property p ON p.iddef_property = bh.iddef_property\
                        INNER JOIN def_market_segment m ON m.iddef_market_segment = bh.iddef_market_segment\
                        INNER JOIN def_channel ch ON ch.iddef_channel = bh.iddef_channel\
                        INNER JOIN def_room_type_category rtc ON rtc.iddef_room_type_category = bhr.iddef_room_type\
                        INNER JOIN op_rateplan rp ON rp.idop_rateplan = bhr.idop_rate_plan\
                        INNER JOIN book_status bs ON bs.idbook_status = bh.idbook_status\
                        LEFT JOIN book_promo_code voucher ON voucher.idbook_hotel = bh.idbook_hotel AND voucher.estado = 1\
                        LEFT JOIN (\
                        SELECT bh.idbook_hotel,\
                        GROUP_CONCAT(DISTINCT bes.description SEPARATOR ', ') AS services\
                        FROM book_extra_service bes\
                        INNER JOIN book_hotel bh ON bh.idbook_hotel = bes.idbook_hotel\
                        GROUP BY bh.idbook_hotel\
                        ) aux_services ON aux_services.idbook_hotel = bh.idbook_hotel\
                        inner join def_currency dc on bh.iddef_currency  = dc.iddef_currency\
                        inner join def_country dc2 on bh.iddef_country  = dc2.iddef_country \
                        WHERE CONVERT_TZ(bh.fecha_creacion, '+00:00', '-05:00') BETWEEN '{from_date}' AND '{to_date}'\
                        AND bhr.estado = 1\
                        ORDER BY bh.idbook_hotel, bhr.idbook_hotel_room;".format(from_date= from_date,  to_date = to_date ))
        
        #data  = db.session.execute(query).scalar()
        #print(query)
        data = db.session.execute(query)

        schema = DailyReservationsListSchema(many=True)

        if data:
            data = schema.dump(data)

        if api.upper() == 'EXCELL' or api.upper() == 'PDF':
            return query
        else:
            return data

    @staticmethod
    def daily_cancelations_list(from_date, to_date, api):

        from_date = datetime.strptime(from_date,'%Y-%m-%d %H:%M:%S')
        to_date = datetime.strptime(to_date,'%Y-%m-%d %H:%M:%S')

        from_date = from_date.replace(hour=00, minute=00, second=00)
        to_date = to_date.replace(hour=23, minute=59, second=59)

        query = text( "SELECT p.property_code,bs.name AS book_status, bh.cancelation_date,\
                        CONVERT_TZ(bh.fecha_creacion, '+00:00', '-05:00') AS booking_date,\
                        bh.code_reservation, CONCAT_WS(' ', bc.first_name, bc.last_name) AS guest_name, \
                        bh.from_date AS arrival_date, bh.to_date AS departure_date, 1 AS bookings,\
                        rtc.room_code, bhr.adults,bhr.child, rp.code AS rateplan_name, rp.rate_code_clever AS rate_code,\
                        bh.nights AS total_room_nights, bhr.rate_amount, IFNULL(voucher.promo_code,'') AS promo_code, \
                        bhr.promo_amount AS promo_code_amount, bhr.total AS total_room_value,   ROUND(bhr.total/bh.nights, 2) AS avg_daily_rate,\
                        ROUND(bh.nights/1) AS avg_los, m.code AS user_market, bc.dialling_code, bc.phone_number AS guest_phone,\
                        bc.email AS guest_email, ch.name AS channel, IFNULL(aux_services.services, '') AS services,\
                        IF(\
                                (SELECT COUNT(*) AS num_past_bookings FROM book_hotel aux_bh \
                                INNER JOIN book_customer_hotel aux_bch ON aux_bch.idbook_hotel = aux_bh.idbook_hotel AND aux_bch.estado = 1\
                                INNER JOIN book_customer aux_bc ON aux_bc.idbook_customer = aux_bch.idbook_customer\
                                WHERE  aux_bc.email = bc.email\
                                AND aux_bh.fecha_creacion < bh.fecha_creacion\
                                AND aux_bh.estado = 1\
                                AND aux_bh.idbook_status IN (4,5,7,8)) > 0, 1, 0\
                                ) AS is_repetitive_customer\
                                FROM book_hotel_room bhr\
                                INNER JOIN book_hotel bh ON bhr.idbook_hotel = bh.idbook_hotel AND bh.estado = 1\
                                INNER JOIN book_customer_hotel bch ON bch.idbook_hotel = bh.idbook_hotel AND bch.estado = 1\
                                INNER JOIN book_customer bc ON bc.idbook_customer = bch.idbook_customer\
                                INNER JOIN def_property p ON p.iddef_property = bh.iddef_property\
                                INNER JOIN def_market_segment m ON m.iddef_market_segment = bh.iddef_market_segment\
                                INNER JOIN def_channel ch ON ch.iddef_channel = bh.iddef_channel\
                                INNER JOIN def_room_type_category rtc ON rtc.iddef_room_type_category = bhr.iddef_room_type\
                                INNER JOIN op_rateplan rp ON rp.idop_rateplan = bhr.idop_rate_plan\
                                INNER JOIN book_status bs ON bs.idbook_status = bh.idbook_status\
                                LEFT JOIN book_promo_code voucher ON voucher.idbook_hotel = bh.idbook_hotel AND voucher.estado = 1\
                                LEFT JOIN (\
                                SELECT bh.idbook_hotel,\
                                GROUP_CONCAT(DISTINCT bes.description SEPARATOR ', ') AS services\
                                FROM book_extra_service bes\
                                INNER JOIN book_hotel bh ON bh.idbook_hotel = bes.idbook_hotel\
                                GROUP BY bh.idbook_hotel\
                                ) aux_services ON aux_services.idbook_hotel = bh.idbook_hotel\
                                WHERE CONVERT_TZ(bh.fecha_creacion, '+00:00', '-05:00') BETWEEN '{from_date}' AND '{to_date}'\
                                AND bhr.estado = 1\
                                ORDER BY bh.idbook_hotel, bhr.idbook_hotel_room;".format(from_date= from_date,  to_date = to_date ))

        data = db.session.execute(query)
        schema = DailyReservationsListSchema(many=True)
        if data:
            data = schema.dump(data)

        if api.upper() == 'EXCELL' or api.upper() == 'PDF':
            return query
        else:
            return data

    @staticmethod
    def daily_cancelations_list(from_date, to_date, api):

        from_date = datetime.strptime(from_date,'%Y-%m-%d %H:%M:%S')
        to_date = datetime.strptime(to_date,'%Y-%m-%d %H:%M:%S')

        from_date = from_date.replace(hour=00, minute=00, second=00)
        to_date = to_date.replace(hour=23, minute=59, second=59)

        query = text( "SELECT p.property_code,bs.name AS book_status, bh.cancelation_date,\
                        CONVERT_TZ(bh.fecha_creacion, '+00:00', '-05:00') AS booking_date,\
                        bh.code_reservation, CONCAT_WS(' ', bc.first_name, bc.last_name) AS guest_name, \
                        bh.from_date AS arrival_date, bh.to_date AS departure_date, 1 AS bookings,\
                        rtc.room_code, bhr.adults,bhr.child, rp.code AS rateplan_name, rp.rate_code_clever AS rate_code,\
                        bh.nights AS total_room_nights, bhr.rate_amount, IFNULL(voucher.promo_code,'') AS promo_code, \
                        bhr.promo_amount AS promo_code_amount, bhr.total AS total_room_value,   ROUND(bhr.total/bh.nights, 2) AS avg_daily_rate,\
                        ROUND(bh.nights/1) AS avg_los, m.code AS user_market, bc.dialling_code, bc.phone_number AS guest_phone,\
                        bc.email AS guest_email, ch.name AS channel, IFNULL(aux_services.services, '') AS services,\
                        IF(\
                                (SELECT COUNT(*) AS num_past_bookings FROM book_hotel aux_bh \
                                INNER JOIN book_customer_hotel aux_bch ON aux_bch.idbook_hotel = aux_bh.idbook_hotel AND aux_bch.estado = 1\
                                INNER JOIN book_customer aux_bc ON aux_bc.idbook_customer = aux_bch.idbook_customer\
                                WHERE  aux_bc.email = bc.email\
                                AND aux_bh.fecha_creacion < bh.fecha_creacion \
                                AND aux_bh.estado = 1\
                                AND aux_bh.idbook_status IN (4,5,7,8)) > 0, 1, 0\
                                ) AS is_repetitive_customer,\
                                bhr.reason_cancellation\
                                FROM book_hotel_room bhr\
                                INNER JOIN book_hotel bh ON bhr.idbook_hotel = bh.idbook_hotel AND bh.estado = 1\
                                INNER JOIN book_customer_hotel bch ON bch.idbook_hotel = bh.idbook_hotel AND bch.estado = 1\
                                INNER JOIN book_customer bc ON bc.idbook_customer = bch.idbook_customer\
                                INNER JOIN def_property p ON p.iddef_property = bh.iddef_property\
                                INNER JOIN def_market_segment m ON m.iddef_market_segment = bh.iddef_market_segment\
                                INNER JOIN def_channel ch ON ch.iddef_channel = bh.iddef_channel\
                                INNER JOIN def_room_type_category rtc ON rtc.iddef_room_type_category = bhr.iddef_room_type\
                                INNER JOIN op_rateplan rp ON rp.idop_rateplan = bhr.idop_rate_plan\
                                INNER JOIN book_status bs ON bs.idbook_status = bh.idbook_status\
                                LEFT JOIN book_promo_code voucher ON voucher.idbook_hotel = bh.idbook_hotel AND voucher.estado = 1\
                                LEFT JOIN (SELECT bh.idbook_hotel, GROUP_CONCAT(DISTINCT bes.description SEPARATOR ', ') AS services \
                                FROM book_extra_service bes\
                                INNER JOIN book_hotel bh ON bh.idbook_hotel = bes.idbook_hotel\
                                GROUP BY bh.idbook_hotel) aux_services ON aux_services.idbook_hotel = bh.idbook_hotel\
                                        WHERE bh.idbook_status IN (2) AND bh.estado = 1 AND CONVERT_TZ(bh.cancelation_date, '+00:00', '-05:00') BETWEEN '{from_date}' AND '{to_date}'\
                                        AND bhr.estado = 1 ORDER BY bh.idbook_hotel, bhr.idbook_hotel_room;".format(from_date= from_date,  to_date = to_date ))

        #data  = db.session.execute(query).scalar()
        data = db.session.execute(query)

        schema = DailyReservationsListSchema(many=True)

        if data:
            data = schema.dump(data)

        if api.upper() == 'EXCELL' or api.upper() == 'PDF':
            return query
        else:
            return data

    @staticmethod
    def booking_on_hold_consolidated(from_date, to_date, api):
            
            from_date = datetime.strptime(from_date,'%Y-%m-%d %H:%M:%S')
            to_date = datetime.strptime(to_date,'%Y-%m-%d %H:%M:%S')

            from_date = from_date.replace(hour=00, minute=00, second=00)
            to_date = to_date.replace(hour=23, minute=59, second=59)

            query = text( "SELECT s.code, p.property_code, (IF(t.idbook_status=3,t.total_rooms,0)) AS bookings_onhold,\
                            (IF(t.idbook_status!=3,t.total_rooms,0)) AS total_bookings_convert,\
                            CONCAT(ROUND((IF(t.idbook_status!=3,t.total_rooms,0))*100/(t.total_rooms),2),'%') AS convert_rate,\
                            (t.total_rooms*t.nights) AS total_room_nights, t.total_rooms AS bookings,\
                            FORMAT(IF(t.iddef_currency=(SELECT c.iddef_currency FROM `def_currency` c WHERE c.currency_code='USD'), t.total, (t.total/t.exchange_rate))/(t.total_rooms*t.nights),2) AS avg_daily_rate, \
                            FORMAT(IF(t.iddef_currency=(SELECT c.iddef_currency FROM `def_currency` c WHERE c.currency_code='USD'), t.total, (t.total/t.exchange_rate)),2) AS total_booking_value,\
                            t.nights AS avg_los\
                            FROM book_hotel t\
                            INNER JOIN def_market_segment s ON s.iddef_market_segment = t.iddef_market_segment\
                            INNER JOIN def_currency c ON c.iddef_currency = t.iddef_currency\
                            INNER JOIN def_property p ON p.iddef_property = t.iddef_property\
                            WHERE t.estado = 1\
                            AND t.idbook_status IN (3,4,5,7,8)\
                            AND CONVERT_TZ(t.fecha_creacion, '+00:00', '-05:00') BETWEEN '{from_date}' AND '{to_date}';".format(from_date= from_date,  to_date = to_date ))

            #data  = db.session.execute(query).scalar()
            data = db.session.execute(query)

            schema = BookingOnHoldConsolidated(many=True)

            if data:
                    data = schema.dump(data)

            if api.upper() == 'EXCELL' or api.upper() == 'PDF':
                    return query
            else:
                    return data


    @staticmethod
    def promotion_consolidated(from_date, to_date, api):
            
            from_date = datetime.strptime(from_date,'%Y-%m-%d %H:%M:%S')
            to_date = datetime.strptime(to_date,'%Y-%m-%d %H:%M:%S')

            from_date = from_date.replace(hour=00, minute=00, second=00)
            to_date = to_date.replace(hour=23, minute=59, second=59)

            query = text( "SELECT p.property_code, s.code,\
            IFNULL(promo_code.name,'') AS promo_code_name,\
            IFNULL(voucher.promo_code,'') AS promo_code,\
            IFNULL(voucher_type.code,'') AS promo_code_type,\
            t.total_rooms AS bookings,(t.nights) AS total_room_nights,\
            FORMAT(IF(t.iddef_currency=(SELECT c.iddef_currency FROM `def_currency` c WHERE c.currency_code='USD'), t.total,\
            (t.total/t.exchange_rate))/(t.total_rooms*t.nights),2) AS avg_daily_rate, t.nights AS avg_los,\
            FORMAT(IF(t.iddef_currency=(SELECT c.iddef_currency FROM `def_currency` c WHERE c.currency_code='USD'), t.total,\
            (t.total/t.exchange_rate)),2) AS total_booking_value\
            FROM book_hotel t\
            INNER JOIN def_market_segment s ON s.iddef_market_segment = t.iddef_market_segment\
            INNER JOIN def_currency c ON c.iddef_currency = t.iddef_currency\
            INNER JOIN def_property p ON p.iddef_property = t.iddef_property\
            LEFT JOIN book_promo_code voucher ON voucher.idbook_hotel = t.idbook_hotel AND voucher.estado = 1\
            LEFT JOIN def_promo_code promo_code ON promo_code.code = voucher.promo_code AND promo_code.estado = 1\
            LEFT JOIN def_promotion_discount_type voucher_type ON voucher_type.iddef_promotion_discount_type = voucher.promo_code_type AND voucher_type.estado = 1\
            WHERE t.estado = 1\
            AND t.idbook_status IN (4,5,7,8)\
            AND CONVERT_TZ(t.fecha_creacion, '+00:00', '-05:00') BETWEEN '{from_date}' AND '{to_date}';".format(from_date= from_date,  to_date = to_date ))

            #data  = db.session.execute(query).scalar()
            data = db.session.execute(query)

            schema = PromotionConsolidated(many=True)

            if data:
                    data = schema.dump(data)

            if api.upper() == 'EXCELL' or api.upper() == 'PDF':
                    return query
            else:
                    return data
    @staticmethod
    def consolidated_daily_sales(from_date, to_date ,api):
            from_date = datetime.strptime(from_date,'%Y-%m-%d %H:%M:%S')
            to_date = datetime.strptime(to_date,'%Y-%m-%d %H:%M:%S')

            from_date = from_date.replace(hour=00, minute=00, second=00)
            to_date = to_date.replace(hour=23, minute=59, second=59)

            query = text("select aux.hotel_name, aux.total_booking_value, aux.bookings, aux.total_room_nights,\
            round(aux.total_booking_value/aux.total_room_nights, 2) as avg_daily_rate,\
            round(aux.total_room_nights/aux.bookings, 2) as avg_los\
            from (\
            select \
            p.short_name as hotel_name,\
            round(sum(if(t.iddef_currency = 1, t.total, t.total/t.exchange_rate)),2) as total_booking_value, \
            count(t.idbook_hotel) as bookings, \
            sum(t.total_rooms*t.nights) as total_room_nights\
            from book_hotel t \
            inner join def_property p on p.iddef_property = t.iddef_property\
            inner join def_currency c on c.iddef_currency = t.iddef_currency\
            WHERE t.estado = 1\
                AND t.idbook_status IN (4,5,7,8)\
                AND CONVERT_TZ(t.fecha_creacion, '+00:00', '-05:00') BETWEEN '{from_date}' AND '{to_date}' \
                GROUP BY t.iddef_property) aux;".format(from_date= from_date,  to_date = to_date ))
            
            data = db.session.execute(query)

            schema = ConsolidatedDailySales(many=True) #crear
            schemaGen = GeneralConsolidatedDailySales()

            if data:
                    #ejecutamos el query con pandas
                    df = pd.read_sql_query(query, db.engine)
                    
                    #sacamos los campos para los reportes:
                    bookings = df['bookings'].sum()
                    total_room_nights = df['total_room_nights'].sum()
                    total_booking_value = df['total_booking_value'].sum()
                    total_room_nights = df['total_room_nights'].sum()
                    if total_booking_value == 0 or total_room_nights == 0:
                        average_daily_rate_on_total_room = 0
                    else:
                        average_daily_rate_on_total_room = total_booking_value/total_room_nights
                    if total_booking_value == 0 or bookings == 0:
                        average_LOS = 0
                    else:    
                        average_LOS = total_room_nights/bookings

                    dataGeneral ={
                        "bookings" : bookings,
                        "total_room_nights" : total_room_nights,
                        "average_daily_rate_on_total_room": average_daily_rate_on_total_room,
                        "avg_los": average_LOS,
                        "total_booking_value": total_booking_value
                    }

                    data = {
                        "data_general": schemaGen.dump(dataGeneral),
                        "data_items":schema.dump(data)
                    }

            if api.upper() == 'EXCELL' or api.upper() == 'PDF':
                    return query
            else:
                    return data

    @staticmethod
    def get_bulk(charsize=12):
            """ Generate a Random hash """
            hash_list = string.ascii_uppercase + string.ascii_lowercase
            code = "".join(
                    random.SystemRandom().choice(hash_list) for _ in range(charsize)
            ) + str(datetime.now().strftime("%Y-%m-%d %H%M%S"))
            return code

    def get_img_map_bucket(lati, longi):

        def get_bulk(charsize=12):
            """ Generate a Random hash """
            hash_list = string.ascii_uppercase + string.ascii_lowercase
            code = "".join(
                random.SystemRandom().choice(hash_list) for _ in range(charsize)
            ) + str(datetime.now().strftime("%Y-%m-%d %H%M%S"))
            return code

        def upload_bucket(xlsx_report):
            files = {'filename': open(xlsx_report,'rb')}
            if base.environment == "pro":
                url = "/s3upload/clever-palace-prod/booking_reports"
            else:
                url = "/s3upload/clever-palace-dev/booking_reports"
            
            r = requests.post(base.get_url("apiAssetsPy") + "/s3upload/booking_engine", files=files)
            d = json.loads(r.text)

            if d["success"] == True:
                return d['data']#pre_signed_url #d['data']
            else:
                response = {
                    "success": False, 
                    "status": 500, 
                    "message": "Error Bucket: " + d["message"], 
                    "data": {}
                }
            return response

        img = os.path.join(
            base.app_config("TMP_PATH"),
            "{}".format("maps.png", get_bulk(charsize=7))
        )

        @app.after_request
        def after_request(response):
            try:
                #: Borrar el archivo
                if os.path.isfile(xlsx_report):
                    os.remove(xlsx_report)
            except Exception:
                pass
            return response


        api_key = "" #"AIzaSyDcCb0E1ydxpFn8efgdO3Zh2QpWjRAvGbY" #"9KCGswJxovrW851hFDAyRg" #"AIzaSyDcCb0E1ydxpFn8efgdO3Zh2QpWjRAvGbY"
        gmaps.configure(api_key=api_key)
        #cordinates = (20.979819,20.979819)
        url = "https://maps.googleapis.com/maps/api/staticmap?"
        center = '{la},{lo}'.format(la=lati,lo=longi)
        zoom=15
        url2 = (url + "center=" + center + "&zoom="+ str(zoom) + 
                "&size=400x400&key="+api_key+"&sensor=true&markers="+center)
    
        r = requests.get(url + "center=" + center + "&zoom=" +
                str(zoom) + "&size=400x400&key=" +api_key+"&sensor=false&markers="+center)
    
        f= open(img, 'wb')
        f.write(r.content)
        f.close()

        upload_buck = upload_bucket(img)

        return upload_buck
