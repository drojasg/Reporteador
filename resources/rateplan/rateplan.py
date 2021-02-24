from flask import Flask, request
from flask_restful import Resource
from marshmallow import ValidationError
from datetime import datetime

from config import db, base
from models.rateplan import RatePlanSchema as ModelSchema, GetRatePlanSchema as GetModelSchema, GetPublicRatePlanSchema as GetPModelSchema , RatePlan as Model, PostRatePlanSchema as PostModelSchema, RatePlanIdSchema, RatePlanEstadoSchema, GetDataRatePlan2Schema as GetDRPModelSchema
from models.room_type_category import RoomTypeCategory
from models.cross_out_config import CrossOutConfig
from models.rate_plan_rooms import RatePlanRooms
from models.crossout_rate_plan import CrossoutRatePlan
from models.rateplan_restriction import RatePlanRestriction
from models.rateplan_property import RatePlanProperty
from models.property import Property
from models.text_lang import TextLang, GetTextLangSchema
from models.policy import Policy, GetPolicyPublicSchema as GetPPModelSchema, PolicyCPSchema as ModelCPSchema, PolicyGSchema as ModelGSchema, PolicyTSchema as ModelTSchema
from models.policy_cancellation_detail import PolicyCancellationDetail
from models.rateplan_policy import RatePlanPolicy
from models.age_code import AgeCode as ACModel
from models.room_type_category import RoomTypeCategorySchema as RTCModelSchema, RoomTypeCategory as RTCModel
#from resources.rates.RatesHelper import RatesFunctions as funtions
#from resources.rates.rates_helper_v2 import Quotes, Search
from resources.text_lang.textlangHelper import Filter as txtHelper
from resources.property.propertyHelper import FilterProperty as prHelper
from common.util import Util
from common.utilities import Utilities
from sqlalchemy import or_, and_, func
from common.public_auth import PublicAuth

