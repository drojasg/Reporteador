#**********************
import pandas as pd
import tempfile
import pdfkit
from fpdf import FPDF
import xlwt
import os
import requests
import os
#************************
#****BOTO3***************#
import logging
import boto3
from botocore.exceptions import ClientError
#************************#
from flask import Flask, request
from flask_restful import Resource
from pandas import ExcelWriter
from pandas import DataFrame
from common.util import Util
from config import base, app, api
from flask import send_file
from sqlalchemy import text
import random
import string
import json
from datetime import datetime,timedelta
import xlsxwriter
from config import db
from resources.reports.reportsHelper import ReportsHelper as reportsData

MIME = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
MIMEPDF = "application/pdf"
def get_bulk(charsize=12):
    """ Generate a Random hash """
    hash_list = string.ascii_uppercase + string.ascii_lowercase
    code = "".join(
        random.SystemRandom().choice(hash_list) for _ in range(charsize)
    ) + str(datetime.now().strftime("%Y-%m-%d %H%M%S"))
    return code

class ReportDailyCancelationListExcell(Resource):
    @api.representation(MIME)
    def post(self):
        params = request.get_json(force=True)
        params['doc_type'] = 'excell'

        #: Tu archivo xlsx
        xlsx_report = os.path.join(
            base.app_config("TMP_PATH"),
            "{}.xlsx".format("daily_cancelations_list", get_bulk(charsize=7)),
        )

        html_report = os.path.join(
            base.app_config("TMP_PATH"),
            "{}.html".format("daily_cancelations_list", get_bulk(charsize=7)),
        )

        pdf_report = os.path.join(
            base.app_config("TMP_PATH"),
            "{}.pdf".format("daily_cancelations_list", get_bulk(charsize=7)),
        )

        #: Antes de la logica
        #: Se ejecuta despues de cada request
        @app.after_request
        def after_request(response):
            try:
                #: Borrar el archivo
                if os.path.isfile(xlsx_report, html_report, pdf_report):
                    os.remove(xlsx_report, html_report, pdf_report)
            except Exception:
                pass
            return response
        df = pd.DataFrame()

        #ejecutamos el query desde el helper
        query = reportsData.daily_cancelations_list(from_date = params['from_date'], to_date= params['to_date'], api= params['doc_type'])

        if params['doc_type'].upper() == 'API':
            return query

        #ejecutamos el query con pandas
        df = pd.read_sql_query(query, db.engine)

        

        with pd.ExcelWriter(xlsx_report, engine='xlsxwriter') as writer:

            df.rename(columns=
            {
                'code_reservation' : 'Clave de confirmación'  ,
                'dialling_code':'Código Telefónico',
                'child' : 'Niños'  ,
                'booking_date' : 'Fecha de reserva'  ,
                'rate_code' : 'Rate Code'  ,
                'promo_code' : 'Promo Code'  ,
                'avg_los' : 'Avg los'  ,
                'cancelation_date' : 'Fecha de cancelación'  ,
                'departure_date' : 'Fecha de Check-out'  ,
                'arrival_date' : 'Fecha de check-in'  ,
                'services' : 'Servicios extras'  ,
                'guest_email' : 'Email'  ,
                'guest_phone' : 'Telefono'  ,
                'total_room_nights' : 'Cuartos Noches'  ,
                'rateplan_name' : 'Rate Plan'  ,
                'reserved': 'Reserved',
                'is_repetitive_customer' : 'Cliente repetitivo'  ,
                'room_code' : 'Categoria de habitación'  ,
                'bookings' : 'Bookings'  ,
                'rate_amount' : 'Rate amount'  ,
                'adults' : 'Adultos'  ,
                'property_code' : 'Propiedad'  ,
                'guest_name' : 'Nombre cliente'  ,
                'total_room_value' : 'Total Booking Value'  ,
                'avg_daily_rate' : 'Tarifa promedio'  ,
                'reason_cancellation' : 'Motivo de Cancelación'  ,
                'book_status' : 'Book status'  ,
                'user_market' : 'Mercado / Pais'  ,
                'promo_code_amount' : 'Ingresos brutos con promo code'  ,
                'channel' : 'Canal',
            }
            )

            workbook = writer.book

            df.rename(columns= {
                'reserved': 'Reserved',
                'code_reservation' : 'Clave de confirmación'  ,
                'dialling_code':'Código Telefónico',
                'child' : 'Niños'  ,
                'booking_date' : 'Fecha de reserva'  ,
                'rate_code' : 'Rate Code'  ,
                'promo_code' : 'Promo Code'  ,
                'avg_los' : 'Avg los'  ,
                'cancelation_date' : 'Fecha de cancelación'  ,
                'departure_date' : 'Fecha de Check-out'  ,
                'arrival_date' : 'Fecha de check-in'  ,
                'services' : 'Servicios extras'  ,
                'guest_email' : 'Email'  ,
                'guest_phone' : 'Telefono'  ,
                'total_room_nights' : 'Cuartos Noches'  ,
                'rateplan_name' : 'Rate Plan'  ,
                'is_repetitive_customer' : 'Cliente repetitivo'  ,
                'room_code' : 'Categoria de habitación'  ,
                'bookings' : 'Bookings'  ,
                'rate_amount' : 'Rate amount',
                'adults' : 'Adultos'  ,
                'property_code' : 'Propiedad',
                'guest_name' : 'Nombre cliente'  ,
                'total_room_value' : 'Total Booking Value'  ,
                'avg_daily_rate' : 'Tarifa promedio'  ,
                'reason_cancellation' : 'Motivo de Cancelación'  ,
                'book_status' : 'Book status'  ,
                'user_market' : 'Mercado / Pais'  ,
                'promo_code_amount' : 'Ingresos brutos con promo code'  ,
                'channel' : 'Canal',
            }).to_excel(writer, startrow=1, sheet_name="Data", index=False, header = True)
            title = 'Daily Cancelations List'
            #dataFrame_html = df.to_html(index=False, header = True)
            worksheet = writer.sheets['Data']
            worksheet.set_column('A:F', 51)
            worksheet.autofilter('A1:G1')
            merge_format = workbook.add_format({'bold': 1,'border': 1,'align': 'center','valign': 'vcenter','fg_color': 'white'})
            worksheet.merge_range('A1:G1', title, merge_format)
            workbook.close()

            #Obtenemos el response del bucket
            #upload_buck = self.upload_bucket(self,xlsx_report)
            #presigned_url = upload_buck["presigned_url"]

            if params['doc_type'].upper() == 'EXCELL':
                return send_file(xlsx_report, mimetype=MIME)

            dataFrame_html = df.rename(columns= {
                'reserved': 'Reserved',
                'code_reservation' : 'Clave de confirmación'  ,
                'booking_date' : 'Fecha de reserva',
                'dialling_code':'Código Telefónico',
                'child' : 'Niños'  ,
                'rate_code' : 'Rate Code'  ,
                'promo_code' : 'Promo Code'  ,
                'avg_los' : 'Avg los'  ,
                'cancelation_date' : 'Fecha de cancelación'  ,
                'departure_date' : 'Fecha de Check-out'  ,
                'arrival_date' : 'Fecha de check-in'  ,
                'services' : 'Servicios extras'  ,
                'guest_email' : 'Email'  ,
                'guest_phone' : 'Telefono'  ,
                'total_room_nights' : 'Cuartos Noches'  ,
                'rateplan_name' : 'Rate Plan'  ,
                'is_repetitive_customer' : 'Cliente repetitivo'  ,
                'room_code' : 'Categoria de habitación'  ,
                'bookings' : 'Bookings'  ,
                'rate_amount' : 'Rate amount'  ,
                'adults' : 'Adultos'  ,
                'property_code' : 'Propiedad'  ,
                'guest_name' : 'Nombre cliente'  ,
                'total_room_value' : 'Total Booking Value'  ,
                'avg_daily_rate' : 'Tarifa promedio'  ,
                'reason_cancellation' : 'Motivo de Cancelación'  ,
                'book_status' : 'Book status'  ,
                'user_market' : 'Mercado / Pais'  ,
                'promo_code_amount' : 'Ingresos brutos con promo code'  ,
                'channel' : 'Canal',
            }
            ).to_html(index=False, header = True)
            
            with open(html_report, 'w+b') as temp:
                html_layer = open(html_report, 'w')
                html_layer.write("<h1>{title}</h1>".format(title=title))
                html_layer.write(dataFrame_html)
                html_layer.close()
            

            if params['doc_type'].upper() == 'PDF':
                options = {
                    'page-size': 'A4',
                    'orientation': 'Landscape',
                    'margin-top': '0.75in',
                    'margin-right': '0.75in',
                    'margin-bottom': '0.75in',
                    'margin-left': '0.75in',
                }
                with open(pdf_report, 'w+b') as temp:
                    pdfkit.from_file(html_report, pdf_report, options=options)
                    #pdf_layer = open(pdf_report, 'w')
                    #pdf_layer.writelines("Performance by visitor country")
                    # pdfkit.from_file(html_report, pdf_report, options=options)
                    # pdfkit.from_file(html_report, 'daily-sales-by-market.pdf', options=options)
                    #pdf_layer.close()
                    #upload_buck = self.upload_bucket(self,pdf_report)

                    return send_file(pdf_report, mimetype=MIMEPDF)
            
            #pdf = pdfkit.from_file(html,'report_daily_sales_by_market.pdf')
            
            #return upload_buck

