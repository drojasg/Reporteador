from flask import Flask, request
from flask_restful import Resource
from marshmallow import ValidationError

from config import db, base
import datetime
from models.policy import PolicySchema as ModelSchema, PolicyCPSchema as ModelCPSchema, PolicyGSchema as ModelGSchema, PolicyTSchema as ModelTSchema, \
Policy as Model, GetPolicySchema as GetModelSchema, PolicyPostSchema, PolicyPostDefaultSchema, GetPolicyDefaultSchema, PolicyRatePlanSchema, GetPolicyRatePlanSchema
#from models.property import Property, GetPropertyPolicySchema
#from models.policy_cancel_penalty import PolicyCancelPenalty
from models.policy_guarantee import PolicyGuarantee
from models.policy_penalty_cancel_fee import PolicyPenaltyCancelFee
from models.policy_guarantee_deposit import PolicyGuaranteeDeposit
from models.policy_tax_group import PolicyTaxGroup
from models.rateplan import RatePlan as rateplanModel
from common.util import Util
from sqlalchemy import func
from .policyHelper import PolicyFunctions
from resources.text_lang.textlangHelper import Filter as textFuntions
from common.public_auth import PublicAuth


class Policy(Resource):
    # def get(self, id, category):
    #   try:
    #       data = {}
    #       result = Model.query.get(id)

    #       if result is None:
    #           response = {
    #               "Code": 200,
    #               "Msg": "Success",
    #               "Error": False,
    #               "data": {}
    #           }
    #       else:
    #           if category == 1:
    #               schema = ModelCPSchema(exclude=Util.get_default_excludes())
    #           elif category == 2:
    #               schema = ModelGSchema(exclude=Util.get_default_excludes())
    #           elif category == 3:
    #               schema = ModelTSchema(exclude=Util.get_default_excludes())
    #           else:
    #               schema = ModelSchema(exclude=Util.get_default_excludes())

    #           data = schema.dump(result)

    #           if("policy_cancel_penalties" in data):
    #               for policy_cancel_penalty_id, policy_cancel_penalty_value in enumerate(data["policy_cancel_penalties"]):
    #                   list_cancel_fees = list(filter(lambda elem_cancel_fee: elem_cancel_fee["estado"] == 1, policy_cancel_penalty_value["cancel_fees"]))
    #                   data["policy_cancel_penalties"][policy_cancel_penalty_id]["cancel_fees"] = list_cancel_fees
    #               list_policy_cancel_penalties = list(filter(lambda elem_policy_cancel_penalty: elem_policy_cancel_penalty["estado"] == 1, data["policy_cancel_penalties"]))
    #               data["policy_cancel_penalties"] = list_policy_cancel_penalties
    #           if("policy_guarantees" in data):
    #               for policy_guarantee_id, policy_guarantee_value in enumerate(data["policy_guarantees"]):
    #                   list_policy_guarantee_deposits = list(filter(lambda elem_policy_guarantee_deposit: elem_policy_guarantee_deposit["estado"] == 1, policy_guarantee_value["policy_guarantee_deposits"]))
    #                   data["policy_guarantees"][policy_guarantee_id]["policy_guarantee_deposits"] = list_policy_guarantee_deposits
    #               list_policy_guarantees = list(filter(lambda elem_policy_guarantee: elem_policy_guarantee["estado"] == 1, data["policy_guarantees"]))
    #               data["policy_guarantees"] = list_policy_guarantees
    #           if("policy_tax_groups" in data):
    #               list_policy_tax_groups = list(filter(lambda elem_policy_tax_group: elem_policy_tax_group["estado"] == 1, data["policy_tax_groups"]))
    #               data["policy_tax_groups"] = list_policy_tax_groups

    #       response = {
    #           "Code": 200,
    #           "Msg": "Success",
    #           "Error": False,
    #           "data": data
    #       }
    #   except Exception as e:
    #       response = {
    #           "Code": 500,
    #           "Msg": str(e),
    #           "Error": True,
    #           "data": {}
    #       }

    #   return response

    #api-policies-put
    # @base.access_middleware
    def put(self, id):
        response = {}
        try:
            json_data = request.get_json(force=True)
            schema = GetModelSchema(exclude=Util.get_default_excludes())
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
            # if request.json.get("iddef_policy_category") != None:
            #   model.iddef_policy_category = data["iddef_policy_category"]
            if request.json.get("policy_code") != None:
                if model.policy_code != data["policy_code"]:
                    count_same_code_policy = Model.query.filter(Model.policy_code==data["policy_code"], Model.iddef_policy!=model.iddef_policy).with_entities(func.count()).scalar()
                    if count_same_code_policy > 0:
                        raise Exception("Duplicate Policy Code")
                model.policy_code = data["policy_code"]
            if request.json.get("iddef_currency") != None:
                model.iddef_currency = data["iddef_currency"]
            if request.json.get("is_default") != None:
                model.is_default = data["is_default"]
            if request.json.get("option_selected") != None:
                model.option_selected = data["option_selected"]
            if request.json.get("text_only_policy") != None:
                model.text_only_policy = data["text_only_policy"]
            if request.json.get("available_dates") != None:
                model.available_dates = data["available_dates"]
            if request.json.get("estado") != None:
                model.estado = data["estado"]
            model.usuario_ultima_modificacion = user_name

            # Nota: Los modelos nuevos se agregan fuera del loop debido a que al agregar un elemento nuevo
            # dentro del for se continuaba con el elemento agregado, generando un loop infinito 
            list_models_policy_cancel_penalties = []
            list_models_policy_guarantees = []
            list_models_tax_groups = []

            # Se procesan Penalidades
            """ for policy_cancel_penalty in request.json.get("policy_cancel_penalties", []):
                if(len(model.policy_cancel_penalties) == 0):
                    #insert si no hay elementos guardados
                    model_policy_cancel_penalty = PolicyCancelPenalty()
                    model_policy_cancel_penalty.penalty_name = policy_cancel_penalty["penalty_name"]
                    model_policy_cancel_penalty.days_prior_to_arrival_deadline = policy_cancel_penalty["days_prior_to_arrival_deadline"]
                    model_policy_cancel_penalty.time_date_deadline = policy_cancel_penalty["time_date_deadline"]
                    model_policy_cancel_penalty.description_en = policy_cancel_penalty["description_en"]
                    model_policy_cancel_penalty.description_es = policy_cancel_penalty["description_es"]
                    model_policy_cancel_penalty.estado = 1
                    model_policy_cancel_penalty.usuario_creacion = user_name
                    for cancel_fee in policy_cancel_penalty["cancel_fees"]:
                        model_cancel_fee = PolicyPenaltyCancelFee()
                        model_cancel_fee.iddef_policy_rule = cancel_fee["iddef_policy_rule"]
                        model_cancel_fee.percent = cancel_fee["percent"]
                        model_cancel_fee.option_percent = cancel_fee["option_percent"]
                        model_cancel_fee.number_nights_percent = cancel_fee["number_nights_percent"]
                        model_cancel_fee.fixed_amount = cancel_fee["fixed_amount"]
                        model_cancel_fee.estado = 1
                        model_cancel_fee.usuario_creacion = user_name

                        model_policy_cancel_penalty.cancel_fees.append(model_cancel_fee)

                    list_models_policy_cancel_penalties.append(model_policy_cancel_penalty)

                for id_policy_cancel_penalty, value_policy_cancel_penalty in enumerate(model.policy_cancel_penalties):
                    policy_cancel_penalties_index = int(policy_cancel_penalty["iddef_policy_cancel_penalty"]) if policy_cancel_penalty["iddef_policy_cancel_penalty"] else 0
                    if(model.policy_cancel_penalties[id_policy_cancel_penalty].iddef_policy_cancel_penalty == policy_cancel_penalties_index):
                        #Update
                        model.policy_cancel_penalties[id_policy_cancel_penalty].penalty_name = policy_cancel_penalty["penalty_name"]
                        model.policy_cancel_penalties[id_policy_cancel_penalty].days_prior_to_arrival_deadline = policy_cancel_penalty["days_prior_to_arrival_deadline"]
                        model.policy_cancel_penalties[id_policy_cancel_penalty].time_date_deadline = policy_cancel_penalty["time_date_deadline"]
                        model.policy_cancel_penalties[id_policy_cancel_penalty].description_en = policy_cancel_penalty["description_en"]
                        model.policy_cancel_penalties[id_policy_cancel_penalty].description_es = policy_cancel_penalty["description_es"]
                        model.policy_cancel_penalties[id_policy_cancel_penalty].estado = policy_cancel_penalty["estado"]
                        model.policy_cancel_penalties[id_policy_cancel_penalty].usuario_ultima_modificacion = user_name

                        list_models_cancel_fees = []
                        for cancel_fee in policy_cancel_penalty["cancel_fees"]:
                            if(len(model.policy_cancel_penalties[id_policy_cancel_penalty].cancel_fees) == 0):
                                model_cancel_fee = PolicyPenaltyCancelFee()
                                model_cancel_fee.iddef_policy_rule = cancel_fee["iddef_policy_rule"]
                                model_cancel_fee.percent = cancel_fee["percent"]
                                model_cancel_fee.option_percent = cancel_fee["option_percent"]
                                model_cancel_fee.number_nights_percent = cancel_fee["number_nights_percent"]
                                model_cancel_fee.fixed_amount = cancel_fee["fixed_amount"]
                                model_cancel_fee.estado = 1
                                model_cancel_fee.usuario_creacion = user_name
                                list_models_cancel_fees.append(model_cancel_fee)

                            for id_cancel_fee, value_cancel_fee in enumerate(model.policy_cancel_penalties[id_policy_cancel_penalty].cancel_fees):
                                cancel_fee_index = int(cancel_fee["iddef_policy_penalty_cancel_fee"]) if cancel_fee["iddef_policy_penalty_cancel_fee"] else 0
                                if(model.policy_cancel_penalties[id_policy_cancel_penalty].cancel_fees[id_cancel_fee].iddef_policy_penalty_cancel_fee == cancel_fee_index):
                                    #update
                                    model.policy_cancel_penalties[id_policy_cancel_penalty].cancel_fees[id_cancel_fee].iddef_policy_rule = cancel_fee["iddef_policy_rule"]
                                    model.policy_cancel_penalties[id_policy_cancel_penalty].cancel_fees[id_cancel_fee].percent = cancel_fee["percent"]
                                    model.policy_cancel_penalties[id_policy_cancel_penalty].cancel_fees[id_cancel_fee].option_percent = cancel_fee["option_percent"]
                                    model.policy_cancel_penalties[id_policy_cancel_penalty].cancel_fees[id_cancel_fee].number_nights_percent = cancel_fee["number_nights_percent"]
                                    model.policy_cancel_penalties[id_policy_cancel_penalty].cancel_fees[id_cancel_fee].fixed_amount = cancel_fee["fixed_amount"]
                                    model.policy_cancel_penalties[id_policy_cancel_penalty].cancel_fees[id_cancel_fee].estado = cancel_fee["estado"]
                                    model.policy_cancel_penalties[id_policy_cancel_penalty].cancel_fees[id_cancel_fee].usuario_ultima_modificacion = user_name
                                elif(cancel_fee_index == 0):
                                    #insert
                                    model_cancel_fee = PolicyPenaltyCancelFee()
                                    model_cancel_fee.iddef_policy_rule = cancel_fee["iddef_policy_rule"]
                                    model_cancel_fee.percent = cancel_fee["percent"]
                                    model_cancel_fee.option_percent = cancel_fee["option_percent"]
                                    model_cancel_fee.number_nights_percent = cancel_fee["number_nights_percent"]
                                    model_cancel_fee.fixed_amount = cancel_fee["fixed_amount"]
                                    model_cancel_fee.estado = 1
                                    model_cancel_fee.usuario_creacion = user_name
                                    list_models_cancel_fees.append(model_cancel_fee)
                                    break
                        for temp_cancel_fees in list_models_cancel_fees:
                            model.policy_cancel_penalties[id_policy_cancel_penalty].cancel_fees.append(temp_cancel_fees)

                    elif(policy_cancel_penalties_index == 0):
                        #Insert
                        model_policy_cancel_penalty = PolicyCancelPenalty()
                        model_policy_cancel_penalty.penalty_name = policy_cancel_penalty["penalty_name"]
                        model_policy_cancel_penalty.days_prior_to_arrival_deadline = policy_cancel_penalty["days_prior_to_arrival_deadline"]
                        model_policy_cancel_penalty.time_date_deadline = policy_cancel_penalty["time_date_deadline"]
                        model_policy_cancel_penalty.description_en = policy_cancel_penalty["description_en"]
                        model_policy_cancel_penalty.description_es = policy_cancel_penalty["description_es"]
                        model_policy_cancel_penalty.estado = 1
                        model_policy_cancel_penalty.usuario_creacion = user_name
                        for cancel_fee in policy_cancel_penalty["cancel_fees"]:
                            model_cancel_fee = PolicyPenaltyCancelFee()
                            model_cancel_fee.iddef_policy_rule = cancel_fee["iddef_policy_rule"]
                            model_cancel_fee.percent = cancel_fee["percent"]
                            model_cancel_fee.option_percent = cancel_fee["option_percent"]
                            model_cancel_fee.number_nights_percent = cancel_fee["number_nights_percent"]
                            model_cancel_fee.fixed_amount = cancel_fee["fixed_amount"]
                            model_cancel_fee.estado = 1
                            model_cancel_fee.usuario_creacion = user_name

                            model_policy_cancel_penalty.cancel_fees.append(model_cancel_fee)
                        list_models_policy_cancel_penalties.append(model_policy_cancel_penalty)
                        break """

            # Se procesan garantias
            for policy_guarantee in request.json.get("policy_guarantees", []):
                if(len(model.policy_guarantees) == 0):
                    #insert
                    model_policy_guarantee = PolicyGuarantee()
                    model_policy_guarantee.iddef_policy_guarantee_type = policy_guarantee["iddef_policy_guarantee_type"]
                    model_policy_guarantee.allow_hold_free = policy_guarantee["allow_hold_free"]
                    model_policy_guarantee.hold_duration = policy_guarantee["hold_duration"]
                    model_policy_guarantee.stay_dates_option = policy_guarantee["stay_dates_option"]
                    model_policy_guarantee.stay_dates = policy_guarantee["stay_dates"]
                    model_policy_guarantee.reminder_lead_time = policy_guarantee["reminder_lead_time"]
                    model_policy_guarantee.offer_last_chance_promotion = policy_guarantee["offer_last_chance_promotion"]
                    model_policy_guarantee.discount_per_night = policy_guarantee["discount_per_night"]
                    model_policy_guarantee.type_discount = policy_guarantee["type_discount"]
                    model_policy_guarantee.min_lead_time = policy_guarantee["min_lead_time"]
                    model_policy_guarantee.availability_threshold = policy_guarantee["availability_threshold"]
                    model_policy_guarantee.description_en = policy_guarantee["description_en"]
                    model_policy_guarantee.description_es = policy_guarantee["description_es"]
                    model_policy_guarantee.estado = 1
                    model_policy_guarantee.usuario_creacion = user_name
                    for policy_guarantee_deposit in policy_guarantee["policy_guarantee_deposits"]:
                        model_policy_guarantee_deposit = PolicyGuaranteeDeposit()
                        model_policy_guarantee_deposit.iddef_policy_rule = policy_guarantee_deposit["iddef_policy_rule"]
                        model_policy_guarantee_deposit.percent = policy_guarantee_deposit["percent"]
                        model_policy_guarantee_deposit.option_percent = policy_guarantee_deposit["option_percent"]
                        model_policy_guarantee_deposit.number_nights_percent = policy_guarantee_deposit["number_nights_percent"]
                        model_policy_guarantee_deposit.fixed_amount = policy_guarantee_deposit["fixed_amount"]
                        model_policy_guarantee_deposit.estado = 1
                        model_policy_guarantee_deposit.usuario_creacion = user_name
                        model_policy_guarantee.policy_guarantee_deposits.append(model_policy_guarantee_deposit)

                    list_models_policy_guarantees.append(model_policy_guarantee)
                for id_policy_guarantee, value_policy_guarantee in enumerate(model.policy_guarantees):
                    policy_guarantee_index = int(policy_guarantee["iddef_policy_guarantee"]) if policy_guarantee["iddef_policy_guarantee"] else 0
                    if(model.policy_guarantees[id_policy_guarantee].iddef_policy_guarantee == policy_guarantee_index):
                        #update
                        model.policy_guarantees[id_policy_guarantee].iddef_policy_guarantee_type = policy_guarantee["iddef_policy_guarantee_type"]
                        model.policy_guarantees[id_policy_guarantee].allow_hold_free = policy_guarantee["allow_hold_free"]
                        model.policy_guarantees[id_policy_guarantee].hold_duration = policy_guarantee["hold_duration"]
                        model.policy_guarantees[id_policy_guarantee].stay_dates = policy_guarantee["stay_dates"]
                        model.policy_guarantees[id_policy_guarantee].stay_dates_option = policy_guarantee["stay_dates_option"]
                        model.policy_guarantees[id_policy_guarantee].reminder_lead_time = policy_guarantee["reminder_lead_time"]
                        model.policy_guarantees[id_policy_guarantee].offer_last_chance_promotion = policy_guarantee["offer_last_chance_promotion"]
                        model.policy_guarantees[id_policy_guarantee].discount_per_night = policy_guarantee["discount_per_night"]
                        model.policy_guarantees[id_policy_guarantee].type_discount = policy_guarantee["type_discount"]
                        model.policy_guarantees[id_policy_guarantee].min_lead_time = policy_guarantee["min_lead_time"]
                        model.policy_guarantees[id_policy_guarantee].availability_threshold = policy_guarantee["availability_threshold"]
                        model.policy_guarantees[id_policy_guarantee].description_en = policy_guarantee["description_en"]
                        model.policy_guarantees[id_policy_guarantee].description_es = policy_guarantee["description_es"]
                        model.policy_guarantees[id_policy_guarantee].estado = policy_guarantee["estado"]
                        model.policy_guarantees[id_policy_guarantee].usuario_ultima_modificacion = user_name

                        list_models_policy_guarantee = []
                        for policy_guarantee_deposit in policy_guarantee["policy_guarantee_deposits"]:
                            if(len(model.policy_guarantees[id_policy_guarantee].policy_guarantee_deposits) == 0):
                                #insert
                                model_policy_guarantee_deposit = PolicyGuaranteeDeposit()
                                model_policy_guarantee_deposit.iddef_policy_rule = policy_guarantee_deposit["iddef_policy_rule"]
                                model_policy_guarantee_deposit.percent = policy_guarantee_deposit["percent"]
                                model_policy_guarantee_deposit.option_percent = policy_guarantee_deposit["option_percent"]
                                model_policy_guarantee_deposit.number_nights_percent = policy_guarantee_deposit["number_nights_percent"]
                                model_policy_guarantee_deposit.fixed_amount = policy_guarantee_deposit["fixed_amount"]
                                model_policy_guarantee_deposit.estado = 1
                                model_policy_guarantee_deposit.usuario_creacion = user_name
                                list_models_policy_guarantee.append(model_policy_guarantee_deposit)

                            for id_policy_guarantee_deposit, value_policy_guarantee_deposit in enumerate(model.policy_guarantees[id_policy_guarantee].policy_guarantee_deposits):
                                policy_guarantee_deposit_index = int(policy_guarantee_deposit["iddef_policy_guarantee_deposit"]) if policy_guarantee_deposit["iddef_policy_guarantee_deposit"] else 0
                                if(model.policy_guarantees[id_policy_guarantee].policy_guarantee_deposits[id_policy_guarantee_deposit].iddef_policy_guarantee_deposit == policy_guarantee_deposit_index):
                                    #update
                                    model.policy_guarantees[id_policy_guarantee].policy_guarantee_deposits[id_policy_guarantee_deposit].iddef_policy_rule = policy_guarantee_deposit["iddef_policy_rule"]
                                    model.policy_guarantees[id_policy_guarantee].policy_guarantee_deposits[id_policy_guarantee_deposit].percent = policy_guarantee_deposit["percent"]
                                    model.policy_guarantees[id_policy_guarantee].policy_guarantee_deposits[id_policy_guarantee_deposit].option_percent = policy_guarantee_deposit["option_percent"]
                                    model.policy_guarantees[id_policy_guarantee].policy_guarantee_deposits[id_policy_guarantee_deposit].number_nights_percent = policy_guarantee_deposit["number_nights_percent"]
                                    model.policy_guarantees[id_policy_guarantee].policy_guarantee_deposits[id_policy_guarantee_deposit].fixed_amount = policy_guarantee_deposit["fixed_amount"]
                                    model.policy_guarantees[id_policy_guarantee].policy_guarantee_deposits[id_policy_guarantee_deposit].estado = policy_guarantee_deposit["estado"]
                                    model.policy_guarantees[id_policy_guarantee].policy_guarantee_deposits[id_policy_guarantee_deposit].usuario_ultima_modificacion = user_name
                                elif(policy_guarantee_deposit_index == 0):
                                    #insert
                                    model_policy_guarantee_deposit = PolicyGuaranteeDeposit()
                                    model_policy_guarantee_deposit.iddef_policy_rule = policy_guarantee_deposit["iddef_policy_rule"]
                                    model_policy_guarantee_deposit.percent = policy_guarantee_deposit["percent"]
                                    model_policy_guarantee_deposit.option_percent = policy_guarantee_deposit["option_percent"]
                                    model_policy_guarantee_deposit.number_nights_percent = policy_guarantee_deposit["number_nights_percent"]
                                    model_policy_guarantee_deposit.fixed_amount = policy_guarantee_deposit["fixed_amount"]
                                    model_policy_guarantee_deposit.estado = 1
                                    model_policy_guarantee_deposit.usuario_creacion = user_name
                                    list_models_policy_guarantee.append(model_policy_guarantee_deposit)
                                    break
                        for temp_policy_guarantee_deposit in list_models_policy_guarantee:
                            model.policy_guarantees[id_policy_guarantee].policy_guarantee_deposits.append(temp_policy_guarantee_deposit)
                    elif(policy_guarantee_index == 0):
                        #insert
                        model_policy_guarantee = PolicyGuarantee()
                        model_policy_guarantee.iddef_policy_guarantee_type = policy_guarantee["iddef_policy_guarantee_type"]
                        model_policy_guarantee.allow_hold_free = policy_guarantee["allow_hold_free"]
                        model_policy_guarantee.hold_duration = policy_guarantee["hold_duration"]
                        model_policy_guarantee.stay_dates_option = policy_guarantee["stay_dates_option"]
                        model_policy_guarantee.stay_dates = policy_guarantee["stay_dates"]
                        model_policy_guarantee.reminder_lead_time = policy_guarantee["reminder_lead_time"]
                        model_policy_guarantee.offer_last_chance_promotion = policy_guarantee["offer_last_chance_promotion"]
                        model_policy_guarantee.discount_per_night = policy_guarantee["discount_per_night"]
                        model_policy_guarantee.type_discount = policy_guarantee["type_discount"]
                        model_policy_guarantee.min_lead_time = policy_guarantee["min_lead_time"]
                        model_policy_guarantee.availability_threshold = policy_guarantee["availability_threshold"]
                        model_policy_guarantee.description_en = policy_guarantee["description_en"]
                        model_policy_guarantee.description_es = policy_guarantee["description_es"]
                        model_policy_guarantee.estado = 1
                        model_policy_guarantee.usuario_creacion = user_name
                        for policy_guarantee_deposit in policy_guarantee["policy_guarantee_deposits"]:
                            model_policy_guarantee_deposit = PolicyGuaranteeDeposit()
                            model_policy_guarantee_deposit.iddef_policy_rule = policy_guarantee_deposit["iddef_policy_rule"]
                            model_policy_guarantee_deposit.percent = policy_guarantee_deposit["percent"]
                            model_policy_guarantee_deposit.option_percent = policy_guarantee_deposit["option_percent"]
                            model_policy_guarantee_deposit.number_nights_percent = policy_guarantee_deposit["number_nights_percent"]
                            model_policy_guarantee_deposit.fixed_amount = policy_guarantee_deposit["fixed_amount"]
                            model_policy_guarantee_deposit.estado = 1
                            model_policy_guarantee_deposit.usuario_creacion = user_name
    
                            model_policy_guarantee.policy_guarantee_deposits.append(model_policy_guarantee_deposit)
                        list_models_policy_guarantees.append(model_policy_guarantee)
                        break

            # Se procesan Tax Groups
            for policy_tax_group in request.json.get("policy_tax_groups", []):
                if(len(model.policy_tax_groups) == 0):
                    #insert
                    model_policy_tax_group = PolicyTaxGroup()
                    #model_policy_tax_group.iddef_policy_tax_group = policy_tax_group["iddef_policy_tax_group"]
                    #model_policy_tax_group.iddef_policy = policy_tax_group["iddef_policy"]
                    model_policy_tax_group.iddef_policy_tax_base = policy_tax_group["iddef_policy_tax_base"]
                    model_policy_tax_group.iddef_policy_tax_type = policy_tax_group["iddef_policy_tax_type"]
                    model_policy_tax_group.iddef_policy_tax_price = policy_tax_group["iddef_policy_tax_price"]
                    model_policy_tax_group.iddef_policy_tax_vat = policy_tax_group["iddef_policy_tax_vat"]
                    model_policy_tax_group.amount = policy_tax_group["amount"]
                    model_policy_tax_group.max_amount = policy_tax_group["max_amount"]
                    model_policy_tax_group.is_custom_text = policy_tax_group["is_custom_text"]
                    model_policy_tax_group.description_en = policy_tax_group["description_en"]
                    model_policy_tax_group.description_es = policy_tax_group["description_es"]
                    model_policy_tax_group.use_maximum_amount = policy_tax_group["use_maximum_amount"]
                    model_policy_tax_group.use_custom_desc = policy_tax_group["use_custom_desc"]
                    model_policy_tax_group.use_ages_range = policy_tax_group["use_ages_range"]
                    model_policy_tax_group.age_ranges = policy_tax_group["age_ranges"] if "age_ranges" in policy_tax_group else []
                    model_policy_tax_group.use_dates_range = policy_tax_group["use_dates_range"]
                    model_policy_tax_group.date_ranges = policy_tax_group["date_ranges"] if "date_ranges" in policy_tax_group else []
                    model_policy_tax_group.estado = 1
                    model_policy_tax_group.usuario_creacion = user_name
                    list_models_policy_guarantees.append(model_policy_tax_group)
                for id_policy_tax_group, value_policy_tax_group in enumerate(model.policy_tax_groups):
                    policy_guarantee_index = int(policy_tax_group["iddef_policy_tax_group"]) if policy_tax_group["iddef_policy_tax_group"] else 0
                    if(model.policy_tax_groups[id_policy_tax_group].iddef_policy_tax_group == policy_guarantee_index):
                        #update
                        model.policy_tax_groups[id_policy_tax_group].iddef_policy_tax_base = policy_tax_group["iddef_policy_tax_base"]
                        model.policy_tax_groups[id_policy_tax_group].iddef_policy_tax_type = policy_tax_group["iddef_policy_tax_type"]
                        model.policy_tax_groups[id_policy_tax_group].iddef_policy_tax_price = policy_tax_group["iddef_policy_tax_price"]
                        model.policy_tax_groups[id_policy_tax_group].iddef_policy_tax_vat = policy_tax_group["iddef_policy_tax_vat"]
                        model.policy_tax_groups[id_policy_tax_group].amount = policy_tax_group["amount"]
                        model.policy_tax_groups[id_policy_tax_group].max_amount = policy_tax_group["max_amount"]
                        model.policy_tax_groups[id_policy_tax_group].is_custom_text = policy_tax_group["is_custom_text"]
                        model.policy_tax_groups[id_policy_tax_group].description_en = policy_tax_group["description_en"]
                        model.policy_tax_groups[id_policy_tax_group].description_es = policy_tax_group["description_es"]
                        model.policy_tax_groups[id_policy_tax_group].use_maximum_amount = policy_tax_group["use_maximum_amount"]
                        model.policy_tax_groups[id_policy_tax_group].use_custom_desc = policy_tax_group["use_custom_desc"]
                        model.policy_tax_groups[id_policy_tax_group].use_ages_range = policy_tax_group["use_ages_range"]
                        if "age_ranges" in policy_tax_group: model.policy_tax_groups[id_policy_tax_group].age_ranges = policy_tax_group["age_ranges"]
                        model.policy_tax_groups[id_policy_tax_group].use_dates_range = policy_tax_group["use_dates_range"]
                        if "date_ranges" in policy_tax_group: model.policy_tax_groups[id_policy_tax_group].date_ranges = policy_tax_group["date_ranges"]
                        model.policy_tax_groups[id_policy_tax_group].estado = policy_tax_group["estado"]
                        model.policy_tax_groups[id_policy_tax_group].usuario_ultima_modificacion = user_name
                    elif(policy_guarantee_index == 0):
                        #insert
                        model_policy_tax_group = PolicyTaxGroup()
                        #model_policy_tax_group.iddef_policy_tax_group = policy_tax_group["iddef_policy_tax_group"]
                        #model_policy_tax_group.iddef_policy = policy_tax_group["iddef_policy"]
                        model_policy_tax_group.iddef_policy_tax_base = policy_tax_group["iddef_policy_tax_base"]
                        model_policy_tax_group.iddef_policy_tax_type = policy_tax_group["iddef_policy_tax_type"]
                        model_policy_tax_group.iddef_policy_tax_price = policy_tax_group["iddef_policy_tax_price"]
                        model_policy_tax_group.iddef_policy_tax_vat = policy_tax_group["iddef_policy_tax_vat"]
                        model_policy_tax_group.amount = policy_tax_group["amount"]
                        model_policy_tax_group.max_amount = policy_tax_group["max_amount"]
                        model_policy_tax_group.is_custom_text = policy_tax_group["is_custom_text"]
                        model_policy_tax_group.description_en = policy_tax_group["description_en"]
                        model_policy_tax_group.description_es = policy_tax_group["description_es"]
                        model_policy_tax_group.use_maximum_amount = policy_tax_group["use_maximum_amount"]
                        model_policy_tax_group.use_custom_desc = policy_tax_group["use_custom_desc"]
                        model_policy_tax_group.use_ages_range = policy_tax_group["use_ages_range"]
                        model_policy_tax_group.age_ranges = policy_tax_group["age_ranges"] if "age_ranges" in policy_tax_group else []
                        model_policy_tax_group.use_dates_range = policy_tax_group["use_dates_range"]
                        model_policy_tax_group.date_ranges = policy_tax_group["date_ranges"] if "date_ranges" in policy_tax_group else []
                        model_policy_tax_group.estado = 1
                        model_policy_tax_group.usuario_creacion = user_name
                        list_models_policy_guarantees.append(model_policy_tax_group)


            """ for temp_policy_cancel_penalty in list_models_policy_cancel_penalties:
                model.policy_cancel_penalties.append(temp_policy_cancel_penalty) """

            for temp_policy_guarantees in list_models_policy_guarantees:
                model.policy_guarantees.append(temp_policy_guarantees)

            for temp_policy_tax_groups in list_models_tax_groups:
                model.policy_tax_groups.append(temp_policy_tax_groups)


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