class RatePlan(Resource):
    #api-rate-plan-get-by-id
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
                result = schema.dump(data)

                list_rooms = []
                list_rate_plan_rooms = list(filter(lambda rate_plan_room: rate_plan_room["estado"] == 1, result["rate_plan_rooms"])) #Se filtran solo los activos
                result.pop('rate_plan_rooms', None) # Se elimina tabla intermedia de la respuesta

                for rate_plan_room in list_rate_plan_rooms:
                    temp_room = None
                    temp_room = rate_plan_room["rooms"] if rate_plan_room["rooms"] is not None and rate_plan_room["rooms"]["estado"] == 1 else None
                    if temp_room is not None:
                        list_rooms.append(temp_room["iddef_room_type_category"])

                list_crossouts = []
                list_crossout_rate_plans = list(filter(lambda crossout_rate_plan: crossout_rate_plan["estado"] == 1, result["crossout_rate_plans"])) #Se filtran solo los activos
                result.pop('crossout_rate_plans', None) # Se elimina tabla intermedia de la respuesta

                for crossout_rate_plan in list_crossout_rate_plans:
                    temp_crossout = None
                    temp_crossout = crossout_rate_plan["crossouts"] if crossout_rate_plan["crossouts"] is not None and crossout_rate_plan["crossouts"]["estado"] else None
                    if temp_crossout is not None:
                        list_crossouts.append(temp_crossout)

                list_restrictions = []
                list_rateplan_restrictions = list(filter(lambda rateplan_restriction: rateplan_restriction["estado"] == 1, result["rateplan_restrictions"])) #Se filtran solo los activos
                result.pop('rateplan_restrictions', None) # Se elimina tabla intermedia de la respuesta

                for rateplan_restriction in list_rateplan_restrictions:
                    temp_restriction = None
                    temp_restriction = rateplan_restriction["restrictions"] if rateplan_restriction["restrictions"] is not None and rateplan_restriction["restrictions"]["estado"] else None
                    if temp_restriction is not None:
                        list_restrictions.append(temp_restriction)

                result["rooms"] = list_rooms #Se insertan valores de la relacion
                result["crossouts"] = list_crossouts #Se insertan valores de la relacion
                result["restrictions"] = list_restrictions #Se insertan valores de la relacion

                text_lang_schema = GetTextLangSchema()
                text_lang = TextLang.query.filter(TextLang.id_relation==id,TextLang.table_name=="op_rateplan",TextLang.attribute=="commercial_name",
                    TextLang.estado==1).all()
                result["text_langs"] = text_lang_schema.dump(text_lang, many=True)

                rate_plan_properties = Property.query.join(RatePlanProperty, Property.iddef_property == RatePlanProperty.id_property)\
                .filter(RatePlanProperty.id_rateplan==id, RatePlanProperty.estado==1).all()
                result["properties"] = [rpp.iddef_property for rpp in rate_plan_properties]

                rate_plan_policies = Policy.query.join(RatePlanPolicy, Policy.iddef_policy == RatePlanPolicy.iddef_policy)\
                .filter(RatePlanPolicy.idop_rateplan==id, RatePlanPolicy.estado==1, Policy.estado==1).all()

                result["policy_penalty"] = [rppol.iddef_policy for rppol in rate_plan_policies if rppol.iddef_policy_category == 1]
                result["policy_guaranty"] = [rppol.iddef_policy for rppol in rate_plan_policies if rppol.iddef_policy_category == 2]
                result["policy_tax"] = [rppol.iddef_policy for rppol in rate_plan_policies if rppol.iddef_policy_category == 3]

                #result["policies"] = [rppol.iddef_policy for rppol in rate_plan_policies]

                response = {
                    "Code": 200,
                    "Msg": "Success",
                    "Error": False,
                    "data": result
                }
        except Exception as e:
            response = {
                "Code": 500,
                "Msg": str(e),
                "Error": True,
                "data": {}
            }

        return response

    #api-rate-plan-put
    # @base.access_middleware
    def put(self, id):
        response = {}
        try:
            json_data = request.get_json(force=True)
            schema = GetModelSchema(exclude=Util.get_default_excludes())
            schema_request = RatePlanIdSchema(exclude=Util.get_default_excludes())
            data = schema_request.load(json_data)
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
            if request.json.get("id_sistema") != None:
                model.code = data["id_sistema"]
            # if request.json.get("id_market_segment") != None:
            # model.id_market_segment = 1 #Eliminar
            if request.json.get("code") != None:
                model.code = data["code"]
            # if request.json.get("booking_window_start") != None:
            #     model.booking_window_start = data["booking_window_start"]
            # if request.json.get("booking_window_end") != None:
            #     model.booking_window_end = data["booking_window_end"]
            # if request.json.get("travel_window_start") != None:
            # model.travel_window_start = "1900-01-01" #Eliminar
            # if request.json.get("travel_window_end") != None:
            # model.travel_window_end = "1900-01-01" #Eliminar
            if request.json.get("lead_time") != None:
                model.lead_time = data["lead_time"]
            if request.json.get("estado") != None:
                model.estado = data["estado"]
            if request.json.get("currency_code") != None:
                model.currency_code = data["currency_code"]
            if request.json.get("rate_code_clever") != None:
                model.rate_code_clever = data["rate_code_clever"]
            if request.json.get("refundable") != None:
                model.refundable = data["refundable"]
            if request.json.get("rooms") != None:
                if(len(model.rate_plan_rooms) == 0):
                    for id_room in data["rooms"]:
                        model_rate_plan_room = RatePlanRooms()
                        model_rate_plan_room.id_room_type = id_room
                        model_rate_plan_room.estado = 1
                        model_rate_plan_room.usuario_creacion = user_name
                        model.rate_plan_rooms.append(model_rate_plan_room)
                else:
                    # Se identifican elementos nuevos
                    rooms_to_insert = []
                    for id_room in data["rooms"]:
                        #SELECT count(*) AS count_1 FROM op_rate_plan_rooms rate_plan_rooms.id_rate_plan = :id AND op_rate_plan_rooms.id_room_type = :id_room
                        count_rate_plan_rooms = RatePlanRooms.query.filter(RatePlanRooms.id_rate_plan==id, RatePlanRooms.id_room_type==id_room).with_entities(func.count()).scalar()
                        if int(count_rate_plan_rooms) == 0:
                            rooms_to_insert.append(id_room)

                    #Se identifican si los elementos están en la lista del request, posteriormente se activan o desactivan dependiendo del caso
                    for rate_plan_room_id, rate_plan_room_value in enumerate(model.rate_plan_rooms):
                        if(model.rate_plan_rooms[rate_plan_room_id].id_room_type in data["rooms"]):
                            if int(model.rate_plan_rooms[rate_plan_room_id].estado) == 0:
                                model.rate_plan_rooms[rate_plan_room_id].estado = 1
                                model.rate_plan_rooms[rate_plan_room_id].usuario_ultima_modificacion = user_name
                        else:
                            if int(model.rate_plan_rooms[rate_plan_room_id].estado) == 1:
                                model.rate_plan_rooms[rate_plan_room_id].estado = 0
                                model.rate_plan_rooms[rate_plan_room_id].usuario_ultima_modificacion = user_name

                    #Se insertan elementos nuevos
                    for id_room in rooms_to_insert:
                        model_rate_plan_room = RatePlanRooms()
                        model_rate_plan_room.id_room_type = id_room
                        model_rate_plan_room.estado = 1
                        model_rate_plan_room.usuario_creacion = user_name
                        model.rate_plan_rooms.append(model_rate_plan_room)


            if request.json.get("crossouts") != None:
                if(len(model.crossout_rate_plans) == 0):
                    for id_crossout in data["crossouts"]:
                        model_crossout_rate_plan = CrossoutRatePlan()
                        model_crossout_rate_plan.iddef_crossout = id_crossout
                        model_crossout_rate_plan.estado = 1
                        model_crossout_rate_plan.usuario_creacion = user_name
                        model.crossout_rate_plans.append(model_crossout_rate_plan)
                else:
                    # Se identifican elementos nuevos
                    crossouts_to_insert = []
                    for id_crossout in data["crossouts"]:
                        #*SELECT count(*) AS count_1 FROM op_rate_plan_rooms rate_plan_rooms.id_rate_plan = :id AND op_rate_plan_rooms.id_room_type = :id_room
                        count_crossout_rate_plan = CrossoutRatePlan.query.filter(CrossoutRatePlan.iddef_rate_plan==id, CrossoutRatePlan.iddef_crossout==id_crossout).with_entities(func.count()).scalar()
                        if count_crossout_rate_plan == 0:
                            crossouts_to_insert.append(id_crossout)

                    #Se identifican si los elementos están en la lista del request, posteriormente se activan o desactivan dependiendo del caso
                    for crossout_rate_plan_id, crossout_rate_plan_value in enumerate(model.crossout_rate_plans):
                        if(model.crossout_rate_plans[crossout_rate_plan_id].iddef_crossout in data["crossouts"]):
                            if model.crossout_rate_plans[crossout_rate_plan_id].estado == 0:
                                model.crossout_rate_plans[crossout_rate_plan_id].estado = 1
                                model.crossout_rate_plans[crossout_rate_plan_id].usuario_ultima_modificacion = user_name
                        else:
                            if int(model.crossout_rate_plans[crossout_rate_plan_id].estado) == 1:
                                model.crossout_rate_plans[crossout_rate_plan_id].estado = 0
                                model.crossout_rate_plans[crossout_rate_plan_id].usuario_ultima_modificacion = user_name

                    #Se insertan elementos nuevos
                    for id_crossout in crossouts_to_insert:
                        model_crossout_rate_plan = CrossoutRatePlan()
                        model_crossout_rate_plan.iddef_crossout = id_crossout
                        model_crossout_rate_plan.estado = 1
                        model_crossout_rate_plan.usuario_creacion = user_name
                        model.crossout_rate_plans.append(model_crossout_rate_plan)

            if request.json.get("restrictions") != None:
                if(len(model.rateplan_restrictions) == 0):
                    for id_restriction in data["restrictions"]:
                        model_rateplan_restriction = RatePlanRestriction()
                        model_rateplan_restriction.iddef_restriction = id_restriction
                        model_rateplan_restriction.estado = 1
                        model_rateplan_restriction.usuario_creacion = user_name
                        model.rateplan_restrictions.append(model_rateplan_restriction)
                else:
                    # Se identifican elementos nuevos
                    restrictions_to_insert = []
                    for id_restriction in data["restrictions"]:
                        #*SELECT count(*) AS count_1 FROM op_rate_plan_rooms rate_plan_rooms.id_rate_plan = :id AND op_rate_plan_rooms.id_room_type = :id_room
                        count_rateplan_restriction = RatePlanRestriction.query.filter(RatePlanRestriction.idop_rateplan==id, RatePlanRestriction.iddef_restriction==id_restriction).with_entities(func.count()).scalar()
                        if count_rateplan_restriction == 0:
                            restrictions_to_insert.append(id_restriction)

                    #Se identifican si los elementos están en la lista del request, posteriormente se activan o desactivan dependiendo del caso
                    for rateplan_restriction_id, rateplan_restriction_value in enumerate(model.rateplan_restrictions):
                        if(model.rateplan_restrictions[rateplan_restriction_id].iddef_restriction in data["restrictions"]):
                            if model.rateplan_restrictions[rateplan_restriction_id].estado == 0:
                                model.rateplan_restrictions[rateplan_restriction_id].estado = 1
                                model.rateplan_restrictions[rateplan_restriction_id].usuario_ultima_modificacion = user_name
                        else:
                            if int(model.rateplan_restrictions[rateplan_restriction_id].estado) == 1:
                                model.rateplan_restrictions[rateplan_restriction_id].estado = 0
                                model.rateplan_restrictions[rateplan_restriction_id].usuario_ultima_modificacion = user_name

                    #Se insertan elementos nuevos
                    for id_restriction in restrictions_to_insert:
                        model_rateplan_restriction = RatePlanRestriction()
                        model_rateplan_restriction.iddef_restriction = id_restriction
                        model_rateplan_restriction.estado = 1
                        model_rateplan_restriction.usuario_creacion = user_name
                        model.rateplan_restrictions.append(model_rateplan_restriction)


            model.usuario_ultima_modificacion = user_name
            db.session.flush()

            if request.json.get("text_langs") != None:
                list_text_langs_request = request.json.get("text_langs", [])
                list_text_lang_codes_request = [text_lang_obj["lang_code"] for text_lang_obj in list_text_langs_request if text_lang_obj["estado"]==1]
                list_text_langs_search = TextLang.query.filter(TextLang.id_relation==id,TextLang.table_name=="op_rateplan",TextLang.attribute=="commercial_name").all()
                # Se cambia a estado 0 cuando el text lang no esté en el listado usado en el request
                for md_text_lang_index, md_text_lang_value in enumerate(list_text_langs_search):
                    if md_text_lang_value.lang_code not in list_text_lang_codes_request:
                        list_text_langs_search[md_text_lang_index].estado = 0
                        db.session.flush()
                for text_lang in list_text_langs_request:
                    model_text_lang_search = TextLang.query.filter(TextLang.id_relation==id,TextLang.table_name=="op_rateplan",TextLang.attribute=="commercial_name",
                        TextLang.lang_code==text_lang["lang_code"]).first()
                    if(model_text_lang_search is not None):
                        model_text_lang_search.lang_code = text_lang["lang_code"]
                        model_text_lang_search.text = text_lang["text"]
                        model_text_lang_search.estado = text_lang["estado"]
                        db.session.flush()
                    else:
                        model_text_lang = TextLang()
                        model_text_lang.lang_code = text_lang["lang_code"]
                        model_text_lang.text = text_lang["text"]
                        model_text_lang.table_name = "op_rateplan"
                        model_text_lang.id_relation = model.idop_rateplan
                        model_text_lang.attribute = "commercial_name"
                        model_text_lang.estado = 1
                        db.session.add(model_text_lang)
                        db.session.flush()

            if request.json.get("properties") != None:
                model_properties_old = Property.query.join(RatePlanProperty, Property.iddef_property == RatePlanProperty.id_property)\
                .filter(RatePlanProperty.id_rateplan==id, Property.estado==1).all()
                if(len(model_properties_old) == 0):
                    for id_property_insert in data["properties"]:
                        model_rateplan_property = RatePlanProperty()
                        model_rateplan_property.id_rateplan = model.idop_rateplan
                        model_rateplan_property.id_property = id_property_insert
                        model_rateplan_property.estado = 1
                        model_rateplan_property.usuario_creacion = user_name
                        db.session.add(model_rateplan_property)
                        db.session.flush()
                else:
                    # Se identifican elementos nuevos
                    properties_to_insert = []
                    for id_property_element in data["properties"]:
                        #SELECT count(*) AS count_1 FROM op_rateplan_property op_rateplan_property.id_rateplan = :id AND op_rateplan_property.id_property = :id_property
                        count_rate_plan_properties= RatePlanProperty.query.filter(RatePlanProperty.id_rateplan==id, RatePlanProperty.id_property==id_property_element).with_entities(func.count()).scalar()
                        if int(count_rate_plan_properties) == 0:
                            properties_to_insert.append(id_property_element)

                    #Se identifican si los elementos están en la lista del request, posteriormente se activan o desactivan dependiendo del caso
                    list_rateplan_property = RatePlanProperty.query.filter(RatePlanProperty.id_rateplan==id)
                    for rate_plan_property_index, rate_plan_property_value in enumerate(list_rateplan_property):
                        if(list_rateplan_property[rate_plan_property_index].id_property in data["properties"]):
                            if int(list_rateplan_property[rate_plan_property_index].estado) == 0:
                                list_rateplan_property[rate_plan_property_index].estado = 1
                                list_rateplan_property[rate_plan_property_index].usuario_ultima_modificacion = user_name
                                db.session.flush()
                        else:
                            if int(list_rateplan_property[rate_plan_property_index].estado) == 1:
                                list_rateplan_property[rate_plan_property_index].estado = 0
                                list_rateplan_property[rate_plan_property_index].usuario_ultima_modificacion = user_name
                                db.session.flush()

                    #Se insertan elementos nuevos
                    for id_property_insert in properties_to_insert:
                        model_rateplan_property = RatePlanProperty()
                        model_rateplan_property.id_rateplan = model.idop_rateplan
                        model_rateplan_property.id_property = id_property_insert
                        model_rateplan_property.estado = 1
                        model_rateplan_property.usuario_creacion = user_name
                        db.session.add(model_rateplan_property)
                        db.session.flush()

            if request.json.get("policies") != None:
                model_policies_old = Policy.query.join(RatePlanPolicy, Policy.iddef_policy == RatePlanPolicy.iddef_policy)\
                .filter(RatePlanPolicy.idop_rateplan==id, Policy.estado==1).all()
                if(len(model_policies_old) == 0):
                    list_policies = Policy.query.filter(Policy.iddef_policy.in_(data["policies"])).all()
                    temp_list_categories = []
                    for policy_index, policy_value in enumerate(list_policies):
                        #Se valida que todas las politicas sean de categorias diferentes
                        # if(policy_value.iddef_policy_category in temp_list_categories):
                        #     raise Exception("Duplicate Policy Category, Categories needs to be different")
                        model_rateplan_policy = RatePlanPolicy()
                        model_rateplan_policy.idop_rateplan = model.idop_rateplan
                        model_rateplan_policy.iddef_policy = policy_value.iddef_policy
                        model_rateplan_policy.iddef_policy_category = policy_value.iddef_policy_category
                        model_rateplan_policy.estado = 1
                        model_rateplan_policy.usuario_creacion = user_name
                        db.session.add(model_rateplan_policy)
                        db.session.flush()
                        temp_list_categories.append(policy_value.iddef_policy_category)
                else:
                    list_policies = Policy.query.filter(Policy.iddef_policy.in_(data["policies"])).all()
                    temp_list_categories = []
                    # Se identifican elementos nuevos
                    policies_to_insert = []
                    for policy_index, policy_value in enumerate(list_policies):
                        #Se valida que todas las politicas sean de categorias diferentes
                        # if(policy_value.iddef_policy_category in temp_list_categories):
                        #     raise Exception("Duplicate Policy Category, Categories needs to be different")
                        temp_list_categories.append(policy_value.iddef_policy_category)

                        #SELECT count(*) AS count_1 FROM op_rateplan_policy WHERE op_rateplan_policy.idop_rateplan = id AND op_rateplan_policy.iddef_policy = iddef_policy
                        #SELECT count(*) AS count_1 FROM op_rateplan_property op_rateplan_property.idop_rateplan = :id AND op_rateplan_property.iddef_policy = :iddef_policy
                        count_rate_plan_policies= RatePlanPolicy.query.filter(RatePlanPolicy.idop_rateplan==id, RatePlanPolicy.iddef_policy==policy_value.iddef_policy).with_entities(func.count()).scalar()
                        if int(count_rate_plan_policies) == 0:
                            policies_to_insert.append({"iddef_policy":policy_value.iddef_policy,"iddef_policy_category":policy_value.iddef_policy_category})

                    #Se identifican si los elementos están en la lista del request, posteriormente se activan o desactivan dependiendo del caso
                    list_rateplan_policy = RatePlanPolicy.query.filter(RatePlanPolicy.idop_rateplan==id)
                    for rate_plan_policy_index, rate_plan_policy_value in enumerate(list_rateplan_policy):
                        if(list_rateplan_policy[rate_plan_policy_index].iddef_policy in data["policies"]):
                            if int(list_rateplan_policy[rate_plan_policy_index].estado) == 0:
                                list_rateplan_policy[rate_plan_policy_index].estado = 1
                                list_rateplan_policy[rate_plan_policy_index].usuario_ultima_modificacion = user_name
                                db.session.flush()
                        else:
                            if int(list_rateplan_policy[rate_plan_policy_index].estado) == 1:
                                list_rateplan_policy[rate_plan_policy_index].estado = 0
                                list_rateplan_policy[rate_plan_policy_index].usuario_ultima_modificacion = user_name
                                db.session.flush()

                    #Se insertan elementos nuevos
                    for policy_insert_index, policy_insert_value in enumerate(policies_to_insert):
                        model_rateplan_policy = RatePlanPolicy()
                        model_rateplan_policy.idop_rateplan = model.idop_rateplan
                        model_rateplan_policy.iddef_policy = policy_insert_value["iddef_policy"]
                        model_rateplan_policy.iddef_policy_category = policy_insert_value["iddef_policy_category"]
                        model_rateplan_policy.estado = 1
                        model_rateplan_policy.usuario_creacion = user_name
                        db.session.add(model_rateplan_policy)
                        db.session.flush()

            db.session.commit()

            result = schema.dump(model)

            #Se formatea el resultado
            list_rooms = []
            list_rate_plan_rooms = list(filter(lambda rate_plan_room: rate_plan_room["estado"] == 1, result["rate_plan_rooms"])) #Se filtran solo los activos
            result.pop('rate_plan_rooms', None) # Se elimina tabla intermedia de la respuesta

            for rate_plan_room in list_rate_plan_rooms:
                temp_room = None
                temp_room = rate_plan_room["rooms"] if rate_plan_room["rooms"] is not None and rate_plan_room["rooms"]["estado"] else None
                if temp_room is not None and temp_room not in list_rooms:
                    list_rooms.append(temp_room)

            list_crossouts = []
            list_crossout_rate_plans = list(filter(lambda crossout_rate_plan: crossout_rate_plan["estado"] == 1, result["crossout_rate_plans"])) #Se filtran solo los activos
            result.pop('crossout_rate_plans', None) # Se elimina tabla intermedia de la respuesta

            for crossout_rate_plan in list_crossout_rate_plans:
                temp_crossout = None
                temp_crossout = crossout_rate_plan["crossouts"] if crossout_rate_plan["crossouts"] is not None and crossout_rate_plan["crossouts"]["estado"] else None
                if temp_crossout is not None:
                    list_crossouts.append(temp_crossout)

            list_restrictions = []
            list_rateplan_restrictions = list(filter(lambda rateplan_restriction: rateplan_restriction["estado"] == 1, result["rateplan_restrictions"])) #Se filtran solo los activos
            result.pop('rateplan_restrictions', None) # Se elimina tabla intermedia de la respuesta

            for rateplan_restriction in list_rateplan_restrictions:
                temp_restriction = None
                temp_restriction = rateplan_restriction["restrictions"] if rateplan_restriction["restrictions"] is not None and rateplan_restriction["restrictions"]["estado"] else None
                if temp_restriction is not None:
                    list_restrictions.append(temp_restriction)

            result["rooms"] = list_rooms #Se insertan valores de la relacion
            result["crossouts"] = list_crossouts #Se insertan valores de la relacion
            result["restrictions"] = list_restrictions #Se insertan valores de la relacion

            text_lang_schema = GetTextLangSchema()
            text_lang = TextLang.query.filter(TextLang.id_relation==id,TextLang.table_name=="op_rateplan",TextLang.attribute=="commercial_name",TextLang.estado==1).all()
            result["text_langs"] = text_lang_schema.dump(text_lang, many=True)

            rate_plan_properties = Property.query.join(RatePlanProperty, Property.iddef_property == RatePlanProperty.id_property)\
            .filter(RatePlanProperty.id_rateplan==id, RatePlanProperty.estado==1).all()
            result["properties"] = [rpp.iddef_property for rpp in rate_plan_properties]

            rate_plan_policies = Policy.query.join(RatePlanPolicy, Policy.iddef_policy == RatePlanPolicy.iddef_policy)\
            .filter(RatePlanPolicy.idop_rateplan==id, RatePlanPolicy.estado==1, Policy.estado==1).all()
            result["policies"] = [rppol.iddef_policy for rppol in rate_plan_policies]

            response = {
                "Code": 200,
                "Msg": "Success",
                "Error": False,
                "data": result
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

    #api-rate-plan-delete
    #@base.access_middleware
    # def delete(self, id):
    #     response = {}
    #     try:
    #         schema = ModelSchema(exclude=Util.get_default_excludes())
    #         model = Model.query.get(id)

    #         user_data = base.get_token_data()
    #         user_name = user_data['user']['username']

    #         if model is None:
    #             return {
    #                 "Code": 404,
    #                 "Msg": "data not found",
    #                 "Error": True,
    #                 "data": {}
    #             }

    #         model.estado = 0
    #         model.usuario_ultima_modificacion = user_name

    #         db.session.commit()

    #         result = schema.dump(model)

    #         #Se formatea el resultado
    #         list_rooms = []
    #         list_rate_plan_rooms = list(filter(lambda rate_plan_room: rate_plan_room["estado"] == 1, result["rate_plan_rooms"])) #Se filtran solo los activos
    #         result.pop('rate_plan_rooms', None) # Se elimina tabla intermedia de la respuesta

    #         for rate_plan_room in list_rate_plan_rooms:
    #             temp_room = None
    #             temp_room = rate_plan_room["rooms"] if rate_plan_room["rooms"] is not None and rate_plan_room["rooms"]["estado"] else None
    #             if temp_room is not None:
    #                 list_rooms.append(temp_room)

    #         list_crossouts = []
    #         list_crossout_rate_plans = list(filter(lambda crossout_rate_plan: crossout_rate_plan["estado"] == 1, result["crossout_rate_plans"])) #Se filtran solo los activos
    #         result.pop('crossout_rate_plans', None) # Se elimina tabla intermedia de la respuesta

    #         for crossout_rate_plan in list_crossout_rate_plans:
    #             temp_crossout = None
    #             temp_crossout = crossout_rate_plan["crossouts"] if crossout_rate_plan["crossouts"] is not None and crossout_rate_plan["crossouts"]["estado"] else None
    #             if temp_crossout is not None:
    #                 list_crossouts.append(temp_crossout)

    #         list_restrictions = []
    #         list_rateplan_restrictions = list(filter(lambda rateplan_restriction: rateplan_restriction["estado"] == 1, result["rateplan_restrictions"])) #Se filtran solo los activos
    #         result.pop('rateplan_restrictions', None) # Se elimina tabla intermedia de la respuesta

    #         for rateplan_restriction in list_rateplan_restrictions:
    #             temp_restriction = None
    #             temp_restriction = rateplan_restriction["restrictions"] if rateplan_restriction["restrictions"] is not None and rateplan_restriction["restrictions"]["estado"] else None
    #             if temp_restriction is not None:
    #                 list_restrictions.append(temp_restriction)

    #         result["rooms"] = list_rooms #Se insertan valores de la relacion
    #         result["crossouts"] = list_crossouts #Se insertan valores de la relacion
    #         result["restrictions"] = list_restrictions #Se insertan valores de la relacion

    #         rate_plan_properties = Property.query.join(RatePlanProperty, Property.iddef_property == RatePlanProperty.id_property)\
    #         .filter(RatePlanProperty.id_rateplan==id, RatePlanProperty.estado==1).all()
    #         result["properties"] = [rpp.iddef_property for rpp in rate_plan_properties]

    #         response = {
    #             "Code": 200,
    #             "Msg": "Success",
    #             "Error": False,
    #             "data": result
    #         }
    #     except ValidationError as error:
    #         response = {
    #             "Code": 500,
    #             "Msg": error.messages,
    #             "Error": True,
    #             "data": {}
    #         }
    #     except Exception as e:
    #         db.session.rollback()
    #         response = {
    #             "Code": 500,
    #             "Msg": str(e),
    #             "Error": True,
    #             "data": {}
    #         }

    #     return response

    #api-rate-plan-post
    # @base.access_middleware
    def post(self):
        response = {}
        try:
            json_data = request.get_json(force=True)
            schema = ModelSchema(exclude=Util.get_default_excludes())
            schema_post = PostModelSchema(exclude=Util.get_default_excludes())
            data = schema_post.load(json_data)            
            model = Model()

            user_data = base.get_token_data()
            user_name = user_data['user']['username']
            
            # model.id_market_segment = 1 #Eliminar
            model.code = data["code"]
            # model.booking_window_start = data["booking_window_start"]
            # model.booking_window_end = data["booking_window_end"]
            # model.travel_window_start = "1900-01-01" #Eliminar
            # model.travel_window_end = "1900-01-01" #Eliminar
            model.id_sistema = request.json.get("id_sistema", 1)
            model.currency_code = data["currency_code"]
            model.rate_code_clever = data["rate_code_clever"]
            model.refundable = data["refundable"]
            model.lead_time = data["lead_time"]
            model.estado = 1
            model.usuario_creacion = user_name

            if(len(data["rooms"]) > 0):
                for id_room in data["rooms"]:
                    model_rate_plan_room = RatePlanRooms()
                    model_rate_plan_room.id_room_type = id_room
                    model_rate_plan_room.estado = 1
                    model_rate_plan_room.usuario_creacion = user_name
                    model.rate_plan_rooms.append(model_rate_plan_room)

            if(len(data["crossouts"]) > 0):
                for id_crossout in data["crossouts"]:
                    model_crossout_rate_plan = CrossoutRatePlan()
                    model_crossout_rate_plan.iddef_crossout = id_crossout
                    model_crossout_rate_plan.estado = 1
                    model_crossout_rate_plan.usuario_creacion = user_name
                    model.crossout_rate_plans.append(model_crossout_rate_plan)

            if(len(data["restrictions"]) > 0):
                for id_restriction in data["restrictions"]:
                    model_rateplan_restriction = RatePlanRestriction()
                    model_rateplan_restriction.iddef_restriction = id_restriction
                    model_rateplan_restriction.estado = 1
                    model_rateplan_restriction.usuario_creacion = user_name
                    model.rateplan_restrictions.append(model_rateplan_restriction)

            db.session.add(model)
            db.session.flush()
            if(len(data["text_langs"]) > 0):
                for text_lang in data["text_langs"]:
                    model_text_lang = TextLang()
                    model_text_lang.lang_code = text_lang["lang_code"]
                    model_text_lang.text = text_lang["text"]
                    model_text_lang.table_name = "op_rateplan"
                    model_text_lang.id_relation = model.idop_rateplan
                    model_text_lang.attribute = "commercial_name"
                    model_text_lang.estado = 1
                    db.session.add(model_text_lang)
                    db.session.flush()

            if(len(data["properties"]) > 0):
                for id_property in data["properties"]:
                    model_rateplan_property = RatePlanProperty()
                    model_rateplan_property.id_rateplan = model.idop_rateplan
                    model_rateplan_property.id_property = id_property
                    model_rateplan_property.estado = 1
                    model_rateplan_property.usuario_creacion = user_name
                    db.session.add(model_rateplan_property)
                    db.session.flush()

            if(len(request.json.get("policies", [])) > 0):
                list_policies = Policy.query.filter(Policy.iddef_policy.in_(data["policies"])).all()
                temp_list_categories = []
                for policy_index, policy_value in enumerate(list_policies):
                    #Se valida que todas las politicas sean de categorias diferentes
                    # if(policy_value.iddef_policy_category in temp_list_categories):
                    #     raise Exception("Duplicate Policy Category, Categories needs to be different")
                    model_rateplan_policy = RatePlanPolicy()
                    model_rateplan_policy.idop_rateplan = model.idop_rateplan
                    model_rateplan_policy.iddef_policy = policy_value.iddef_policy
                    model_rateplan_policy.iddef_policy_category = policy_value.iddef_policy_category
                    model_rateplan_policy.estado = 1
                    model_rateplan_policy.usuario_creacion = user_name
                    db.session.add(model_rateplan_policy)
                    db.session.flush()
                    temp_list_categories.append(policy_value.iddef_policy_category)

            db.session.commit()

            result = schema.dump(model)

            #Se formatea el resultado
            list_rooms = []
            list_rate_plan_rooms = list(filter(lambda rate_plan_room: rate_plan_room["estado"] == 1, result["rate_plan_rooms"])) #Se filtran solo los activos
            result.pop('rate_plan_rooms', None) # Se elimina tabla intermedia de la respuesta

            for rate_plan_room in list_rate_plan_rooms:
                temp_room = None
                temp_room = rate_plan_room["rooms"] if rate_plan_room["rooms"] is not None and rate_plan_room["rooms"]["estado"] else None
                if temp_room is not None:
                    list_rooms.append(temp_room)

            list_crossouts = []
            list_crossout_rate_plans = list(filter(lambda crossout_rate_plan: crossout_rate_plan["estado"] == 1, result["crossout_rate_plans"])) #Se filtran solo los activos
            result.pop('crossout_rate_plans', None) # Se elimina tabla intermedia de la respuesta

            for crossout_rate_plan in list_crossout_rate_plans:
                temp_crossout = None
                temp_crossout = crossout_rate_plan["crossouts"] if crossout_rate_plan["crossouts"] is not None and crossout_rate_plan["crossouts"]["estado"] else None
                if temp_crossout is not None:
                    list_crossouts.append(temp_crossout)

            list_restrictions = []
            list_rateplan_restrictions = list(filter(lambda rateplan_restriction: rateplan_restriction["estado"] == 1, result["rateplan_restrictions"])) #Se filtran solo los activos
            result.pop('rateplan_restrictions', None) # Se elimina tabla intermedia de la respuesta

            for rateplan_restriction in list_rateplan_restrictions:
                temp_restriction = None
                temp_restriction = rateplan_restriction["restrictions"] if rateplan_restriction["restrictions"] is not None and rateplan_restriction["restrictions"]["estado"] else None
                if temp_restriction is not None:
                    list_restrictions.append(temp_restriction)

            result["rooms"] = list_rooms #Se insertan valores de la relacion
            result["crossouts"] = list_crossouts #Se insertan valores de la relacion
            result["restrictions"] = list_restrictions #Se insertan valores de la relacion

            text_lang_schema = GetTextLangSchema()
            text_lang = TextLang.query.filter(TextLang.id_relation==model.idop_rateplan,TextLang.table_name=="op_rateplan",TextLang.attribute=="commercial_name",
                TextLang.estado==1).all()
            result["text_langs"] = text_lang_schema.dump(text_lang, many=True)

            rate_plan_properties = Property.query.join(RatePlanProperty, Property.iddef_property == RatePlanProperty.id_property)\
            .filter(RatePlanProperty.id_rateplan==model.idop_rateplan, RatePlanProperty.estado==1).all()
            result["properties"] = [rpp.iddef_property for rpp in rate_plan_properties]

            rate_plan_policies = Policy.query.join(RatePlanPolicy, Policy.iddef_policy == RatePlanPolicy.iddef_policy)\
            .filter(RatePlanPolicy.idop_rateplan==model.idop_rateplan, RatePlanPolicy.estado==1, Policy.estado==1).all()
            result["policies"] = [rppol.iddef_policy for rppol in rate_plan_policies]

            response = {
                "Code": 200,
                "Msg": "Success",
                "Error": False,
                "data": result
            }
        except ValidationError as error:
            db.session.rollback()
            response = {
                "Code": 500,
                "Msg": error.messages,
                "Error": True,
                "data" : {}
            }
        except Exception as e:
            db.session.rollback()
            response = {
                "Code": 500,
                "Msg": str(e),
                "Error": True,
                "data" : {}
            }
        
        return response

class RatePlanListSearch(Resource):
    #api-rate-plan-get-all
    # @base.access_middleware
    def get(self):
        try:
            isAll = request.args.get("all")
            property_code = request.args.get("property")
            sistema = request.args.get("system")
            market = request.args.get("market")
            order = request.args.get("order")
            desc = request.args.get("desc")

            data = Model()

            condition = []

            condition.append(Model.estado==1)

            if isAll is not None:
                condition.pop()

            if sistema is not None:
                condition.append(Model.id_sistema==sistema)
            else:
                condition.append(Model.id_sistema==1)

            # if market is not None:
            #     condition.append(Model.id_market_segment==market)

            if property_code is not None:
                condition.append(RatePlanProperty.id_property==property_code)
                condition.append(RatePlanProperty.estado==1)

            data = Model.query.join(RatePlanProperty).filter(and_(*condition))

            schema = ModelSchema(exclude=Util.get_default_excludes()+("crossout_rate_plans","rateplan_restrictions"), many=True)

            result = schema.dump(data)

            for rateplan_id, rateplan_value in enumerate(result):
                list_rooms = []
                list_rate_plan_rooms = list(filter(lambda rate_plan_room: rate_plan_room["estado"] == 1, rateplan_value["rate_plan_rooms"])) #Se filtran solo los activos
                result[rateplan_id].pop('rate_plan_rooms', None) # Se elimina tabla intermedia de la respuesta

                result[rateplan_id]["rooms"] = []
                for rate_plan_room in list_rate_plan_rooms:
                    temp_room = None
                    temp_room = rate_plan_room["rooms"] if rate_plan_room["rooms"] is not None and rate_plan_room["rooms"]["estado"] == 1 else None
                    if temp_room is not None and temp_room["room_code"] not in result[rateplan_id]["rooms"]:
                        result[rateplan_id]["rooms"].append(temp_room["room_code"])


            if data is None:
                response = {
                    "Code": 200,
                    "Msg": "Success",
                    "Error": False,
                    "data": {}
                }
            else:
                msg = "Success"
                try:
                    order_type = False if desc is None else True
                    if order is not None and Utilities.check_field_exists_data(self,result,order):
                        result = Utilities.sort_dict(self,result,order,asc=order_type)
                    elif order is not None:
                        msg = order + " not exist"
                except Exception as ex:
                    msg = str(ex)

                response = {
                    "Code": 200,
                    "Msg": msg,
                    "Error": False,
                    "data": result
                }
        except Exception as e:
            response = {
                "Code": 500,
                "Msg": str(e),
                "Error": True,
                "data": {}
            }

        return response

class RatePlanDefault(Resource):
    #api-rate-plan-put-estado
    # @base.access_middleware
    def put(self, id):
        response = {}
        try:
            json_data = request.get_json(force=True)
            schema = GetModelSchema(exclude=Util.get_default_excludes())
            schema_request = RatePlanEstadoSchema(exclude=Util.get_default_excludes())
            data = schema_request.load(json_data)
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

            model.estado = data["estado"]
            model.usuario_ultima_modificacion = user_name

            db.session.commit()

            result = schema.dump(model)
            
            result.pop('rate_plan_rooms', None) # Se elimina tabla intermedia de la respuesta
            result.pop('crossout_rate_plans', None) # Se elimina tabla intermedia de la respuesta
            result.pop('rateplan_restrictions', None) # Se elimina tabla intermedia de la respuesta

            text_lang_schema = GetTextLangSchema()
            text_lang = TextLang.query.filter(TextLang.id_relation==id,TextLang.table_name=="op_rateplan",TextLang.attribute=="commercial_name",TextLang.estado==1).all()
            result["text_langs"] = text_lang_schema.dump(text_lang, many=True)

            response = {
                "Code": 200,
                "Msg": "Success",
                "Error": False,
                "data": result
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

class RatePlanPublic(Resource):
    #api-public-rate-plan-get-id
    @PublicAuth.access_middleware
    def get(self, id, lang_code):
        try:
            lang_code = lang_code.upper()
            if lang_code == 'ES':
                lang_code = 'description_es'
            else:
                lang_code = 'description_en'

            schemaPolicy = GetPPModelSchema()
            rate_plan_policies = Policy.query.join(RatePlanPolicy, Policy.iddef_policy == RatePlanPolicy.iddef_policy)\
            .filter(RatePlanPolicy.idop_rateplan==id, RatePlanPolicy.estado==1, Policy.estado==1).all()

            if len(rate_plan_policies) > 0:
                result = []
                for item_policy in rate_plan_policies:
                    iddef_policy = item_policy.iddef_policy
                    if item_policy.iddef_policy_category ==1:
                        schema = ModelCPSchema(exclude=Util.get_default_excludes())
                    elif item_policy.iddef_policy_category == 2:
                        schema = ModelGSchema(exclude=Util.get_default_excludes())
                    elif item_policy.iddef_policy_category == 3:
                        schema = ModelTSchema(exclude=Util.get_default_excludes())
                    else:
                        schema = GetPPModelSchema()
                    data = schema.dump(item_policy)
                    obj = {}
                    if("policy_cancel_penalties" in data):
                        list_policy_cancel_penalties = list(filter(lambda elem_policy_cancel_penalty: elem_policy_cancel_penalty["estado"] == 1, data["policy_cancel_penalties"]))
                        list_texts = []
                        list_texts = [cancel[lang_code] for cancel in list_policy_cancel_penalties]
                        obj = {
                            "idop_rate_plan":id,
                            "iddef_policy_category":data["iddef_policy_category"],
                            "policy_category":data["policy_category"],
                            "texts":list_texts,
                        }
                        result.append(obj)
                    obj = {}
                    if("policy_guarantees" in data):
                        list_policy_guarantees = list(filter(lambda elem_policy_guarantee: elem_policy_guarantee["estado"] == 1, data["policy_guarantees"]))
                        list_texts = []
                        list_texts = [guarantees[lang_code] for guarantees in list_policy_guarantees]
                        obj = {
                            "idop_rate_plan":id,
                            "iddef_policy_category":data["iddef_policy_category"],
                            "policy_category":data["policy_category"],
                            "texts":list_texts,
                        }
                        result.append(obj)
                    obj = {}
                    if("policy_tax_groups" in data):
                        list_policy_tax_groups = list(filter(lambda elem_policy_tax_groups: elem_policy_tax_groups["estado"] == 1, data["policy_tax_groups"]))
                        list_texts = []
                        list_texts = [groups[lang_code] for groups in list_policy_tax_groups]
                        obj = {
                            "idop_rate_plan":id,
                            "iddef_policy_category":data["iddef_policy_category"],
                            "policy_category":data["policy_category"],
                            "texts":list_texts,
                        }
                        result.append(obj)

            if rate_plan_policies is None:
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
                    "data": result
                }
        except Exception as e:
            response = {
                "Code": 500,
                "Msg": str(e),
                "Error": True,
                "data": {}
            }

        return response
    
    @staticmethod
    def get_policy_lang(iddef_policy, lang_code, is_cancellation = False):
        obj = None
        lang_code = lang_code.upper()
        lang_field = "description_en"
        if lang_code == 'ES':
            lang_field = 'description_es'        
        
        if not is_cancellation:
            data_policy = Policy.query.filter_by(iddef_policy=iddef_policy, estado=1).first()
        else:
            data_policy = PolicyCancellationDetail.query.filter(\
                PolicyCancellationDetail.iddef_policy_cancellation_detail==iddef_policy,\
                PolicyCancellationDetail.estado==1).first()
        
        if data_policy is not None:
            if not is_cancellation:
                if data_policy.iddef_policy_category == 2:
                    schema = ModelGSchema(exclude=Util.get_default_excludes())
                elif data_policy.iddef_policy_category == 3:
                    schema = ModelTSchema(exclude=Util.get_default_excludes())
                else:
                    schema = GetPPModelSchema()
                
                data = schema.dump(data_policy)
                """
                if("policy_cancel_penalties" in data):
                    list_policy_cancel_penalties = list(filter(lambda elem_policy_cancel_penalty: elem_policy_cancel_penalty["estado"] == 1, data["policy_cancel_penalties"]))
                    list_texts = []
                    list_texts = [cancel[lang_code] for cancel in list_policy_cancel_penalties]
                    obj = {
                        "iddef_policy_category":data["iddef_policy_category"],
                        "policy_category":data["policy_category"],
                        "texts":list_texts,
                    }
                """
                if("policy_guarantees" in data):
                    list_policy_guarantees = list(filter(lambda elem_policy_guarantee: elem_policy_guarantee["estado"] == 1, data["policy_guarantees"]))
                    list_texts = []
                    list_texts = [guarantees[lang_field] for guarantees in list_policy_guarantees]
                    obj = {
                        "iddef_policy_category":data["iddef_policy_category"],
                        "policy_category":data["policy_category"],
                        "texts":list_texts,
                    }
                if("policy_tax_groups" in data):
                    list_policy_tax_groups = list(filter(lambda elem_policy_tax_groups: elem_policy_tax_groups["estado"] == 1, data["policy_tax_groups"]))
                    list_texts = []
                    list_texts = [groups[lang_field] for groups in list_policy_tax_groups]
                    obj = {
                        "iddef_policy_category":data["iddef_policy_category"],
                        "policy_category":data["policy_category"],
                        "texts":list_texts,
                    }
            else:
                texts = data_policy.description_es if lang_code == 'ES' else data_policy.description_en
                policy_info = Policy.query.filter_by(iddef_policy=data_policy.iddef_policy, estado=1).first()
                schema = ModelCPSchema(exclude=Util.get_default_excludes())
                policy_data = schema.dump(policy_info)
                obj = {
                    "iddef_policy_category": policy_data["iddef_policy_category"],
                    "policy_category": policy_data["policy_category"],
                    "texts": texts,
                }
        
        return obj
    
    @staticmethod
    def get_policy_by_category(idop_rateplan, iddef_policy_category, booking_start_date):
        """
            Retrieve policy by id rate plan & id policy category, if it doesn't config then 
            retrieve the default policy of the category

            *Note: NOT USE FOR CANCELLATION POLICY

            :param idop_rateplan ID rate plan
            :param iddef_policy_category ID policy category
            :param booking_start_date Booking start date

            :return policy Policy instance
        """
        policy = None

        policies = Policy.query.join(RatePlanPolicy, RatePlanPolicy.iddef_policy == Policy.iddef_policy)\
            .filter(RatePlanPolicy.iddef_policy_category == iddef_policy_category, \
                RatePlanPolicy.idop_rateplan == idop_rateplan, \
                RatePlanPolicy.estado == 1).all()

        #search in dates
        for item in policies:
            for range_date in item.available_dates:
                start_date = datetime.strptime(range_date.get("start_date"), '%Y-%m-%d')
                end_date = datetime.strptime(range_date.get("end_date"), '%Y-%m-%d')

                if booking_start_date >= start_date and booking_start_date <= end_date:
                    policy = item
                    break
            
            if policy:
                break
        else:
            if policies:
                policy = policies[0]
        
        return policy
    
    @staticmethod
    def get_policy_cancellation(idop_rateplan, booking_start_date, refundable = False):
        """
            find policy cancellation by rateplan and booking start date
            :param idop_rateplan ID rate plan
            :param booking_start_date Booking start date
            :param is_refundable RatePlan is refundable (default false)

            :return cancellation_detail PolicyCancellationDetail instance
        """
        cancellation_detail = None
        iddef_policy_category = 1
        #booking_start_date = date(booking_start_date.year, booking_start_date.month, booking_start_date.day)
        
        policies = Policy.query.join(RatePlanPolicy, RatePlanPolicy.iddef_policy == Policy.iddef_policy)\
            .filter(RatePlanPolicy.iddef_policy_category == iddef_policy_category, \
                RatePlanPolicy.idop_rateplan == idop_rateplan, \
                RatePlanPolicy.estado == 1).all()
        
        for policy in policies:
            #check if is required refundable cancellation policy
            if refundable:
                cancellation_detail = next((item for item in policy.policy_cancel_penalties if item.estado == 1 \
                and item.is_base == 0 and item.is_refundable == 1 \
                and (booking_start_date.date() >= item.start_date and booking_start_date.date() <= item.end_date)), None)
            
            #if not found refundable or refundable is false, search for dates
            if not cancellation_detail:
                cancellation_detail = next((item for item in policy.policy_cancel_penalties if item.estado == 1 \
                and item.is_base == 0 and item.is_refundable == 0 \
                and (booking_start_date.date() >= item.start_date and booking_start_date.date() <= item.end_date)), None)
            
            #if policy was found, get the lang description and break loop
            if cancellation_detail:
                break
            else:
                #in other case, looking for base cancellation and break loop
                cancellation_detail = next((item for item in policy.policy_cancel_penalties if item.estado == 1 \
                    and item.is_base == 1), None)
                if cancellation_detail:
                    break
        
        return cancellation_detail
    
    #api-public-room-rate-plan-get
    # @PublicAuth.access_middleware
    # def post(self):
    #     try:
    #         json_data = request.get_json(force=True)
    #         schema = GetPModelSchema()
    #         schemaRTC = RTCModelSchema(exclude=Util.get_default_excludes())
    #         schemaRP = GetDRPModelSchema()
    #         data = schema.load(json_data)
    #         if request.json.get("lang_code") != None:
    #             lang_code = data["lang_code"]
    #         else:
    #             lang_code = "EN"
    #         date_start = data["date_start"]
    #         date_end = data["date_end"]
    #         id_rate_plan = data["id_rate_plan"]
    #         currency = data["currency"]
    #         id_room = data["id_room"]
    #         hotel = prHelper.getHotelInfo(self,data["id_hotel"])
    #         id_hotel = hotel.iddef_property
    #         data_room = data["paxes"]
    #         for itemAR in data_room:
    #             if ("adults" in data_room):
    #                 adults = data_room["adults"]
    #             else:
    #                 adults = 0
    #             if ("teens" in data_room):    
    #                 teens = data_room["teens"]
    #             else:
    #                 teens = 0
    #             if ("kids" in data_room):    
    #                 kids = data_room["kids"]
    #             else:
    #                 kids = 0
    #             if ("infants" in data_room):    
    #                 infants = data_room["infants"]
    #             else:
    #                 infants = 0
    #             totalChild = teens + kids + infants
    #             totalOcupacity = adults + kids + teens + infants
    #         #Busqueda de cuarto
    #         TotalTarifa = []
    #         dataRooms = RTCModel.query.filter_by(iddef_room_type_category=id_room, estado=1).first()
    #         if dataRooms is not None:
    #             TotalTarifa = []
    #             max_ocupancy = dataRooms.max_ocupancy
    #             acept_chd = dataRooms.acept_chd
    #             standar_ocupancy = dataRooms.standar_ocupancy
    #             band_room = False # bandera para filtrar habitacion por pax
    #             #validar cuarto que sea menor al max pax
    #             if totalOcupacity <= max_ocupancy:
    #                 band_room = True
    #                 if totalChild > 0:
    #                     if acept_chd != 0:
    #                         band_room = True
    #                     else:
    #                         band_room = False
    #                 else:
    #                     band_room = True
    #             else:
    #                 band_room = False
    #             if totalOcupacity != 0:
    #                 totalAdults = adults
    #             else:
    #                 totalAdults = standar_ocupancy

    #             #Validar si entra cuarto
    #             if band_room == True:
    #                 #calculo de tarifa por cuarto                     
    #                 dataRatePlanPrices = Search.get_price_per_day(self,\
    #                 id_hotel,dataRooms.iddef_room_type_category,id_rate_plan,date_start,\
    #                 date_end,totalAdults,totalChild,currency=currency)

    #                 #Busqueda rate plan code
    #                 dataPlan = Model.query.filter_by(idop_rateplan=id_rate_plan, estado=1).first()
    #                 nameCode = dataPlan.code
    #                 #Busqueda de nombre rate plan
    #                 dataTextLangPlan = txtHelper.getTextLangAttributes(self,\
    #                 'op_rateplan','commercial_name',lang_code,id_rate_plan)

    #                 if dataTextLangPlan is not None:
    #                     name_Plan = dataTextLangPlan.text
    #                 else:
    #                     name_Plan = ''
    #                 if dataRatePlanPrices['total'] != 0:
    #                     if dataRatePlanPrices['nights'] == 0:
    #                         night_price = 0
    #                     else:
    #                         night_price = dataRatePlanPrices['total'] / dataRatePlanPrices['nights']
    #                         percent_discount = int(dataRatePlanPrices["total_percent_discount"])
    #                         night_price_cross = Quotes.get_rate_crossout(self,\
    #                         percent_discount,amount=night_price)
    #                     RatePlanPrices = schemaRP.dump(dataRatePlanPrices)
    #                     RatePlanPrices.setdefault("idop_rate_plan", id_rate_plan)
    #                     RatePlanPrices.setdefault("plan_name", name_Plan)
    #                     RatePlanPrices.setdefault("plan_code", nameCode)
    #                     RatePlanPrices.setdefault("night_price", round(night_price,2))
    #                     RatePlanPrices["total_crossout"] = round(night_price_cross,2)
    #                     RatePlanPrices["idRoom"]=data["id_room"]
    #                     #filtrar  politicas por rate
    #                     RoomPolicy = []
    #                     DataRoomPolicy = self.get(id_rate_plan, lang_code)
    #                     if len(DataRoomPolicy) > 0:
    #                         RoomPolicy = DataRoomPolicy["data"]
    #                     RatePlanPrices['policies'] = RoomPolicy
    #                     TotalTarifa.append(RatePlanPrices)
    #             else:
    #                 pass
    #         else:
    #             TotalTarifa = []
            
    #         if data is None:
    #             return {
    #                 "Code": 404,
    #                 "Msg": "data not found",
    #                 "Error": True,
    #                 "data": {}
    #             }

    #         response = {
    #             "Code": 200,
    #             "Msg": "Success",
    #             "Error": False,
    #             "data": TotalTarifa
    #         }
    #     except ValidationError as error:
    #         response = {
    #             "Code": 500,
    #             "Msg": error.messages,
    #             "Error": True,
    #             "data": {}
    #         }
    #     except Exception as e:
    #         db.session.rollback()
    #         response = {
    #             "Code": 500,
    #             "Msg": str(e),
    #             "Error": True,
    #             "data": {}
    #         }

    #     return response
