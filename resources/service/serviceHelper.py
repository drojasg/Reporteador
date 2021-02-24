from flask import Flask, request
from flask_restful import Resource
from marshmallow import ValidationError
from config import db, base
from models.service import ServiceSchema as ModelSchema, ServicePublicSchema as ModelPbSchema, SaveServiceSchema as SaveModelSchema, UpdateServiceSchema as UpdateModelSchema, GetDataTextLangSchema as GetDataTLSchema, GetDataContentSchema as GetDataContentSchema,GetPublicServiceSchema as GetPublicServSchema, Service as Model
from models.service_pricing_option import ServicePricingOptionSchema as SPOModelSchema, ServicePricingOption as SPOModel
from models.service_price import ServicePriceSchema as SPModelSchema,GetServicePriceSchema as GetSPModelSchema, ServicePrice as SPModel
from models.media_service import MediaServiceSchema as MSModelSchema, GetMediaServiceSchema as GetMSModelSchema, GetListMediaServiceSchema as GetListMSModelSchema, MediaService as MSModel
from models.service_restriction import ServiceRestriction as ServRestrModel, ServicerestrictionSchema as ServRestrModelSchema
from resources.text_lang.textlangHelper import Filter as textFuntions 
from resources.media_service import AdminMediaServiceList
from resources.restriction.restricctionHelper import RestricctionFunction as resFuntions
from resources.restriction.restriction_helper_v2 import Restrictions as resFuntions2
from common.util import Util
from sqlalchemy import or_, and_, case, func
import datetime
import time