class PolicyDefault(Resource):
    #api-policies-get-default-by-id
    # @base.access_middleware
    def get(self, id):
        try:
            response = {
                "Code": 200,
                "Msg": "Success",
                "Error": False,
                "data": PolicyFunctions.getPolicyConfigData(id)
            }
        except Exception as e:
            response = {
                "Code": 500,
                "Msg": str(e),
                "Error": True,
                "data": {}
            }

        return response

    #api-policies-post-single
    # @base.access_middleware
    def post(self):
        response = {}
        try:
            json_data = request.get_json(force=True)
            if request.json.get("iddef_policy_category") == None:
                schema = GetPolicyDefaultSchema(exclude=Util.get_default_excludes())
            else:
                schema = PolicyPostDefaultSchema(exclude=Util.get_default_excludes())
            data = schema.load(json_data)
            # property_model = Property.query.get(data["iddef_property"])

            user_data = base.get_token_data()
            user_name = user_data['user']['username']

            # if property_model is None:
            #   return {
            #       "Code": 404,
            #       "Msg": "property not found",
            #       "Error": True,
            #       "data": {}
            #   }

            count_same_code_policy = Model.query.filter(Model.policy_code==data["policy_code"]).with_entities(func.count()).scalar()
            if count_same_code_policy > 0:
                raise Exception("Duplicate Policy Code")

            if request.json.get("iddef_policy_category") != None:
                iddef_policy_category = data["iddef_policy_category"]
            else:
                iddef_policy_category = 1
            
            is_default = 0
            count_default_policy_category = Model.query.filter(Model.iddef_policy_category==iddef_policy_category, 
                Model.estado == 1).with_entities(func.count()).scalar()
            if count_default_policy_category == 0:
                if request.json.get("is_default") != None:
                    data["is_default"] = 1
                else:
                    is_default = 1

            model = Model()
            #model.iddef_policy = data["iddef_policy"]
            model.iddef_policy_category = iddef_policy_category
            model.policy_code = data["policy_code"]
            model.iddef_currency = request.json.get("iddef_currency", 1) #data["iddef_currency"]
            model.is_default = request.json.get("is_default", is_default) #data["is_default"]
            model.option_selected = request.json.get("option_selected", 0) #data["option_selected"]
            model.text_only_policy = request.json.get("text_only_policy", 0) #data["text_only_policy"]
            model.available_dates = request.json.get("available_dates", []) #data["available_dates"]
            model.estado = 1
            model.usuario_creacion = user_name

            #property_model.policies.append(model)

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

    #api-policies-single-put
    # @base.access_middleware
    def put(self, id):
        response = {}
        try:
            json_data = request.get_json(force=True)
            schema = GetPolicyDefaultSchema(exclude=Util.get_default_excludes())
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
            # if request.json.get("iddef_policy_category") != None:
            #   model.iddef_policy_category = data["iddef_policy_category"]
            if request.json.get("policy_code") != None:
                if model.policy_code != data["policy_code"]:
                    count_same_code_policy = Model.query.filter(Model.policy_code==data["policy_code"], Model.iddef_policy!=model.iddef_policy).with_entities(func.count()).scalar()
                    if count_same_code_policy > 0:
                        raise Exception("Duplicate Policy Code")
                model.policy_code = data["policy_code"]
            if request.json.get("iddef_currency") != None:
                model.iddef_currency = data["iddef_currency"]
            if request.json.get("is_default") != None:
                model.is_default = data["is_default"]
            if request.json.get("option_selected") != None:
                model.option_selected = data["option_selected"]
            if request.json.get("text_only_policy") != None:
                model.text_only_policy = data["text_only_policy"]
            if request.json.get("available_dates") != None:
                model.available_dates = data["available_dates"]
            if request.json.get("estado") != None:
                model.estado = data["estado"]
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

