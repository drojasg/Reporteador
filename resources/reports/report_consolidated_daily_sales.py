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

class ReportConsolidatedDailySalesExcell(Resource):
    @api.representation(MIME)
    def post(self):
        params = request.get_json(force=True)
        params['doc_type'] = 'excell'

        #: Tu archivo xlsx
        xlsx_report = os.path.join(
            base.app_config("TMP_PATH"),
            "{}.xlsx".format("consolidated-daily-sales", get_bulk(charsize=7)),
        )

        html_report = os.path.join(
            base.app_config("TMP_PATH"),
            "{}.html".format("consolidated-daily-sales", get_bulk(charsize=7)),
        )

        pdf_report = os.path.join(
            base.app_config("TMP_PATH"),
            "{}.pdf".format("consolidated-daily-sales", get_bulk(charsize=7)),
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
        query = reportsData.consolidated_daily_sales(from_date = params['from_date'], to_date= params['to_date'], api= params['doc_type'])

        if params['doc_type'].upper() == 'API':
            return query

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

        data_sheet2 ={
            'Bookings' : [bookings],
            'Total room nights' : [total_room_nights],
            'Average daily rate on total roomnights': [round(average_daily_rate_on_total_room, 3)],
            'Average LOS': [round(average_LOS, 3)],
            'Total booking value (room only)': [round(total_booking_value, 3)]
        }

        def format(x):
            return "${:,.2f}".format(x)
        
        df['total_booking_value'] = df['total_booking_value'].apply(format)
        df['avg_daily_rate']= df['avg_daily_rate'].apply(format)

        df_sheet_2 = pd.DataFrame(data_sheet2,columns=['Bookings','Total room nights','Average daily rate on total roomnights', 'Average LOS', 'Total booking value (room only)'] )
        df_sheet_2 = df_sheet_2.T

        with pd.ExcelWriter(xlsx_report, engine='xlsxwriter') as writer:

            df.rename(columns=
            {
                'hotel_name':'Hotel name',
                'total_booking_value':'Total Booking Value (room only)',
                'bookings':'Bookings',
                'total_room_nights': 'Total room nights',
                'avg_daily_rate': 'Average daily rate on total room nights',
                'avg_los': 'Average LOS'
            }, inplace=True)

            workbook = writer.book

            #Agregamos una nueva Hoja(solo y solo si es necesario, de lo contrario, comentar este código)
            df_sheet_2.to_excel(writer, sheet_name="KPI", index=True, header = False)
            worksheet_2 = writer.sheets['KPI']
            worksheet_2.set_column('A:A', 51)
            #worksheet_2.autofilter('A2:B2')
            #merge_format = workbook.add_format({'bold': 15,'border': 1,'align': 'right','valign': 'vright','fg_color': 'white'})
            #worksheet_2.merge_range('A1:A5',merge_format)

            df.to_excel(writer, startrow=1, sheet_name="Data", index=False, header = True)
            title = 'Consolidated Daily Sales'
            worksheet = writer.sheets['Data']
            worksheet.set_column('A:F', 51)
            worksheet.autofilter('A1:F1')
            merge_format = workbook.add_format({'bold': 1,'border': 1,'align': 'center','valign': 'vcenter','fg_color': 'white'})
            #worksheet.merge_range('A1:G1', title, merge_format)
            workbook.close()

            #Obtenemos el response del bucket
            #upload_buck = self.upload_bucket(self,xlsx_report)
            #presigned_url = upload_buck["presigned_url"]

            if params['doc_type'].upper() == 'EXCELL':
                return send_file(xlsx_report, mimetype=MIME)

            dataFrame_html = df.rename(columns=
            {
                'hotel_name':'Hotel name',
                'total_booking_value':'Total Booking Value (room only)',
                'bookings':'Bookings',
                'total_room_nights': 'Total room nights',
                'avg_daily_rate': 'Average daily rate on total room nights',
                'avg_los': 'Average LOS'
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
                    # pdfkit.from_file(html_report, 'promotion_consolidated.pdf', options=options)
                    #pdf_layer.close()
                    #upload_buck = self.upload_bucket(self,pdf_report)

                    return send_file(pdf_report, mimetype=MIMEPDF)
            
            #pdf = pdfkit.from_file(html,'report_daily_sales_by_market.pdf')
            
            #return upload_buck

class ReportConsolidatedDailySalesPDF(Resource):
    @api.representation(MIME)
    def post(self):
        params = request.get_json(force=True)
        params['doc_type'] = 'pdf'

        #: Tu archivo xlsx
        xlsx_report = os.path.join(
            base.app_config("TMP_PATH"),
            "{}.xlsx".format("consolidated-daily-sales", get_bulk(charsize=7)),
        )

        html_report = os.path.join(
            base.app_config("TMP_PATH"),
            "{}.html".format("consolidated-daily-sales", get_bulk(charsize=7)),
        )

        pdf_report = os.path.join(
            base.app_config("TMP_PATH"),
            "{}.pdf".format("consolidated-daily-sales", get_bulk(charsize=7)),
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
        query = reportsData.consolidated_daily_sales(from_date = params['from_date'], to_date= params['to_date'], api= params['doc_type'])

        if params['doc_type'].upper() == 'API':
            return query

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

        data_sheet2 ={
            'Bookings' : [bookings],
            'Total room nights' : [total_room_nights],
            'Average daily rate on total room nights': [round(average_daily_rate_on_total_room, 3)],
            'Average LOS': [round(average_LOS, 3)],
            'Total booking value (room only)': [round(total_booking_value, 3)]
        }

        def format(x):
            return "${:,.2f}".format(x)
        
        df['total_booking_value'] = df['total_booking_value'].apply(format)
        df['avg_daily_rate']= df['avg_daily_rate'].apply(format)

        df_sheet_2 = pd.DataFrame(data_sheet2,columns=['Bookings','Total room nights','Average daily rate on total room nights', 'Average LOS', 'Total booking value (room only)'] )
        df_sheet_2 = df_sheet_2.T

        with pd.ExcelWriter(xlsx_report, engine='xlsxwriter') as writer:

            df.rename(columns=
            {
                'hotel_name':'Hotel name',
                'total_booking_value':'Total Booking Value (room only)',
                'bookings':'Bookings',
                'total_room_nights': 'Total room nights',
                'avg_daily_rate': 'Average daily rate on total room nights',
                'avg_los': 'Average LOS'
            }, inplace=True)

            workbook = writer.book

            #Agregamos una nueva Hoja(solo y solo si es necesario, de lo contrario, comentar este código)
            df_sheet_2.to_excel(writer, sheet_name="KPI", index=True, header = False)
            worksheet_2 = writer.sheets['KPI']
            worksheet_2.set_column('A:A', 51)
            #worksheet_2.autofilter('A2:B2')
            #merge_format = workbook.add_format({'bold': 15,'border': 1,'align': 'right','valign': 'vright','fg_color': 'white'})
            #worksheet_2.merge_range('A1:A5',merge_format)

            df.to_excel(writer, startrow=1, sheet_name="Data", index=False, header = True)
            title = 'Consolidated Daily Sales'
            #dataFrame_html = df.to_html(index=False, header = True)
            worksheet = writer.sheets['Data']
            worksheet.set_column('A:F', 51)
            worksheet.autofilter('A1:F1')
            merge_format = workbook.add_format({'bold': 1,'border': 1,'align': 'center','valign': 'vcenter','fg_color': 'white'})
            worksheet.merge_range('A1:G1', title, merge_format)
            workbook.close()

            #Obtenemos el response del bucket
            #upload_buck = self.upload_bucket(self,xlsx_report)
            #presigned_url = upload_buck["presigned_url"]

            if params['doc_type'].upper() == 'EXCELL':
                return send_file(xlsx_report, mimetype=MIME)
            
            dataFrame_html_general = pd.DataFrame(data_sheet2,\
            columns=['Bookings','Total room nights','Average daily rate on total room nights',\
            'Average LOS', 'Total booking value (room only)'] ).to_html(index=False, header = True)

            dataFrame_html = df.rename(columns=
            {
                'hotel_name':'Hotel name',
                'total_booking_value':'Total Booking Value (room only)',
                'bookings':'Bookings',
                'total_room_nights': 'Total room nights',
                'avg_daily_rate': 'Average daily rate on total room nights',
                'avg_los': 'Average LOS'
            }
            ).to_html(index=False, header = True)
            
            with open(html_report, 'w+b') as temp:
                html_layer = open(html_report, 'w')
                html_layer.write("<h1>{title}</h1>".format(title=title))
                #html_layer.write(dataFrame_html)
                html_layer.write("<div>{}</div>".format(dataFrame_html_general))
                html_layer.write("<div><br></div>")
                html_layer.write("<div>{}</div>".format(dataFrame_html))
                html_layer.close()
            

            if params['doc_type'].upper() == 'PDF':
                options = {
                    'page-size': 'A4',
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
                    # pdfkit.from_file(html_report, 'promotion_consolidated.pdf', options=options)
                    #pdf_layer.close()
                    #upload_buck = self.upload_bucket(self,pdf_report)

                    return send_file(pdf_report, mimetype=MIMEPDF)
            
            #pdf = pdfkit.from_file(html,'report_daily_sales_by_market.pdf')
            
            #return upload_buck

class ReportConsolidatedDailySalesApi(Resource):
    @api.representation(MIME)
    def post(self):
        params = request.get_json(force=True)
        params['doc_type'] = 'api'

        #: Tu archivo xlsx
        xlsx_report = os.path.join(
            base.app_config("TMP_PATH"),
            "{}.xlsx".format("consolidated-daily-sales", get_bulk(charsize=7)),
        )

        html_report = os.path.join(
            base.app_config("TMP_PATH"),
            "{}.html".format("consolidated-daily-sales", get_bulk(charsize=7)),
        )

        pdf_report = os.path.join(
            base.app_config("TMP_PATH"),
            "{}.pdf".format("consolidated-daily-sales", get_bulk(charsize=7)),
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
        query = reportsData.consolidated_daily_sales(from_date = params['from_date'], to_date= params['to_date'], api= params['doc_type'])

        if params['doc_type'].upper() == 'API':
            return query

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

        data_sheet2 ={
            'Bookings' : [bookings],
            'Total room nights' : [total_room_nights],
            'Average daily rate on total roomnights': [round(average_daily_rate_on_total_room, 3)],
            'Average LOS': [round(average_LOS, 3)],
            'Total booking value (room only)': [round(total_booking_value, 3)]
        }

        def format(x):
            return "${:,.2f}".format(x)
        
        df['total_booking_value'] = df['total_booking_value'].apply(format)
        df['avg_daily_rate']= df['avg_daily_rate'].apply(format)

        df_sheet_2 = pd.DataFrame(data_sheet2,columns=['Bookings','Total room nights','Average daily rate on total roomnights', 'Average LOS', 'Total booking value (room only)'] )
        df_sheet_2 = df_sheet_2.T

        with pd.ExcelWriter(xlsx_report, engine='xlsxwriter') as writer:

            df.rename(columns={
                'hotel_name':'Hotel name',
                'total_booking_value':'Total Booking Value (room only)',
                'bookings':'Bookings',
                'total_room_nights': 'Total room nights',
                'avg_daily_rate': 'Average daily rate on total room nights',
                'avg_los': 'Average LOS'
            }, inplace=True)

            workbook = writer.book

            #Agregamos una nueva Hoja(solo y solo si es necesario, de lo contrario, comentar este código)
            df_sheet_2.to_excel(writer, sheet_name="KPI", index=True, header = False)
            worksheet_2 = writer.sheets['KPI']
            worksheet_2.set_column('A:A', 51)
            #worksheet_2.autofilter('A2:B2')
            #merge_format = workbook.add_format({'bold': 15,'border': 1,'align': 'right','valign': 'vright','fg_color': 'white'})
            #worksheet_2.merge_range('A1:A5',merge_format)

            df.to_excel(writer, startrow=1, sheet_name="Data", index=False, header = True)
            title = 'Consolidated Daily Sales'
            #dataFrame_html = df.to_html(index=False, header = True)
            worksheet = writer.sheets['Data']
            worksheet.set_column('A:F', 51)
            worksheet.autofilter('A1:F1')
            merge_format = workbook.add_format({'bold': 1,'border': 1,'align': 'center','valign': 'vcenter','fg_color': 'white'})
            #worksheet.merge_range('A1:G1', title, merge_format)
            workbook.close()

            #Obtenemos el response del bucket
            #upload_buck = self.upload_bucket(self,xlsx_report)
            #presigned_url = upload_buck["presigned_url"]

            if params['doc_type'].upper() == 'EXCELL':
                return send_file(xlsx_report, mimetype=MIME)

            dataFrame_html = df.rename(columns=
            {
                'hotel_name':'Hotel name',
                'total_booking_value':'Total Booking Value (room only)',
                'bookings':'Bookings',
                'total_room_nights': 'Total room nights',
                'avg_daily_rate': 'Average daily rate on total room nights',
                'avg_los': 'Average LOS'
            }
            ).to_html(index=False, header = True)
            
            with open(html_report, 'w+b') as temp:
                html_layer = open(html_report, 'w')
                html_layer.write("<h1>{title}</h1>".format(title=title))
                html_layer.write(dataFrame_html)
                html_layer.close()
            

            if params['doc_type'].upper() == 'PDF':
                options ={
                'hotel_name':'Hotel',
                'total_booking_value':'Total Booking Value',
                'bookings':'Número de Bookings',
                'total_room_nights': 'Cuartos Noches',
                'avg_daily_rate': 'Tarifa promedio',
                'avg_los': 'Estancia promedio'
                }
                with open(pdf_report, 'w+b') as temp:
                    pdfkit.from_file(html_report, pdf_report, options=options)
                    #pdf_layer = open(pdf_report, 'w')
                    #pdf_layer.writelines("Performance by visitor country")
                    # pdfkit.from_file(html_report, pdf_report, options=options)
                    # pdfkit.from_file(html_report, 'promotion_consolidated.pdf', options=options)
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