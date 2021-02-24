from flask import Flask, request
from flask_restful import Resource
from marshmallow import ValidationError
from datetime import date, datetime, timedelta

from config import db, base
from models.reports_setting import ReportSettingSchema as ModelSchema, ReportSetting as Model
from models.reports import ReportsSchema as RModelSchema, Reports as RModel
from .reportssettingHelper import ReportSettingFunction as functionsRepSetting
from common.util import Util
from sqlalchemy import or_, and_, func
import datetime as dt

class ReportSetting(Resource):
    #api-reports-setting-get-by-id
    # @base.access_middleware
    def get(self, id):
        try:
            schema = ModelSchema(exclude=Util.get_default_excludes())
            data = Model.query.get(id)

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

    #api-reports-setting-put
    # @base.access_middleware
    def put(self, id):
        response = {}
        try:
            json_data = request.get_json(force=True)
            schema = ModelSchema(exclude=Util.get_default_excludes())
            data = schema.load(json_data)
            model = Model.query.get(id)
            user_data = base.get_token_data()
            user_name = user_data['user']['username']

            if model is None:
                return {
                    "Code": 404,
                    "Msg": "data not found",
                    "Error": True,
                    "data": {}
                }

            if request.json.get("subject_letter") != None:
                model.subject_letter = data["subject_letter"]
            if request.json.get("reports") != None:
                model.reports = data["reports"]
            if request.json.get("date_window") != None:
                model.date_window = data["date_window"]
            if request.json.get("date_window_custom") != None:
                model.date_window_custom = data["date_window_custom"]
            if request.json.get("subscription") != None:
                model.subscription = data["subscription"]
            if request.json.get("type_recurrence") != None:
                model.type_recurrence = data["type_recurrence"]
            if request.json.get("recurrence") != None:
                model.recurrence = data["recurrence"]
            if request.json.get("time") != None:
                model.time = data["time"]
            if request.json.get("emails") != None:
                model.emails = data["emails"]
            #model.estado = data["estado"]
            model.usuario_ultima_modificacion = user_name
            db.session.commit()

            response = {
                "Code": 200,
                "Msg": "Success",
                "Error": False,
                "data": schema.dump(model)
            }
        except ValidationError as error:
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

    #api-reports-setting-post
    # @base.access_middleware
    def post(self):
        response = {}
        try:
            json_data = request.get_json(force=True)
            schema = ModelSchema(exclude=Util.get_default_excludes())
            data = schema.load(json_data)
            user_data = base.get_token_data()
            user_name = user_data['user']['username']
            model = Model()

            model.subject_letter = data["subject_letter"]
            model.reports = data["reports"]
            model.date_window = data["date_window"]
            model.date_window_custom = data["date_window_custom"]
            model.subscription = data["subscription"]
            model.type_recurrence = data["type_recurrence"]
            model.recurrence = data["recurrence"]
            model.time = data["time"]
            model.emails = data["emails"]
            model.estado = 1
            model.usuario_creacion = user_name
            db.session.add(model)
            db.session.commit()

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

class ReportsSettingStatus(Resource):
    #api-reports-setting-delete
    # @base.access_middleware
    def put(self, id, status):
        response = {}
        try:
            schema = ModelSchema(exclude=Util.get_default_excludes())
            model = Model.query.get(id)
            user_data = base.get_token_data()
            user_name = user_data['user']['username']

            if model is None:
                return {
                    "Code": 404,
                    "Msg": "data not found",
                    "Error": True,
                    "data": {}
                }

            model.estado = status
            model.usuario_ultima_modificacion = user_name
            db.session.commit()

            response = {
                "Code": 200,
                "Msg": "Success",
                "Error": False,
                "data": schema.dump(model)
            }
        except ValidationError as error:
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

class ReportsSettingListSearch(Resource):
    #api-reports-setting-get-all
    # @base.access_middleware
    def get(self):
        try:

            isAll = request.args.get("all")

            data = Model()

            if isAll is not None:
                data = Model.query.all()
            else:
                data = Model.query.filter(Model.estado==1)

            schema = ModelSchema(exclude=Util.get_default_excludes(), many=True)

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
    