class ReportDailyCancelationListPDF(Resource):
    @api.representation(MIME)
    def post(self):
        params = request.get_json(force=True)
        params['doc_type'] = 'pdf'

        #: Tu archivo xlsx
        xlsx_report = os.path.join(
            base.app_config("TMP_PATH"),
            "{}.xlsx".format("daily_cancelations_list", get_bulk(charsize=7)),
        )

        html_report = os.path.join(
            base.app_config("TMP_PATH"),
            "{}.html".format("daily_cancelations_list", get_bulk(charsize=7)),
        )

        pdf_report = os.path.join(
            base.app_config("TMP_PATH"),
            "{}.pdf".format("daily_cancelations_list", get_bulk(charsize=7)),
        )

        #: Antes de la logica
        #: Se ejecuta despues de cada request
        @app.after_request
        def after_request(response):
            try:
                #: Borrar el archivo
                if os.path.isfile(xlsx_report, html_report, pdf_report):
                    os.remove(xlsx_report, html_report, pdf_report)
            except Exception:
                pass
            return response
        df = pd.DataFrame()

        #ejecutamos el query desde el helper
        query = reportsData.daily_cancelations_list(from_date = params['from_date'], to_date= params['to_date'], api= params['doc_type'])

        if params['doc_type'].upper() == 'API':
            return query

        #ejecutamos el query con pandas
        df = pd.read_sql_query(query, db.engine)

        with pd.ExcelWriter(xlsx_report, engine='xlsxwriter') as writer:

            df.rename(columns={
                'reserved': 'Reserved',
                'code_reservation' : 'Clave de confirmación'  ,
                'booking_date' : 'Fecha de reserva'  ,
                'dialling_code':'Código Telefónico',
                'child' : 'Niños'  ,
                'rate_code' : 'Rate Code'  ,
                'promo_code' : 'Promo Code'  ,
                'avg_los' : 'Avg los'  ,
                'cancelation_date' : 'Fecha de cancelación'  ,
                'departure_date' : 'Fecha de Check-out'  ,
                'arrival_date' : 'Fecha de check-in'  ,
                'services' : 'Servicios extras'  ,
                'guest_email' : 'Email'  ,
                'guest_phone' : 'Telefono'  ,
                'total_room_nights' : 'Cuartos Noches'  ,
                'rateplan_name' : 'Rate Plan'  ,
                'is_repetitive_customer' : 'Cliente repetitivo'  ,
                'room_code' : 'Categoria de habitación'  ,
                'bookings' : 'Bookings'  ,
                'rate_amount' : 'Rate amount'  ,
                'adults' : 'Adultos'  ,
                'property_code' : 'Propiedad'  ,
                'guest_name' : 'Nombre cliente'  ,
                'total_room_value' : 'Total Booking Value'  ,
                'avg_daily_rate' : 'Tarifa promedio'  ,
                'reason_cancellation' : 'Motivo de Cancelación'  ,
                'book_status' : 'Book status'  ,
                'user_market' : 'Mercado / Pais'  ,
                'promo_code_amount' : 'Ingresos brutos con promo code'  ,
                'channel' : 'Canal',
            }
            )

            workbook = writer.book

            df.rename(columns={
                'reserved': 'Reserved',
                'code_reservation' : 'Clave de confirmación'  ,
                'booking_date' : 'Fecha de reserva'  ,
                'rate_code' : 'Rate Code'  ,
                'promo_code' : 'Promo Code'  ,
                'avg_los' : 'Avg los'  ,
                'cancelation_date' : 'Fecha de cancelación'  ,
                'departure_date' : 'Fecha de Check-out'  ,
                'arrival_date' : 'Fecha de check-in'  ,
                'services' : 'Servicios extras'  ,
                'guest_email' : 'Email'  ,
                'guest_phone' : 'Telefono'  ,
                'total_room_nights' : 'Cuartos Noches'  ,
                'rateplan_name' : 'Rate Plan'  ,
                'is_repetitive_customer' : 'Cliente repetitivo'  ,
                'room_code' : 'Categoria de habitación'  ,
                'bookings' : 'Bookings'  ,
                'rate_amount' : 'Rate amount'  ,
                'adults' : 'Adultos'  ,
                'property_code' : 'Propiedad'  ,
                'dialling_code':'Código Telefónico',
                'child' : 'Niños'  ,
                'guest_name' : 'Nombre cliente'  ,
                'total_room_value' : 'Total Booking Value'  ,
                'avg_daily_rate' : 'Tarifa promedio'  ,
                'reason_cancellation' : 'Motivo de Cancelación'  ,
                'book_status' : 'Book status'  ,
                'user_market' : 'Mercado / Pais'  ,
                'promo_code_amount' : 'Ingresos brutos con promo code'  ,
                'channel' : 'Canal',
            }).to_excel(writer, startrow=1, sheet_name="Data", index=False, header = True)
            title = 'Daily Cancelations List'
            #dataFrame_html = df.to_html(index=False, header = True)
            worksheet = writer.sheets['Data']
            worksheet.set_column('A:F', 51)
            worksheet.autofilter('A1:G1')
            merge_format = workbook.add_format({'bold': 1,'border': 1,'align': 'center','valign': 'vcenter','fg_color': 'white'})
            worksheet.merge_range('A1:G1', title, merge_format)
            workbook.close()

            #Obtenemos el response del bucket
            #upload_buck = self.upload_bucket(self,xlsx_report)
            #presigned_url = upload_buck["presigned_url"]

            if params['doc_type'].upper() == 'EXCELL':
                return send_file(xlsx_report, mimetype=MIME)

            dataFrame_html = df.rename(columns={
                'reserved': 'Reserved',
                'code_reservation' : 'Clave de confirmación'  ,
                'booking_date' : 'Fecha de reserva'  ,
                'rate_code' : 'Rate Code'  ,
                'promo_code' : 'Promo Code'  ,
                'avg_los' : 'Avg los'  ,
                'cancelation_date' : 'Fecha de cancelación'  ,
                'departure_date' : 'Fecha de Check-out'  ,
                'arrival_date' : 'Fecha de check-in'  ,
                'services' : 'Servicios extras'  ,
                'guest_email' : 'Email'  ,
                'guest_phone' : 'Telefono'  ,
                'total_room_nights' : 'Cuartos Noches'  ,
                'rateplan_name' : 'Rate Plan'  ,
                'is_repetitive_customer' : 'Cliente repetitivo'  ,
                'room_code' : 'Categoria de habitación'  ,
                'bookings' : 'Bookings'  ,
                'rate_amount' : 'Rate amount'  ,
                'adults' : 'Adultos'  ,
                'property_code' : 'Propiedad'  ,
                'dialling_code':'Código Telefónico',
                'child' : 'Niños'  ,
                'guest_name' : 'Nombre cliente'  ,
                'total_room_value' : 'Total Booking Value'  ,
                'avg_daily_rate' : 'Tarifa promedio'  ,
                'reason_cancellation' : 'Motivo de Cancelación'  ,
                'book_status' : 'Book status'  ,
                'user_market' : 'Mercado / Pais'  ,
                'promo_code_amount' : 'Ingresos brutos con promo code'  ,
                'channel' : 'Canal',
            }
            ).to_html(index=False, header = True)
            
            with open(html_report, 'w+b') as temp:
                html_layer = open(html_report, 'w')
                html_layer.write("<h1 style='text-align:center'>{title}</h1>".format(title=title))
                html_layer.write(dataFrame_html)

                html_layer.close()
            

            if params['doc_type'].upper() == 'PDF':
                options = {
                    'page-size': 'A1',
                    'title': 'title',
                    'header-left': 'hola',
                    'orientation': 'Landscape',
                    'margin-top': '0.1in',
                    'margin-right': '0.1in',
                    'margin-bottom': '0.1in',
                    'margin-left': '0.1in',
                }
                #toc = {'xsl-style-sheet': xlsx_report}
                with open(pdf_report, 'w+b') as temp:
                    pdfkit.from_file(html_report, pdf_report, options=options)
                    #pdf_layer = open(pdf_report, 'w')
                    #pdf_layer.writelines("Performance by visitor country")
                    # pdfkit.from_file(html_report, pdf_report, options=options)
                    # pdfkit.from_file(html_report, 'daily-sales-by-market.pdf', options=options)
                    #pdf_layer.close()
                    #upload_buck = self.upload_bucket(self,pdf_report)

                    return send_file(pdf_report, mimetype=MIMEPDF)
            
            #pdf = pdfkit.from_file(html,'report_daily_sales_by_market.pdf')
            
            #return upload_buck

