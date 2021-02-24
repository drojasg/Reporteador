from config import db
from common.util import Util
from sqlalchemy import or_, and_, func
from datetime import datetime, timedelta
from resources.restriction.restricctionHelper import RestricctionFunction as resFuntions
from models.rateplan import RatePlan as rpModel
from models.rateplan_property import RatePlanProperty as rppModel
from models.rate_plan_rooms import RatePlanRooms as rtprModel
from models.rateplan_restriction import RatePlanRestriction as rpresModel
from resources.restriction.restriction_helper_v2 import Restrictions as resFuntions2

class Rateplans_Helper():

    def update_ratecode_rateplan(self,idrateplan,ratecode):
        update = False
        msg = "Success"

        try:
            rpdata = rpModel.query.get(idrateplan)
            rpdata.rate_code_base = ratecode
            db.session.commit()
        except Exception as update_error:
            msg = str(update_error)

        return update, msg
        

    def get_rateplan_info(self,rateplanId=None,rate_code=None,property_id=None,date_start=None,\
    date_end=None,market_id=None,bookin_window=False,only_one=True,only_rateplan=False,\
    country=None,validate_lead_time=False,roomid=None,validate_estado=True,language='en'):
        
        conditions = []

        if rate_code == "":
            raise Exception("Campo Rate Plan Code Vacio Favor de Validar")
        
        if property_id is None:
            raise Exception("Se necesita el codigo del la propiedad")

        if only_rateplan == False:
            #Se revisa su hay un "General_Restriction" de tipo "Apply"
            if date_start is not None and date_end is not None and market_id is not None:
                # restriction_details_apply = resFuntions.getRestrictionDetails(travel_window_start=date_start.strftime("%Y-%m-%d"), \
                #     travel_window_end=date_end.strftime("%Y-%m-%d"), restriction_by=6, restriction_type=4, market_targeting=market_id,
                #     geo_targeting_country=country)
                obj = resFuntions2(travel_window_start=date_start.strftime("%Y-%m-%d"), \
                    travel_window_end=date_end.strftime("%Y-%m-%d"), restriction_by=6, restriction_type=4, market_targeting=market_id,
                    geo_targeting_country=country)
                restriction_details_apply = obj.get_restriction_details()
            else:
                restriction_details_apply = []

            if restriction_details_apply is None or len(restriction_details_apply) == 0:
                raise Exception(Util.t(language, "rateplan_not_found"))
            else:
                list_ids_restrictions = [restriction_elem["iddef_restriction"] for restriction_elem in restriction_details_apply]

        if validate_estado == True:
            conditions.append(rpModel.estado==1)
            
        conditions.append(rpModel.id_sistema==1)
        conditions.append(rppModel.id_property==property_id)

        if rateplanId is not None:
            conditions.append(rpModel.idop_rateplan==rateplanId)

        if rate_code is not None:
            conditions.append(rpModel.code==rate_code)

        data = rpModel.query.join(rppModel, rppModel.id_rateplan==\
        rpModel.idop_rateplan).filter(and_(*conditions,rppModel.estado==1)).all()

        #Si el roomid existe se valida que el rateplan este mapeado con dicha habitacion
        if roomid is not None:
            rateplans_by_room = rpModel.query.join(rtprModel, rtprModel.id_rate_plan==\
            rpModel.idop_rateplan).filter(and_(rtprModel.id_room_type==roomid\
            ,rtprModel.estado==1)).all()

            rateplans_room = [element.idop_rateplan for element in rateplans_by_room]

            aux_rateplan_list = []
            for rateplans in data:
                if rateplans.idop_rateplan in rateplans_room:
                    aux_rateplan_list.append(rateplans)
            
            data = aux_rateplan_list
        
        if only_rateplan == False:
            list_ids_rateplans = [rateplan_elem.idop_rateplan for rateplan_elem in data]

            data_rateplan_restriction = rpresModel.query.filter(rpresModel.idop_rateplan.in_(list_ids_rateplans), rpresModel.iddef_restriction.in_(list_ids_restrictions), rpresModel.estado==1).all()
            ids_rateplans_filtered = [elem_rpr.idop_rateplan for elem_rpr in data_rateplan_restriction]

            data = [rateplan_elem for rateplan_elem in data if rateplan_elem.idop_rateplan in ids_rateplans_filtered]
        else:
            data_rateplan_restriction = []

        #Se valida el valor "lead_time" con la fecha de booking
        if validate_lead_time:
            new_data_list = []
            today = datetime.utcnow().date()
            for data_index, data_value in enumerate(data):
                date_booking_limit = date_start - timedelta(days=data_value.lead_time)
                if today <= date_booking_limit:
                    new_data_list.append(data[data_index])
            #Se sustituyen datos de variable data
            data = new_data_list

        if only_one and len(data) >= 1:
            data = data[0]

        if only_rateplan == False and (data is None or len(data_rateplan_restriction)==0):
            raise Exception(Util.t(language, "rateplan_not_found"))
        elif only_rateplan and data is None:
            raise Exception(Util.t(language, "rateplan_not_found"))

        return data