class Search():
    #Filtrar servicios por lenguaje
    def get_service_by_lang(self,iddef_service,lang_code):
        textFuntion = textFuntions()
        data = Model.query.filter_by(iddef_service=iddef_service, estado=1).first()
        objt = {}
        elementos = ["Name","Teaser","Description","icon_description"]
        if data is not None:
            service_code = data.service_code
            for (y, z) in enumerate(elementos):
                data_element = textFuntion.getTextLangInfo('def_service',z,lang_code,iddef_service)
                if data_element is not None:
                    traslate_text = data_element.text
                else:
                    traslate_text = ''
                if z == "icon_description":
                    z = "name_html_icon"
                objt["iddef_service"] = iddef_service
                objt["service_code"] = service_code
                objt[z.lower()] = traslate_text

        return objt

    #Filtrar servicios por lenguaje con lista de elementos
    def get_service_by_lang_elements(self,iddef_service,elementos,lang_code):
        textFuntion = textFuntions()
        objt = {}
        data_elements = textFuntion.getTextLangAttributes('def_service',elementos,lang_code,iddef_service)
        if len(data_elements) > 0:
            for (y,z) in enumerate(elementos):
                text = ""
                filter_traslate = list(filter(lambda elem: elem.attribute==z,data_elements))
                if len(filter_traslate)>0:
                    text = filter_traslate[0].text
                if z == "icon_description":
                    z = "name_html_icon"
                objt[z.lower()] = text

        return objt
    
    #Filtrar servicios por booking
    def get_service_by_additional(self,services,date_start,date_end,id_market,id_property,totalRooms,totalPacks,market):
        data_srv, result = [], []
        #schema = ModelPbSchema(only=('iddef_service','service_code','html_icon', 'available_upon_request', 'auto_add_price_is_zero', 'price', 'service_info'),)
        #booking_window = datetime.datetime.now().date()
        totalNigths = date_end - date_start
        totalNigths = totalNigths.days
        if len(services ) > 0:
            data_srv = Model.query.filter(Model.iddef_service.in_(services), Model.estado==1, Model.iddef_property==id_property).all()
        else:
            data_serv2 = []
            #Obtenemos informacion de los servicios sin restrinccion
            data_serv_restr = ServRestrModel.query.with_entities(ServRestrModel.iddef_service).filter(ServRestrModel.estado == 1).subquery()
            data_serv = Model.query.filter(Model.iddef_service.notin_(data_serv_restr), Model.estado==1, Model.iddef_property==id_property).all()
            #Obtenemos informacion de las restrincciones
            # data_restrictions = resFuntions.getRestrictionDetails(travel_window_start=date_start.strftime("%Y-%m-%d"), \
            # travel_window_end=date_end.strftime("%Y-%m-%d"), restriction_by=6, restriction_type=4, market_targeting=id_market,
            # geo_targeting_country=market)
            obj = resFuntions2(travel_window_start=date_start.strftime("%Y-%m-%d"), \
            travel_window_end=date_end.strftime("%Y-%m-%d"), restriction_by=6, restriction_type=4, market_targeting=id_market,
            geo_targeting_country=market)
            data_restrictions = obj.get_restriction_details()
            if len(data_restrictions)>0:
                ids_restrictions = [restriction_elem["iddef_restriction"] for restriction_elem in data_restrictions] 
                #Obtenemos informacion de servicios con las restrincciones activas
                data_services_restrictions = ServRestrModel.query.with_entities(ServRestrModel.iddef_service)\
                .filter(ServRestrModel.iddef_restriction.in_(ids_restrictions), \
                ServRestrModel.estado == 1).subquery()
                data_serv2 = Model.query.filter(Model.iddef_service.in_(data_services_restrictions), Model.estado==1, Model.iddef_property==id_property).all()
                data_srv = data_serv + data_serv2
            else:
                data_srv = data_serv
        #Metodo para filtrar los types, options
        if len(data_srv) > 0:
            ids_service = [srv_elem.iddef_service for srv_elem in data_srv]
            result = self.get_service_pricing(ids_service,date_start.strftime("%Y-%m-%d"),date_end.strftime("%Y-%m-%d"),totalRooms,totalPacks,totalNigths)

        return result
    
    #Filtrar costo servicio
    def get_service_pricing(self,ids_service,date_start,date_end,total_rooms,total_paxs,total_days):
        schema = ModelPbSchema(only=('iddef_service','service_code','html_icon',\
            'available_upon_request', 'auto_add_price_is_zero', 'price', 'service_info',\
            'min_los', 'max_los', 'iddef_currency'),)

        #validar si es gratis el servicio
        info_case = case([
        (and_(Model.available_upon_request == 1, Model.auto_add_price_is_zero == 1,\
            SPModel.price ==0), 'INCLUDED'),
        (and_(Model.available_upon_request == 0, Model.auto_add_price_is_zero == 1,\
            SPModel.price ==0), 'INCLUDED'),
        (and_(Model.available_upon_request == 1, Model.auto_add_price_is_zero == 0,\
            SPModel.price != 0), 'NO FREE'),
        (and_(Model.available_upon_request == 0, Model.auto_add_price_is_zero == 0,\
            SPModel.price != 0), 'NO FREE'),
        (and_(Model.available_upon_request == 0, Model.auto_add_price_is_zero == 0,\
            SPModel.price ==0), 'FREE'),
        (and_(Model.available_upon_request == 1, Model.auto_add_price_is_zero == 1,\
            SPModel.price != 0), 'FREE'),
        (and_(Model.available_upon_request == 0, Model.auto_add_price_is_zero == 1,\
            SPModel.price !=0), 'FREE'),
        (and_(Model.available_upon_request == 1, Model.auto_add_price_is_zero == 0,\
            SPModel.price ==0), 'FREE'),
        ])

        #validar costo del servicio
        price = case([
        (and_(func.json_extract(Model.pricing_option, '$.option') == 1, Model.iddef_pricing_type == 1), SPModel.price),
        (and_(func.json_extract(Model.pricing_option, '$.option') == 2, Model.iddef_pricing_type == 1), SPModel.price),
        (and_(func.json_extract(Model.pricing_option, '$.option') == 3, Model.iddef_pricing_type == 2), SPModel.price * total_paxs),
        (and_(func.json_extract(Model.pricing_option, '$.option') == 4, Model.iddef_pricing_type == 2), SPModel.price),
        (and_(func.json_extract(Model.pricing_option, '$.option') == 5, Model.iddef_pricing_type == 3), (SPModel.price * total_paxs) * total_days ),
        (and_(func.json_extract(Model.pricing_option, '$.option') == 6, Model.iddef_pricing_type == 3), SPModel.price * total_paxs),
        (and_(func.json_extract(Model.pricing_option, '$.option') == 7, Model.iddef_pricing_type == 3), SPModel.price * total_days),
        (and_(func.json_extract(Model.pricing_option, '$.option') == 8, Model.iddef_pricing_type == 4), SPModel.price * total_rooms),
        (and_(func.json_extract(Model.pricing_option, '$.option') == 9, Model.iddef_pricing_type == 4), SPModel.price),
        (and_(func.json_extract(Model.pricing_option, '$.option') == 10, Model.iddef_pricing_type == 5), (SPModel.price * total_rooms) * total_days),
        (and_(func.json_extract(Model.pricing_option, '$.option') == 11, Model.iddef_pricing_type == 5), SPModel.price * total_rooms),
        (and_(func.json_extract(Model.pricing_option, '$.option') == 12, Model.iddef_pricing_type == 5), SPModel.price * total_days),
        ])

        data = Model.query.join(SPModel, Model.iddef_service == SPModel.iddef_service).add_columns(Model.iddef_service,\
        Model.service_code,Model.html_icon, Model.available_upon_request, Model.auto_add_price_is_zero,\
        SPModel.min_los, SPModel.max_los, (price).label("price"), Model.iddef_currency,\
        (info_case).label("service_info")).filter(and_(Model.iddef_service.in_(ids_service),\
            or_(and_(SPModel.min_los<=total_days,SPModel.max_los>=total_days),\
                        and_(SPModel.min_los<=total_days,SPModel.max_los==0),\
                        and_(SPModel.min_los==0,SPModel.max_los==0)),\
            or_(Model.is_same_price_all_dates==1,\
            and_(Model.is_same_price_all_dates==0,SPModel.start_date<=date_start,SPModel.end_date>=date_end)),\
        Model.estado==1)).all()

        if len(data) > 0:
            return schema.dump(data, many=True)

        return []