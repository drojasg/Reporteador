from flask import Flask, request
from flask_restful import Resource
from marshmallow import ValidationError

from config import db, base
from models.media import Media as MedModel, MediaSchema as MedSchema, MediaSchemaStatus
from models.media_banners import MediaBanners as Model, MediaBannersSchema as ModelSchema,\
MediaBannersUpdateSchema as UpdateModelSchema, MediaBannersGetSchema as GetModelSchema
from models.brand import Brand
from models.property import Property
from models.country import Country
from resources.market_segment.marketHelper import Market as FunctionsMark
from common.util import Util
from sqlalchemy import or_, and_, func
from datetime import datetime
import datetime as dates
import json

class MediaBannersService():
    #obtener banners
    def get_media_banners_by_parameters(self,property_code=None,lang_code=None,market=None,\
    booking_window=None,brand=None,country=None, pages=None, type_banner=None):
        data, conditions = [], []
        conditionsAnd01, conditionsAnd02 = [], []
        conditionsAnd11, conditionsAnd12, conditionsAnd13 = [], [], []
        conditionsAnd21, conditionsAnd22, conditionsAnd23 = [], [], []
        conditionsOr0, conditionsOr1, conditionsOr2, conditionsOr3,\
        conditionsOr4, conditionsOr5, conditionsOr6 = [], [], [], [], [], [], []
        conditionsAnd31, conditionsAnd32, conditionsAnd33 = [], [], []
        if property_code is not None and brand is not None:
            conditionsOr3.append(Model.brand_option==1)
            conditionsOr3.append(Model.brand_option==2)
            conditionsAnd31.append(or_(*conditionsOr3))
            conditionsAnd31.append(func.json_contains(Model.property_codes,property_code))
            conditionsOr6.append(and_(*conditionsAnd31))
            conditionsAnd32.append(Model.brand_option==0)
            conditionsAnd32.append(func.json_contains(Model.property_codes,property_code))
            conditionsOr6.append(and_(*conditionsAnd32))
            conditionsOr5.append(Model.brand_option==1)
            conditionsOr5.append(Model.brand_option==2)
            conditionsAnd33.append(or_(*conditionsOr5))
            conditionsAnd33.append(func.json_contains(Model.property_codes,'[]'))
            conditionsOr6.append(and_(*conditionsAnd33))
            conditions.append(or_(*conditionsOr6))
        elif property_code is not None and brand is None:
            conditions.append(func.json_contains(Model.property_codes,property_code))
            conditions.append(Model.brand_option==0)
        elif property_code is None and brand is not None:
            conditions.append(func.json_contains(Model.property_codes,'[]'))
            conditionsOr3.append(Model.brand_option==1)
            conditionsOr3.append(Model.brand_option==2)
            conditions.append(or_(*conditionsOr3))
        if lang_code is not None:
            conditionsAnd01.append(Model.lang_option==0)
            conditionsOr0.append(and_(*conditionsAnd01))
            conditionsAnd02.append(Model.lang_option==1)
            conditionsAnd02.append(func.json_contains(Model.lang_codes,lang_code))
            conditionsOr0.append(and_(*conditionsAnd02))
            conditions.append(or_(*conditionsOr0))
        if market is not None:
            conditionsAnd11.append(Model.market_option==0)
            conditionsOr1.append(and_(*conditionsAnd11))
            conditionsAnd12.append(Model.market_option==1)
            conditionsAnd12.append(func.json_contains(Model.marketing,market))
            conditionsOr1.append(and_(*conditionsAnd12))
            conditionsAnd13.append(Model.market_option==2)
            conditionsOr1.append(and_(*conditionsAnd13))
            conditions.append(or_(*conditionsOr1))
        if booking_window is not None:
            conditionsOr2.append(Model.booking_window_option==1)
            conditionsOr2.append(Model.booking_window_option==2)
            conditionsOr2.append(Model.booking_window_option==3)
            conditions.append(or_(*conditionsOr2))  
        if country is not None:
            conditionsAnd21.append(Model.geo_targeting_option==0)
            conditionsOr4.append(and_(*conditionsAnd21))
            conditionsAnd22.append(Model.geo_targeting_option==1)
            conditionsAnd22.append(func.json_contains(Model.geo_targeting_countries,country))
            conditionsOr4.append(and_(*conditionsAnd22))
            conditionsAnd23.append(Model.geo_targeting_option==2)
            conditionsOr4.append(and_(*conditionsAnd23))
            conditions.append(or_(*conditionsOr4))
        if pages is not None:
            conditions.append(func.json_contains(Model.pages,pages))
        
        if type_banner is not None:
            conditions.append(Model.type_banner==type_banner)
        
        schema = GetModelSchema(exclude=Util.get_default_excludes())
        data_media_banners = Model.query.filter(and_(*conditions,Model.estado==1))\
        .order_by(Model.order.asc())\
        .all()
        data_banners = schema.dump(data_media_banners, many = True)
        if len(data_banners) > 0:
            for banner in data_banners:
                band_market, band_stay, band_brand = True, True, True

                if market is not None:
                    if banner["market_option"] == 2:
                        band_market = False
                        for mk in banner["marketing"]:
                            if str(mk) in market:
                                band_market = True
                                    
                if booking_window is not None:
                    band_stay = False
                    if banner["booking_window_option"] == 1:
                        band_stay = True
                    elif banner["booking_window_option"] == 2:
                        band_stay = any(booking_window <= booking_date["start_date"] and booking_window <= booking_date["end_date"] for booking_date in banner["booking_window"])
                    elif banner["booking_window_option"] == 3:
                        band_stay = not any(booking_window <= booking_date["start_date"] and booking_window <= booking_date["end_date"] for booking_date in banner["booking_window"])
                
                if brand is not None:
                    band_brand = False
                    if banner["brand_option"] == 1:
                        band_brand = True if 'consolidado' in brand else False
                    if banner["brand_option"] == 0:
                        band_brand = True
                    if banner["brand_option"] == 2:
                        for itm_brand in banner["brand_codes"]:
                            if itm_brand in brand:
                                band_brand = True

                if band_market == True and band_stay == True and band_brand == True:
                    data.append(banner)

        return data
    
    def get_heads_and_footers_letter(self,lang_code=None,market_code=None,\
        booking_window=None,property_code=None,brand_code=None):

        data = {
            "heads": [],
            "footers": []
        }

        if lang_code is None:
            raise Exception("Lang Code no encontrado, favor de verificar")
        else:
            lang_code = '['+'"'+str(lang_code)+'"'+']'
        if booking_window is None:
            raise Exception("Booking Window no encontrado, favor de verificar")
        if market_code is not None:
            #country
            data_country = Country.query.filter(Country.country_code==market_code).first()
            id_country = data_country.iddef_country
            country_code = '['+''+str(id_country)+''+']'
            #market
            FunctionMark = FunctionsMark()
            msData = FunctionMark.getMarketInfo(market_code)
            id_market = msData.iddef_market_segment
            market_code = '['+''+str(id_market)+''+']'
        if property_code is not None:
            property_code = '['+'"'+str(property_code)+'"'+']'
        if brand_code is not None:
            brand_code = '['+'"'+str(brand_code)+'"'+']'

        data_heads = self.get_media_banners_by_parameters(property_code=property_code,\
        lang_code=lang_code,brand=brand_code, market=market_code, country=country_code,\
        booking_window=booking_window, type_banner=2)
        if len(data_heads) > 0:
            result_heads = []
            for banner in data_heads:
                for img in banner["ids_media"]:
                    data_media = MedModel.query.get(img["iddef_media"])
                    result_heads.append(data_media.url)
            data["heads"] = result_heads

        data_footers = self.get_media_banners_by_parameters(property_code=property_code,\
        lang_code=lang_code,brand=brand_code, market=market_code, country=country_code,\
        booking_window=booking_window, type_banner=3)
        if len(data_footers) > 0:
            result_footers = []
            for banner in data_footers:
                for img in banner["ids_media"]:
                    if img["category"] == "letter":
                        data_media = MedModel.query.get(img["iddef_media"])
                        if data_media is not None:
                            obj_footer = {
                                "url_img":data_media.url,
                                "href_banner":img["href_banner"]
                            }
                            result_footers.append(obj_footer)
            data["footers"] = result_footers

        return data