class PolicyDefaultListSearch(Resource):
    #api-policies-get-all-single
    # @base.access_middleware
    def get(self):
        try:
            isAll = request.args.get("all")

            data = Model()

            schema = PolicyRatePlanSchema(exclude=Util.get_default_excludes(), many=True)
            
            if isAll is not None:
                data = Model.query.all()
            else:
                data = Model.query.filter(Model.estado==1).all()

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

class PolicyListSearch(Resource):
    #api-policies-get-all
    # @base.access_middleware
    def get(self, category=0):
        try:
            if category == 1:
                schema = ModelCPSchema(exclude=Util.get_default_excludes(), many=True)
            elif category == 2:
                schema = ModelGSchema(exclude=Util.get_default_excludes(), many=True)
            elif category == 3:
                schema = ModelTSchema(exclude=Util.get_default_excludes(), many=True)
            else:
                schema = ModelSchema(exclude=Util.get_default_excludes(), many=True)
            
            data = Model.query.all()
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

    #api-policies-post
    # @base.access_middleware
    def post(self):
        response = {}
        try:
            json_data = request.get_json(force=True)
            #schema = ModelSchema(exclude=Util.get_default_excludes())
            schema = PolicyPostSchema(exclude=Util.get_default_excludes())
            data = schema.load(json_data)
            # property_model = Property.query.get(data["iddef_property"])

            user_data = base.get_token_data()
            user_name = user_data['user']['username']

            # if property_model is None:
            #   return {
            #       "Code": 404,
            #       "Msg": "property not found",
            #       "Error": True,
            #       "data": {}
            #   }

            count_same_code_policy = Model.query.filter(Model.policy_code==data["policy_code"]).with_entities(func.count()).scalar()
            if count_same_code_policy > 0:
                raise Exception("Duplicate Policy Code")

            model = Model()
            #model.iddef_policy = data["iddef_policy"]
            model.iddef_policy_category = data["iddef_policy_category"]
            model.policy_code = data["policy_code"]
            model.iddef_currency = data["iddef_currency"]
            model.is_default = data["is_default"]
            model.option_selected = data["option_selected"]
            model.text_only_policy = data["text_only_policy"]
            model.available_dates = request.json.get("available_dates", []) #data["available_dates"]
            model.estado = 1
            model.usuario_creacion = user_name

            validation_error = None
            if(data["iddef_policy_category"] == 1):
                if(len(request.json.get("policy_guarantees",[]))>0 or len(request.json.get("policy_tax_groups",[]))>0): validation_error = "Different category Information"
            elif(data["iddef_policy_category"] == 2):
                if(len(request.json.get("policy_tax_groups",[]))>0): validation_error = "Different category Information"
            elif(data["iddef_policy_category"] == 3):
                if(len(request.json.get("policy_guarantees",[]))>0): validation_error = "Different category Information"

            if(validation_error != None):
                return {
                    "Code": 500,
                    "Msg": validation_error,
                    "Error": True,
                    "data": {}
                }

            # se insertan los datos de penalties
            """ for policy_cancel_penalty in request.json.get("policy_cancel_penalties", []):
                model_policy_cancel_penalty = PolicyCancelPenalty()
                model_policy_cancel_penalty.penalty_name = policy_cancel_penalty["penalty_name"]
                model_policy_cancel_penalty.days_prior_to_arrival_deadline = policy_cancel_penalty["days_prior_to_arrival_deadline"]
                model_policy_cancel_penalty.time_date_deadline = policy_cancel_penalty["time_date_deadline"]
                model_policy_cancel_penalty.description_en = policy_cancel_penalty["description_en"]
                model_policy_cancel_penalty.description_es = policy_cancel_penalty["description_es"]
                model_policy_cancel_penalty.estado = 1
                model_policy_cancel_penalty.usuario_creacion = user_name
                for cancel_fee in policy_cancel_penalty["cancel_fees"]:
                    model_cancel_fee = PolicyPenaltyCancelFee()
                    model_cancel_fee.iddef_policy_rule = cancel_fee["iddef_policy_rule"]
                    model_cancel_fee.percent = cancel_fee["percent"]
                    model_cancel_fee.option_percent = cancel_fee["option_percent"]
                    model_cancel_fee.number_nights_percent = cancel_fee["number_nights_percent"]
                    model_cancel_fee.fixed_amount = cancel_fee["fixed_amount"]
                    model_cancel_fee.estado = 1
                    model_cancel_fee.usuario_creacion = user_name

                    model_policy_cancel_penalty.cancel_fees.append(model_cancel_fee)

                model.policy_cancel_penalties.append(model_policy_cancel_penalty) """

            #Se insertan los datos de guarantees
            for policy_guarantee in request.json.get("policy_guarantees", []):
                model_policy_guarantee = PolicyGuarantee()
                model_policy_guarantee.iddef_policy_guarantee_type = policy_guarantee["iddef_policy_guarantee_type"]
                model_policy_guarantee.allow_hold_free = policy_guarantee["allow_hold_free"]
                model_policy_guarantee.hold_duration = policy_guarantee["hold_duration"]
                model_policy_guarantee.stay_dates_option = policy_guarantee["stay_dates_option"]
                model_policy_guarantee.stay_dates = policy_guarantee["stay_dates"]
                model_policy_guarantee.reminder_lead_time = policy_guarantee["reminder_lead_time"]
                model_policy_guarantee.offer_last_chance_promotion = policy_guarantee["offer_last_chance_promotion"]
                model_policy_guarantee.discount_per_night = policy_guarantee["discount_per_night"]
                model_policy_guarantee.type_discount = policy_guarantee["type_discount"]
                model_policy_guarantee.min_lead_time = policy_guarantee["min_lead_time"]
                model_policy_guarantee.availability_threshold = policy_guarantee["availability_threshold"]
                model_policy_guarantee.description_en = policy_guarantee["description_en"]
                model_policy_guarantee.description_es = policy_guarantee["description_es"]
                model_policy_guarantee.estado = 1
                model_policy_guarantee.usuario_creacion = user_name
                for policy_guarantee_deposit in policy_guarantee["policy_guarantee_deposits"]:
                    model_policy_guarantee_deposit = PolicyGuaranteeDeposit()
                    model_policy_guarantee_deposit.iddef_policy_rule = policy_guarantee_deposit["iddef_policy_rule"]
                    model_policy_guarantee_deposit.percent = policy_guarantee_deposit["percent"]
                    model_policy_guarantee_deposit.option_percent = policy_guarantee_deposit["option_percent"]
                    model_policy_guarantee_deposit.number_nights_percent = policy_guarantee_deposit["number_nights_percent"]
                    model_policy_guarantee_deposit.fixed_amount = policy_guarantee_deposit["fixed_amount"]
                    model_policy_guarantee_deposit.estado = 1
                    model_policy_guarantee_deposit.usuario_creacion = user_name

                    model_policy_guarantee.policy_guarantee_deposits.append(model_policy_guarantee_deposit)

                model.policy_guarantees.append(model_policy_guarantee)

            # se insertan los datos de tax groups
            for policy_tax_group in request.json.get("policy_tax_groups", []):
                model_policy_tax_group = PolicyTaxGroup()
                model_policy_tax_group.iddef_policy_tax_base = policy_tax_group["iddef_policy_tax_base"]
                model_policy_tax_group.iddef_policy_tax_type = policy_tax_group["iddef_policy_tax_type"]
                model_policy_tax_group.iddef_policy_tax_price = policy_tax_group["iddef_policy_tax_price"]
                model_policy_tax_group.iddef_policy_tax_vat = policy_tax_group["iddef_policy_tax_vat"]
                model_policy_tax_group.amount = policy_tax_group["amount"]
                model_policy_tax_group.max_amount = policy_tax_group["max_amount"]
                model_policy_tax_group.is_custom_text = policy_tax_group["is_custom_text"]
                model_policy_tax_group.description_en = policy_tax_group["description_en"]
                model_policy_tax_group.description_es = policy_tax_group["description_es"]
                model_policy_tax_group.use_maximum_amount = policy_tax_group["use_maximum_amount"]
                model_policy_tax_group.use_custom_desc = policy_tax_group["use_custom_desc"]
                model_policy_tax_group.use_ages_range = policy_tax_group["use_ages_range"]
                model_policy_tax_group.age_ranges = policy_tax_group["age_ranges"] if "age_ranges" in policy_tax_group else []
                model_policy_tax_group.use_dates_range = policy_tax_group["use_dates_range"]
                model_policy_tax_group.date_ranges = policy_tax_group["date_ranges"] if "date_ranges" in policy_tax_group else []
                model_policy_tax_group.estado = 1
                model_policy_tax_group.usuario_creacion = user_name

                model.policy_tax_groups.append(model_policy_tax_group)

            # property_model.policies.append(model)

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

