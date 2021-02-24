from config import db, base
from models.age_range import AgeRange as agModel
from models.age_code import AgeCode as acModel
from models.text_lang import TextLang as tlModel
from models.property import Property as prModel
from common.util import Util
from sqlalchemy import or_, and_

class AgeRangeService():
    @staticmethod
    def get_age_range_lang(iddef_property=None,lang_code=None,iddef_age_range=None,code=None):
        #se consulta traduccion por iddef_age_range o code
        iddef_age_code = 0
        if iddef_property is None:
            raise Exception("Se necesita la propiedad")

        if lang_code is None:
            lang_code = 'EN'

        if code is not None and iddef_age_range is None:
            data_age_code = acModel.query.get(code)
            iddef_age_code = data_age_code.iddef_age_code
        elif iddef_age_range:
            data_age_range = agModel.query.get(iddef_age_range)
            iddef_age_code = data_age_range.iddef_age_code

        #subquery = agModel.query.with_entities(agModel.iddef_age_range).join(prModel).filter(and_(prModel.iddef_property==iddef_property,\
        #agModel.iddef_age_range==iddef_age_range, agModel.estado==1)).subquery()

        data = tlModel.query.with_entities(tlModel.text).filter(tlModel.estado==1, \
            tlModel.table_name=='def_age_code', tlModel.attribute=='descripcion', \
            tlModel.lang_code==lang_code, tlModel.id_relation==iddef_age_code).scalar()
        
        return data
    
    @staticmethod
    def get_validate_age_range(iddef_property,age_from,age_to):
        #busqueda de registro que coicida con el rango
        data = agModel.query.filter(and_(agModel.iddef_property==iddef_property, \
        agModel.estado==1, \
        or_(and_(agModel.age_from<=age_from, agModel.age_to>=age_to),\
        or_(agModel.age_from.between(age_from, age_to), \
        agModel.age_to.between(age_from, age_to))))).all()

        return data
    
    @staticmethod
    def get_all_age_range(iddef_property):
        if iddef_property is None:
            return None

        data = agModel.query.with_entities(agModel.iddef_age_range, acModel.code, acModel.age_from, acModel.age_to)\
            .join(acModel)\
            .filter(agModel.iddef_property==iddef_property, agModel.estado==1)\
            .order_by(acModel.code.desc())\
            .all()
        
        return data