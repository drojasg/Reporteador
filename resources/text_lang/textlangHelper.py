from flask import Flask, request
from flask_restful import Resource
from marshmallow import ValidationError
from config import db, base
from models.text_lang import TextLangSchema as TLModelSchema, TextLang as TextLModel
from common.util import Util
from sqlalchemy import or_, and_, case, func
import datetime

class Filter():

    #get textlang
    def getTextLangInfo(self,table_name,attribute,lang_code,id_relation):
        text = None
        data = TextLModel.query.filter(TextLModel.estado==1, \
        TextLModel.table_name==table_name, \
        TextLModel.attribute==attribute, \
        TextLModel.lang_code==lang_code, \
        TextLModel.id_relation==id_relation).first()

        if data is not None:
            text = data

        return text
    
    #get textlang
    def getTextLangAttributes(self,table_name,attributes,lang_code,id_relation):

        data = TextLModel.query.filter(TextLModel.estado==1, \
        TextLModel.table_name==table_name, \
        TextLModel.attribute.in_(attributes), \
        TextLModel.lang_code==lang_code, \
        TextLModel.id_relation==id_relation).all()

        return data

    def get_text_data(self,table_name=None,attribute=None,\
    lang_code=None,id_relation=None,all=False):
        data = None
        parameters = []

        if all == False:
            parameters.append(TextLModel.estado==1)

        if table_name is not None:
            if isinstance(table_name,str):
                parameters.append(TextLModel.table_name==table_name)

        if attribute is not None:
            if isinstance(attribute,str):
                parameters.append(TextLModel.attribute==attribute)

        if lang_code is not None:
            if isinstance(lang_code,str):
                parameters.append(TextLModel.lang_code==lang_code)

        if id_relation is not None:
            if isinstance(id_relation,int):
                parameters.append(TextLModel.id_relation==id_relation)

        data = TextLModel.query.filter(and_(*parameters)).all()

        return data