class PolicyListCategorySearch(Resource):
    #api-policies-get-all-category
    # @base.access_middleware
    def get(self, category):
        try:
            if category == 1:
                schema = ModelCPSchema(exclude=Util.get_default_excludes(), many=True)
            elif category == 2:
                schema = ModelGSchema(exclude=Util.get_default_excludes(), many=True)
            elif category == 3:
                schema = ModelTSchema(exclude=Util.get_default_excludes(), many=True)
            else:
                schema = ModelSchema(exclude=Util.get_default_excludes(), many=True)
            
            if category == 1:
                resultado = []
                data = Model.query.filter(Model.iddef_policy_category==category)
                result = schema.dump(data)
                for item in result:
                    if len(item["policy_cancel_penalties"]) > 0:
                        details = {}
                        details["base"] = list(filter(lambda elem_base: elem_base["id_type_detail"] == 0, item["policy_cancel_penalties"]))
                        details["seasonal_exception"] = list(filter(lambda elem_exception: elem_exception["id_type_detail"] == 1, item["policy_cancel_penalties"]))
                        details["no_refundable"] = list(filter(lambda elem_no_refundable: elem_no_refundable["id_type_detail"] == 2, item["policy_cancel_penalties"]))
                        item["policy_cancel_penalties"] = details
                    resultado.append(item)
            else:
                data = Model.query.filter(Model.iddef_policy_category==category)
                resultado = schema.dump(data)

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
                    "data": resultado
                }
        except Exception as e:
            response = {
                "Code": 500,
                "Msg": str(e),
                "Error": True,
                "data": {}
            }
        return response