class ReportDailyCancelationListApi(Resource):
    @api.representation(MIME)
    def post(self):
        params = request.get_json(force=True)
        params['doc_type'] = 'api'

        #: Tu archivo xlsx
        xlsx_report = os.path.join(
            base.app_config("TMP_PATH"),
            "{}.xlsx".format("daily_cancelations_list", get_bulk(charsize=7)),
        )

        html_report = os.path.join(
            base.app_config("TMP_PATH"),
            "{}.html".format("daily_cancelations_list", get_bulk(charsize=7)),
        )

        pdf_report = os.path.join(
            base.app_config("TMP_PATH"),
            "{}.pdf".format("daily_cancelations_list", get_bulk(charsize=7)),
        )

        #: Antes de la logica
        #: Se ejecuta despues de cada request
        @app.after_request
        def after_request(response):
            try:
                #: Borrar el archivo
                if os.path.isfile(xlsx_report, html_report, pdf_report):
                    os.remove(xlsx_report, html_report, pdf_report)
            except Exception:
                pass
            return response
        df = pd.DataFrame()

        #ejecutamos el query desde el helper
        query = reportsData.daily_cancelations_list(from_date = params['from_date'], to_date= params['to_date'], api= params['doc_type'])

        if params['doc_type'].upper() == 'API':
            return query

        #ejecutamos el query con pandas
        df = pd.read_sql_query(query, db.engine)

        with pd.ExcelWriter(xlsx_report, engine='xlsxwriter') as writer:

            df.rename(columns={
                'reserved': 'Reserved',
                'code_reservation' : 'Clave de confirmación'  ,
                'booking_date' : 'Fecha de reserva'  ,
                'rate_code' : 'Rate Code'  ,
                'promo_code' : 'Promo Code'  ,
                'avg_los' : 'Avg los'  ,
                'cancelation_date' : 'Fecha de cancelación'  ,
                'departure_date' : 'Fecha de Check-out'  ,
                'arrival_date' : 'Fecha de check-in'  ,
                'services' : 'Servicios extras'  ,
                'guest_email' : 'Email'  ,
                'guest_phone' : 'Telefono'  ,
                'total_room_nights' : 'Cuartos Noches'  ,
                'rateplan_name' : 'Rate Plan'  ,
                'is_repetitive_customer' : 'Cliente repetitivo'  ,
                'room_code' : 'Categoria de habitación'  ,
                'bookings' : 'Bookings'  ,
                'rate_amount' : 'Rate amount'  ,
                'adults' : 'Adultos'  ,
                'property_code' : 'Propiedad'  ,
                'dialling_code':'Código Telefónico',
                'child' : 'Niños'  ,
                'guest_name' : 'Nombre cliente'  ,
                'total_room_value' : 'Total Booking Value'  ,
                'avg_daily_rate' : 'Tarifa promedio'  ,
                'reason_cancellation' : 'Motivo de Cancelación'  ,
                'book_status' : 'Book status'  ,
                'user_market' : 'Mercado / Pais'  ,
                'promo_code_amount' : 'Ingresos brutos con promo code'  ,
                'channel' : 'Canal',
            }
            )

            workbook = writer.book

            df.rename(columns={
                'reserved': 'Reserved',
                'code_reservation' : 'Clave de confirmación'  ,
                'booking_date' : 'Fecha de reserva'  ,
                'rate_code' : 'Rate Code'  ,
                'promo_code' : 'Promo Code'  ,
                'avg_los' : 'Avg los'  ,
                'cancelation_date' : 'Fecha de cancelación'  ,
                'departure_date' : 'Fecha de Check-out'  ,
                'arrival_date' : 'Fecha de check-in'  ,
                'services' : 'Servicios extras'  ,
                'guest_email' : 'Email'  ,
                'guest_phone' : 'Telefono'  ,
                'total_room_nights' : 'Cuartos Noches'  ,
                'rateplan_name' : 'Rate Plan'  ,
                'is_repetitive_customer' : 'Cliente repetitivo'  ,
                'room_code' : 'Categoria de habitación'  ,
                'bookings' : 'Bookings'  ,
                'rate_amount' : 'Rate amount'  ,
                'adults' : 'Adultos'  ,
                'property_code' : 'Propiedad'  ,
                'dialling_code':'Código Telefónico',
                'child' : 'Niños'  ,
                'guest_name' : 'Nombre cliente'  ,
                'total_room_value' : 'Total Booking Value'  ,
                'avg_daily_rate' : 'Tarifa promedio'  ,
                'reason_cancellation' : 'Motivo de Cancelación'  ,
                'book_status' : 'Book status'  ,
                'user_market' : 'Mercado / Pais'  ,
                'promo_code_amount' : 'Ingresos brutos con promo code'  ,
                'channel' : 'Canal',
            }).to_excel(writer, startrow=1, sheet_name="Data", index=False, header = True)
            title = 'Daily Sales Details'
            #dataFrame_html = df.to_html(index=False, header = True)
            worksheet = writer.sheets['Data']
            worksheet.set_column('A:F', 51)
            worksheet.autofilter('A1:G1')
            merge_format = workbook.add_format({'bold': 1,'border': 1,'align': 'center','valign': 'vcenter','fg_color': 'white'})
            worksheet.merge_range('A1:G1', title, merge_format)
            workbook.close()

            #Obtenemos el response del bucket
            #upload_buck = self.upload_bucket(self,xlsx_report)
            #presigned_url = upload_buck["presigned_url"]

            if params['doc_type'].upper() == 'EXCELL':
                return send_file(xlsx_report, mimetype=MIME)

            dataFrame_html = df.rename(columns={
                'reserved': 'Reserved',
                'code_reservation' : 'Clave de confirmación'  ,
                'booking_date' : 'Fecha de reserva'  ,
                'rate_code' : 'Rate Code'  ,
                'promo_code' : 'Promo Code'  ,
                'avg_los' : 'Avg los'  ,
                'cancelation_date' : 'Fecha de cancelación'  ,
                'departure_date' : 'Fecha de Check-out'  ,
                'arrival_date' : 'Fecha de check-in'  ,
                'services' : 'Servicios extras'  ,
                'guest_email' : 'Email'  ,
                'guest_phone' : 'Telefono'  ,
                'total_room_nights' : 'Cuartos Noches'  ,
                'rateplan_name' : 'Rate Plan'  ,
                'is_repetitive_customer' : 'Cliente repetitivo'  ,
                'room_code' : 'Categoria de habitación'  ,
                'bookings' : 'Bookings'  ,
                'rate_amount' : 'Rate amount'  ,
                'adults' : 'Adultos'  ,
                'property_code' : 'Propiedad'  ,
                'dialling_code':'Código Telefónico',
                'child' : 'Niños'  ,
                'guest_name' : 'Nombre cliente'  ,
                'total_room_value' : 'Total Booking Value'  ,
                'avg_daily_rate' : 'Tarifa promedio'  ,
                'reason_cancellation' : 'Motivo de Cancelación'  ,
                'book_status' : 'Book status'  ,
                'user_market' : 'Mercado / Pais'  ,
                'promo_code_amount' : 'Ingresos brutos con promo code'  ,
                'channel' : 'Canal',
            }
            ).to_html(index=False, header = True)
            
            with open(html_report, 'w+b') as temp:
                html_layer = open(html_report, 'w')
                html_layer.write("<h1>{title}</h1>".format(title=title))
                html_layer.write(dataFrame_html)
                html_layer.close()
            

            if params['doc_type'].upper() == 'PDF':
                options = {
                    'page-size': 'A4',
                    'orientation': 'Landscape',
                    'margin-top': '0.75in',
                    'margin-right': '0.75in',
                    'margin-bottom': '0.75in',
                    'margin-left': '0.75in',
                }
                with open(pdf_report, 'w+b') as temp:
                    pdfkit.from_file(html_report, pdf_report, options=options)
                    #pdf_layer = open(pdf_report, 'w')
                    #pdf_layer.writelines("Performance by visitor country")
                    # pdfkit.from_file(html_report, pdf_report, options=options)
                    # pdfkit.from_file(html_report, 'daily-sales-by-market.pdf', options=options)
                    #pdf_layer.close()
                    #upload_buck = self.upload_bucket(self,pdf_report)

                    return send_file(pdf_report, mimetype=MIMEPDF)
            
            #pdf = pdfkit.from_file(html,'report_daily_sales_by_market.pdf')
            
            #return upload_buck

    @staticmethod
    def upload_bucket(self,xlsx_report):
        #Creamos la subida al bucket
            files = {'filename': open(xlsx_report,'rb')}
            #nombre del bucket: booking_reports
            #nombre de subcarpeta/booking_engine/reports
            if base.environment == "pro":
                url = "/s3upload/clever-palace-prod/booking_reports"
            else:
                url = "/s3upload/clever-palace-dev/booking_reports"
            r = requests.post(base.get_url("apiAssetsPy") + url, files=files)
            
            #validamos contra la respuesta del post
            d = json.loads(r.text)

            if d["success"] == True:
                #se remueve archivo temporal
                #pre_signed_url = self.create_presigned_url('clever-palace-dev',d['data']['ETag'],3600)
                return d['data']#pre_signed_url #d['data']
            else:
                #se remueve archivo temporal
                response = {
                "success": False, 
                "status": 500, 
                "message": "Error Bucket: " + d["message"], 
                "data": {}
                }
                return response

    @staticmethod
    def create_presigned_url(bucket_name, object_name, expiration=3600):
        """Generate a presigned URL to share an S3 object
        :param bucket_name: string
        :param object_name: string
        :param expiration: Time in seconds for the presigned URL to remain valid
        :return: Presigned URL as string. If error, returns None.
        """
        # Generate a presigned URL for the S3 object
        s3_client = boto3.client('s3')
        try:
            response = s3_client.generate_presigned_url('get_object',
                                                        Params={'Bucket': bucket_name,
                                                                'Key': object_name},
                                                        ExpiresIn=expiration)
        except ClientError as e:
            logging.error(e)
            return None
        # The response contains the presigned URL
        return send_file(xlsxwriter, mimetype=MIME)