class ReportSettingFilter(Resource):
    #api-reports-setting-filter
    #@base.access_middleware
    def get(self):
        try:

            list_reports = []

            date_now = datetime.now().today().date()
            day_now = datetime.now().today().day
            time_now = datetime.now().time()
            time_now = dt.time(time_now.hour,time_now.minute,0)
            xdia = datetime.today().weekday()
            options = {
                "today":1,
                "yesterday":2,
                "tomorrow":3,
                "week_up_to_date":4,
                "last_week":5,
                "month_up_to_date":6,
                "last_30_days":7,
                "next_30_days":8,
                "last_month":9,
                "year_up_to_date":10,
                "custom_range":11,
                "week":{
                    "monday":0,
                    "saturday":5,
                    "sunday":6
                }
            }

            schema = ModelSchema(exclude=Util.get_default_excludes())

            #obtener reportes a enviar
            data = Model.query.filter(and_(Model.estado==1,\
            Model.subscription==1,or_(Model.type_recurrence==0,\
            and_(Model.type_recurrence==1,\
            func.json_contains(Model.recurrence,'['+''+str(xdia)+''+']')),\
            and_(Model.type_recurrence==2,\
            func.json_contains(Model.recurrence,'['+''+str(day_now)+''+']'))))).all()
            
            if len(data) > 0:
                for itm in data:
                    if itm.date_window == options["today"]:
                        start_date = date_now
                        end_date = date_now
                    elif itm.date_window == options["yesterday"]:
                        start_date = date_now - timedelta(days = 1)
                        end_date = date_now - timedelta(days = 1)
                    elif itm.date_window == options["tomorrow"]:
                        start_date = date_now + timedelta(days = 1)
                        end_date = date_now + timedelta(days = 1)
                    elif itm.date_window == options["week_up_to_date"]:
                        first_week = itm.date_window_custom["first_week"]
                        if first_week == options["week"]["saturday"]:
                            start_date = date_now - timedelta(days = xdia+2)
                        elif first_week == options["week"]["sunday"]:
                            start_date = date_now - timedelta(days = xdia+1)
                        elif first_week == options["week"]["monday"]:
                            start_date = date_now - timedelta(days = xdia)
                        end_date = date_now
                    elif itm.date_window == options["last_week"]:
                        first_week = itm.date_window_custom["first_week"]
                        if first_week == options["week"]["saturday"]:
                            start_date = date_now - timedelta(days = 7+xdia+2)
                        elif first_week == options["week"]["sunday"]:
                            start_date = date_now - timedelta(days = 7+xdia+1)
                        elif first_week == options["week"]["monday"]:
                            start_date = date_now - timedelta(days = 7)
                        end_date = date_now
                    elif itm.date_window == options["month_up_to_date"]:
                        start_date = dt.date(date_now.year,date_now.month,1)
                        end_date = date_now
                    elif itm.date_window == options["last_30_days"]:
                        start_date = date_now - timedelta(days = 30)
                        end_date = date_now
                    elif itm.date_window == options["next_30_days"]:
                        start_date = date_now
                        end_date = date_now + timedelta(days = 30)
                    elif itm.date_window == options["last_month"]:
                        start_date = dt.date(date_now.year,date_now.month-1,day_now)
                        end_date = date_now
                    elif itm.date_window == options["year_up_to_date"]:
                        start_date = dt.date(date_now.year,1,1)
                        end_date = date_now
                    elif itm.date_window == options["custom_range"]:
                        start_date = itm.date_window_custom["start_date"]
                        end_date = itm.date_window_custom["end_date"]

                    band_time = False
                        
                    if itm.time == time_now:
                        band_time = True

                    if band_time == True:    
                        objt = {
                            "subject_letter":itm.subject_letter,
                            "reports":itm.reports,
                            "emails": itm.emails,
                            "date_window_custom":{
                                "start_date":start_date.strftime("%Y-%m-%d"),
                                "end_date":end_date.strftime("%Y-%m-%d")
                            }
                        }
                        list_reports.append(objt)

            #enviar correos
            if len(list_reports) > 0:
                report = functionsRepSetting.reports_setting_leatter(list_reports,'mtun')

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
                    "data": list_reports
                }
        except Exception as e:
            response = {
                "Code": 500,
                "Msg": str(e),
                "Error": True,
                "data": {}
            }

        return response