class PolicyPropertyCategorySearch(Resource):
    #Anteriormente - def get(self, property, category):
    # @base.access_middleware
    def get(self, category):
        try:
            #property_data = Property.query.get(property)
            #data = property_data.policies.filter(Model.iddef_policy_category==category, Model.estado == 1).all()

            data = Model.query.filter(Model.iddef_policy_category==category, Model.estado == 1).all()

            if category == 1:
                schema = ModelCPSchema(exclude=Util.get_default_excludes(), many=True)
            elif category == 2:
                schema = ModelGSchema(exclude=Util.get_default_excludes(), many=True)
            elif category == 3:
                schema = ModelTSchema(exclude=Util.get_default_excludes(), many=True)
            else:
                schema = ModelSchema(exclude=Util.get_default_excludes(), many=True)

            #data = list(filter(lambda elem_policy: elem_policy.iddef_policy_category == category, property_data.policies))

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
                    "data": schema.dump(data, many=True)
                }
        except Exception as e:
            response = {
                "Code": 500,
                "Msg": str(e),
                "Error": True,
                "data": {}
            }
        return response

    #api-policies-set_default-all-category
    #Set default by category
    #Anteriormente - def put(self, id, category, property):
    # @base.access_middleware
    def put(self, id, category):
        response = {}
        try:
            # property_data = Property.query.get(property)
            # data = property_data.policies.filter(Model.iddef_policy_category==category, Model.estado == 1).all()

            user_data = base.get_token_data()
            user_name = user_data['user']['username']

            data = Model.query.filter(Model.iddef_policy_category==category).all()
    
            if data is None or len(data) == 0:
                return {
                    "Code": 404,
                    "Msg": "data not found",
                    "Error": True,
                    "data": {}
                }
            id_exists = next((x for x in data if x.iddef_policy == id), None)

            if id_exists is None:
                return {
                    "Code": 404,
                    "Msg": "Id is not in category or It is not active",
                    "Error": True,
                    "data": {}
                }

            for policy_id, policy_value in enumerate(data):
                if(data[policy_id].iddef_policy == id):
                    data[policy_id].is_default = 1
                else:
                    data[policy_id].is_default = 0

            if category == 1:
                schema = ModelCPSchema(exclude=Util.get_default_excludes(), many=True)
            elif category == 2:
                schema = ModelGSchema(exclude=Util.get_default_excludes(), many=True)
            elif category == 3:
                schema = ModelTSchema(exclude=Util.get_default_excludes(), many=True)
            else:
                schema = ModelSchema(exclude=Util.get_default_excludes(), many=True)

            db.session.commit()

            response = {
                "Code": 200,
                "Msg": "Success",
                "Error": False,
                "data": schema.dump(data)
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


# Se elimina API debido al retiro de la relación entre Property-Policy
# class PolicyListPropertySearch(Resource):
#   def get(self, property):
#       try:
#           property_data = Property.query.get(property)
#           data = property_data.policies
#           schema = ModelSchema(exclude=Util.get_default_excludes(), many=True)

#           if data is None:
#               response = {
#                   "Code": 200,
#                   "Msg": "Success",
#                   "Error": False,
#                   "data": {}
#               }
#           else:
#               response = {
#                   "Code": 200,
#                   "Msg": "Success",
#                   "Error": False,
#                   "data": schema.dump(data, many=True)
#               }
#       except Exception as e:
#           response = {
#               "Code": 500,
#               "Msg": str(e),
#               "Error": True,
#               "data": {}
#           }
#       return response

class PolicyDelete(Resource):
    #api-policies-delete
    # @base.access_middleware
    def put(self, id):
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

            model.estado = 0
            model.usuario_ultima_modificacion = user_name

            # for id_policy_cancel_penalty, value_policy_cancel_penalty in enumerate(model.policy_cancel_penalties):
            #   model.policy_cancel_penalties[id_policy_cancel_penalty].estado = 0
            #   for id_cancel_fee, value_cancel_fee in enumerate(model.policy_cancel_penalties[id_policy_cancel_penalty].cancel_fees):
            #       model.policy_cancel_penalties[id_policy_cancel_penalty].cancel_fees[id_cancel_fee].estado = 0

            # for id_policy_guarantee, value_policy_guarantee in enumerate(model.policy_guarantees):
            #   model.policy_guarantees[id_policy_guarantee].estado = 0
            #   for id_policy_guarantee_deposit, value_policy_guarantee_deposit in enumerate(model.policy_guarantees[id_policy_guarantee].policy_guarantee_deposits):
            #       model.policy_guarantees[id_policy_guarantee].policy_guarantee_deposits[id_policy_guarantee_deposit].estado = 0

            # for id_policy_tax_group, value_policy_tax_group in enumerate(model.policy_tax_groups):
            #   model.policy_tax_groups[id_policy_tax_group].estado = 0
            
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

class PolicyStatus(Resource):
    #api-policies-change-status
    # @base.access_middleware
    def put(self, id, estado):
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

            if estado == 0 or estado == 1:
                pass
            else:
                raise Exception("Status not valid")

            model.estado = estado
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

class PublicPolicies(Resource):
    #api-public-policies_ratesplans-post
    @PublicAuth.access_middleware
    def post(self):
        response = {}

        try:

            dataRq = request.get_json(force=True)
            schema = GetPolicyRatePlanSchema()
            data = schema.load(dataRq)
            
            today = datetime.datetime.now().date()
            lang_code = data["lang_code"]
            id_rateplans = set(data["id_rateplans"])

            funcText = textFuntions()

            data_policy = []
            for x,y in enumerate(id_rateplans):
                data_rateplan = rateplanModel.query.get(y)
                if data_rateplan is not None:
                    refundable = data_rateplan.refundable
                    txtData = funcText.getTextLangInfo("op_rateplan","commercial_name",\
                    lang_code,y)
                    rate_plan_name = txtData.text if txtData is not None else ""

                    policies = PolicyFunctions.get_policy_by_rateplan(y,\
                    today,lang_code=lang_code, refundable=not refundable)
                    policies["id_rateplan"] = y
                    policies["rate_plan_name"] = rate_plan_name
                    
                    data_policy.append(policies)
            
            response = {
                "Code": 200,
                "Msg": "Success",
                "Error": False,
                "data": data_policy
            } 

        except ValidationError as error:
            db.session.rollback()
            response = {
                "Code": 500,
                "Msg": error.messages,
                "Error": True,
                "data": []
            }
        except Exception as e:
            db.session.rollback()
            response = {
                "Code": 500,
                "Msg": str(e),
                "Error": True,
                "data": []
            }

        return response