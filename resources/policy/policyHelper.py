from flask import Flask, request
from flask_restful import Resource
from marshmallow import ValidationError
from config import db,base
from models.policy import Policy as Model, PolicyTSchema as TaxModelSchema, GetPolicyTSchema as GetTaxModelSchema, GetPolicyPublicSchema as GetPolicySchema, PolicySchema as ModelSchema, PolicyCPSchema as ModelCPSchema, PolicyGSchema as ModelGSchema, PolicyCPSchema as CancelModelSchema, GetPolicyCPSchema as GetCancelModelSchema, GetPolicyGSchema as GetGuaranteeModelSchema
from models.policy_tax_group import PolicyTaxGroup as ModelTaxGroup
from models.rateplan_policy import RatePlanPolicy as ModelRPP
from models.rateplan import RatePlan as ModelRP
from models.text_lang import TextLang as tlModel
from resources.restriction.restricctionHelper import RestricctionFunction
from common.util import Util
from operator import itemgetter
from sqlalchemy import or_, and_, func
import datetime, decimal
import json
from datetime import datetime as dt

class PolicyFunctions():
    @staticmethod
    def getPolicyTaxes(rateplan, start_date, end_date, isFormat=False):
        rec_class = RestricctionFunction()
        rec_class.checkParameterType(param_name="start_date", param_value=start_date, param_type=str, isDate=True)
        rec_class.checkParameterType(param_name="end_date", param_value=end_date, param_type=str, isDate=True)
        rec_class.checkParameterType(param_name="rateplan", param_value=rateplan, param_type=int)

        schema = TaxModelSchema(exclude=Util.get_default_excludes())

        query = "SELECT * FROM def_policy INNER JOIN def_policy_tax_group ON def_policy_tax_group.iddef_policy = def_policy.iddef_policy INNER JOIN op_rateplan_policy ON op_rateplan_policy.iddef_policy = def_policy.iddef_policy INNER JOIN op_rateplan ON op_rateplan.idop_rateplan = op_rateplan_policy.idop_rateplan"
        query_where = " WHERE def_policy.iddef_policy_category = 3 AND op_rateplan_policy.idop_rateplan = :rateplan AND def_policy.estado = 1 AND def_policy_tax_group.estado = 1 AND op_rateplan.estado = 1 AND op_rateplan_policy.estado = 1 "
        query_join = ""
        query_date = ""
        params = {}
        params["rateplan"] = int(rateplan)
        max_json_length = dict(db.session.execute(str('SELECT MAX(max_data) AS max_data FROM (SELECT MAX(JSON_LENGTH(available_dates)) AS max_data FROM def_policy) AS max_lengths;'), {}).fetchone())["max_data"]

        if(max_json_length > 0):
            query_join += " CROSS JOIN(SELECT 0 idx"
            for x in range(1,max_json_length):
                query_join += " UNION ALL SELECT " + str(x)
            query_join += ") AS n"

        if max_json_length > 0:
            query_date = " AND ((JSON_EXTRACT(def_policy.available_dates, CONCAT('$[', n.idx, '].start_date')) <= :start_date AND JSON_EXTRACT(def_policy.available_dates, CONCAT('$[', n.idx, '].start_date')) <= :end_date        AND JSON_EXTRACT(def_policy.available_dates, CONCAT('$[', n.idx, '].end_date')) >= :start_date AND JSON_EXTRACT(def_policy.available_dates, CONCAT('$[', n.idx, '].end_date')) >= :end_date) OR (JSON_EXTRACT(def_policy.available_dates, CONCAT('$[', n.idx, '].start_date')) > :start_date AND JSON_EXTRACT(def_policy.available_dates, CONCAT('$[', n.idx, '].end_date')) >= :end_date AND JSON_EXTRACT(def_policy.available_dates, CONCAT('$[', n.idx, '].start_date')) <= :end_date AND JSON_EXTRACT(def_policy.available_dates, CONCAT('$[', n.idx, '].end_date')) > :start_date) OR (JSON_EXTRACT(def_policy.available_dates, CONCAT('$[', n.idx, '].start_date')) <= :start_date AND JSON_EXTRACT(def_policy.available_dates, CONCAT('$[', n.idx, '].end_date')) < :end_date AND JSON_EXTRACT(def_policy.available_dates, CONCAT('$[', n.idx, '].start_date')) < :end_date AND JSON_EXTRACT(def_policy.available_dates, CONCAT('$[', n.idx, '].end_date')) >= :start_date) OR def_policy.available_dates LIKE '[]')"
            query = query + " "+ query_join + query_where + query_date
            params["start_date"] = str(start_date)
            params["end_date"] = str(end_date)
        else:
            query = query + " "+ query_join + " " + query_where + " AND def_policy.available_dates LIKE '[]'"

        schema2 = GetPolicySchema()
        data = db.session.execute(query, params).first()

        if data is not None:
            datos = schema2.dump(data)
            result_policy = Model.query.filter(Model.iddef_policy==datos["iddef_policy"]).first()
        else:
            result_policy = None
        
        if isFormat:
            dataPolicy = schema.dump(result_policy)
            policy = PolicyFunctions.format_policy_taxes(dataPolicy)
        else:
            policy = schema.dump(result_policy)

        return policy
    
    @staticmethod
    def format_policy_taxes(data_policy):
        objt = {}
        if len(data_policy) > 0:
            objt["tax_currency"] = data_policy["currency_code"].upper()
            objt["dates"] = data_policy["available_dates"]
            objt["apply_dates"] = False
            if len(data_policy["available_dates"]) > 0:
                objt["apply_dates"] = True
            objt["apply_max"] = False
            objt["max_amount"] = 0.0
            if data_policy["policy_tax_groups"][0]["use_maximum_amount"] == 1:
                objt["apply_max"] = True
                objt["max_amount"] = round(float(data_policy["policy_tax_groups"][0]["max_amount"]),2)
            objt["type"] = data_policy["policy_tax_groups"][0]["iddef_policy_tax_base"]
            objt["value"] = 0.0
            if objt["type"] != 2:
                objt["value"] = round(float(data_policy["policy_tax_groups"][0]["amount"]),2)
            else:
                objt["value"] = int(round(float(data_policy["policy_tax_groups"][0]["amount"]),0))
                if objt["value"] == 0:
                    objt["value"] = 1

        return objt
    
    @staticmethod 
    def getPolicyConfigData(id):
        """
            Format and retrieve config data of policy.
            param: policy int id
            
            return: data dict Policy config data
        """
        data = {}

        result = Model.query.get(id)

        if result is None:
            return data
        
        if result.iddef_policy_category == 1:
            schema = ModelCPSchema(exclude=Util.get_default_excludes())
        elif result.iddef_policy_category == 2:
            schema = ModelGSchema(exclude=Util.get_default_excludes())
        elif result.iddef_policy_category == 3:
            schema = TaxModelSchema(exclude=Util.get_default_excludes())
        else:
            schema = ModelSchema(exclude=Util.get_default_excludes())

        data = schema.dump(result)

        if("policy_cancel_penalties" in data):
            details = {}
            details["base"] = list(filter(lambda elem_base: elem_base["estado"] == 1 and elem_base["id_type_detail"] == 0, data["policy_cancel_penalties"]))
            details["seasonal_exception"] = list(filter(lambda elem_exception: elem_exception["id_type_detail"] == 1, data["policy_cancel_penalties"]))
            details["no_refundable"] = list(filter(lambda elem_no_refundable: elem_no_refundable["id_type_detail"] == 2, data["policy_cancel_penalties"]))
            data["policy_cancel_penalties"] = details
        if("policy_guarantees" in data):
            for policy_guarantee_id, policy_guarantee_value in enumerate(data["policy_guarantees"]):
                list_policy_guarantee_deposits = list(filter(lambda elem_policy_guarantee_deposit: elem_policy_guarantee_deposit["estado"] == 1, policy_guarantee_value["policy_guarantee_deposits"]))
                data["policy_guarantees"][policy_guarantee_id]["policy_guarantee_deposits"] = list_policy_guarantee_deposits
                list_policy_guarantee_antifrauds = list(filter(lambda elem_policy_guarantee_antifraud: elem_policy_guarantee_antifraud["estado"] == 1, policy_guarantee_value["policy_guarantee_antifrauds"]))
                data["policy_guarantees"][policy_guarantee_id]["policy_guarantee_antifrauds"] = list_policy_guarantee_antifrauds
            list_policy_guarantees = list(filter(lambda elem_policy_guarantee: elem_policy_guarantee["estado"] == 1, data["policy_guarantees"]))
            data["policy_guarantees"] = list_policy_guarantees
        if("policy_tax_groups" in data):
            list_policy_tax_groups = list(filter(lambda elem_policy_tax_group: elem_policy_tax_group["estado"] == 1, data["policy_tax_groups"]))
            data["policy_tax_groups"] = list_policy_tax_groups

        return data

    @staticmethod
    def getPolicyCancel(rateplan, start_date, end_date):
        rec_class = RestricctionFunction()
        rec_class.checkParameterType(param_name="start_date", param_value=start_date, param_type=str, isDate=True)
        rec_class.checkParameterType(param_name="end_date", param_value=end_date, param_type=str, isDate=True)
        rec_class.checkParameterType(param_name="rateplan", param_value=rateplan, param_type=int)

        schema = CancelModelSchema(exclude=Util.get_default_excludes())

        query = "SELECT * FROM def_policy INNER JOIN op_rateplan_policy ON op_rateplan_policy.iddef_policy = def_policy.iddef_policy INNER JOIN op_rateplan ON op_rateplan.idop_rateplan = op_rateplan_policy.idop_rateplan"
        query_where = " WHERE def_policy.iddef_policy_category = 1 AND op_rateplan_policy.idop_rateplan = :rateplan AND def_policy.estado = 1 AND op_rateplan.estado = 1 AND op_rateplan_policy.estado = 1 "
        query_join = ""
        query_date = ""
        params = {}
        params["rateplan"] = int(rateplan)
        max_json_length = dict(db.session.execute(str('SELECT MAX(max_data) AS max_data FROM (SELECT MAX(JSON_LENGTH(available_dates)) AS max_data FROM def_policy) AS max_lengths;'), {}).fetchone())["max_data"]

        if(max_json_length > 0):
            query_join += " CROSS JOIN(SELECT 0 idx"
            for x in range(1,max_json_length):
                query_join += " UNION ALL SELECT " + str(x)
            query_join += ") AS n"

        if max_json_length > 0:
            query_date = " AND ((JSON_EXTRACT(def_policy.available_dates, CONCAT('$[', n.idx, '].start_date')) <= :start_date AND JSON_EXTRACT(def_policy.available_dates, CONCAT('$[', n.idx, '].start_date')) <= :end_date        AND JSON_EXTRACT(def_policy.available_dates, CONCAT('$[', n.idx, '].end_date')) >= :start_date AND JSON_EXTRACT(def_policy.available_dates, CONCAT('$[', n.idx, '].end_date')) >= :end_date) OR (JSON_EXTRACT(def_policy.available_dates, CONCAT('$[', n.idx, '].start_date')) > :start_date AND JSON_EXTRACT(def_policy.available_dates, CONCAT('$[', n.idx, '].end_date')) >= :end_date AND JSON_EXTRACT(def_policy.available_dates, CONCAT('$[', n.idx, '].start_date')) <= :end_date AND JSON_EXTRACT(def_policy.available_dates, CONCAT('$[', n.idx, '].end_date')) > :start_date) OR (JSON_EXTRACT(def_policy.available_dates, CONCAT('$[', n.idx, '].start_date')) <= :start_date AND JSON_EXTRACT(def_policy.available_dates, CONCAT('$[', n.idx, '].end_date')) < :end_date AND JSON_EXTRACT(def_policy.available_dates, CONCAT('$[', n.idx, '].start_date')) < :end_date AND JSON_EXTRACT(def_policy.available_dates, CONCAT('$[', n.idx, '].end_date')) >= :start_date) OR def_policy.available_dates LIKE '[]')"
            query = query + " "+ query_join + query_where + query_date
            params["start_date"] = str(start_date)
            params["end_date"] = str(end_date)
        else:
            query = query + " "+ query_join + " " + query_where + " AND def_policy.available_dates LIKE '[]'"

        schema2 = GetPolicySchema()
        data = db.session.execute(query, params).first()

        if data is not None:
            datos = schema2.dump(data)
            result_policy = Model.query.filter(Model.iddef_policy==datos["iddef_policy"]).first()
        else:
            result_policy = None

        return schema.dump(result_policy)

    @staticmethod
    def getPolicyGuarantee(rateplan, start_date, end_date):
        rec_class = RestricctionFunction()
        rec_class.checkParameterType(param_name="start_date", param_value=start_date, param_type=str, isDate=True)
        rec_class.checkParameterType(param_name="end_date", param_value=end_date, param_type=str, isDate=True)
        rec_class.checkParameterType(param_name="rateplan", param_value=rateplan, param_type=int)

        schema = ModelGSchema(exclude=Util.get_default_excludes())

        query = "SELECT * FROM def_policy INNER JOIN def_policy_guarantee ON def_policy_guarantee.iddef_policy = def_policy.iddef_policy INNER JOIN op_rateplan_policy ON op_rateplan_policy.iddef_policy = def_policy.iddef_policy INNER JOIN op_rateplan ON op_rateplan.idop_rateplan = op_rateplan_policy.idop_rateplan"
        query_where = " WHERE def_policy.iddef_policy_category = 2 AND op_rateplan_policy.idop_rateplan = :rateplan AND def_policy.estado = 1 AND def_policy_guarantee.estado = 1 AND op_rateplan.estado = 1 AND op_rateplan_policy.estado = 1 "
        query_join = ""
        query_date = ""
        params = {}
        params["rateplan"] = int(rateplan)
        max_json_length = dict(db.session.execute(str('SELECT MAX(max_data) AS max_data FROM (SELECT MAX(JSON_LENGTH(available_dates)) AS max_data FROM def_policy) AS max_lengths;'), {}).fetchone())["max_data"]

        if(max_json_length > 0):
            query_join += " CROSS JOIN(SELECT 0 idx"
            for x in range(1,max_json_length):
                query_join += " UNION ALL SELECT " + str(x)
            query_join += ") AS n"

        if max_json_length > 0:
            query_date = " AND ((JSON_EXTRACT(def_policy.available_dates, CONCAT('$[', n.idx, '].start_date')) <= :start_date AND JSON_EXTRACT(def_policy.available_dates, CONCAT('$[', n.idx, '].start_date')) <= :end_date        AND JSON_EXTRACT(def_policy.available_dates, CONCAT('$[', n.idx, '].end_date')) >= :start_date AND JSON_EXTRACT(def_policy.available_dates, CONCAT('$[', n.idx, '].end_date')) >= :end_date) OR (JSON_EXTRACT(def_policy.available_dates, CONCAT('$[', n.idx, '].start_date')) > :start_date AND JSON_EXTRACT(def_policy.available_dates, CONCAT('$[', n.idx, '].end_date')) >= :end_date AND JSON_EXTRACT(def_policy.available_dates, CONCAT('$[', n.idx, '].start_date')) <= :end_date AND JSON_EXTRACT(def_policy.available_dates, CONCAT('$[', n.idx, '].end_date')) > :start_date) OR (JSON_EXTRACT(def_policy.available_dates, CONCAT('$[', n.idx, '].start_date')) <= :start_date AND JSON_EXTRACT(def_policy.available_dates, CONCAT('$[', n.idx, '].end_date')) < :end_date AND JSON_EXTRACT(def_policy.available_dates, CONCAT('$[', n.idx, '].start_date')) < :end_date AND JSON_EXTRACT(def_policy.available_dates, CONCAT('$[', n.idx, '].end_date')) >= :start_date) OR def_policy.available_dates LIKE '[]')"
            query = query + " "+ query_join + query_where + query_date
            params["start_date"] = str(start_date)
            params["end_date"] = str(end_date)
        else:
            query = query + " "+ query_join + " " + query_where + " AND def_policy.available_dates LIKE '[]'"

        schema2 = GetPolicySchema()
        data = db.session.execute(query, params).first()

        if data is not None:
            datos = schema2.dump(data)
            result_policy = Model.query.filter(Model.iddef_policy==datos["iddef_policy"]).first()
        else:
            result_policy = None

        return schema.dump(result_policy)
    
    @staticmethod
    def get_policy_by_rateplan(idRateplan,booking_start_date, lang_code="EN", refundable = False):

        data = {}

        cancel_policy = ""
        guarantee_policy = ""
        tax_policy = ""        
        #booking_start_date = dates.datetime(booking_start_date.year, booking_start_date.month, booking_start_date.day)
        
        rate_plan_policies = Model.query.join(ModelRPP, Model.iddef_policy == ModelRPP.iddef_policy)\
        .filter(ModelRPP.idop_rateplan==idRateplan, ModelRPP.estado==1, Model.estado==1).all()

        cancelacionList = [ rppol for rppol in rate_plan_policies if rppol.iddef_policy_category == 1]
        garantiaList = [rppol for rppol in rate_plan_policies if rppol.iddef_policy_category == 2]
        taxList = [rppol for rppol in rate_plan_policies if rppol.iddef_policy_category == 3]
        
        if len(cancelacionList) > 0 :
            for cancelItem in cancelacionList:
                policy_detail_cancel = None
                
                #check if is required refundable cancellation policy
                if refundable:
                    policy_detail_cancel = next((item for item in cancelItem.policy_cancel_penalties if item.estado == 1 \
                    and item.is_base == 0 and item.is_refundable == 1 \
                    and (booking_start_date >= item.start_date and booking_start_date <= item.end_date)), None)
                
                #if not found refundable or refundable is false, search for dates
                if not policy_detail_cancel:
                    policy_detail_cancel = next((item for item in cancelItem.policy_cancel_penalties if item.estado == 1 \
                    and item.is_base == 0 and item.is_refundable == 0 \
                    and (booking_start_date >= item.start_date and booking_start_date <= item.end_date)), None)
                
                #if policy was found, get the lang description and break loop
                if policy_detail_cancel:
                    if lang_code.upper() != "ES":
                        cancel_policy = policy_detail_cancel.description_en
                    else:
                        cancel_policy = policy_detail_cancel.description_es
                    break
                else:
                    #in other case, looking for base cancellation and break loop
                    policy_detail_cancel = next((item for item in cancelItem.policy_cancel_penalties if item.estado == 1 \
                        and item.is_base == 1), None)
                    if policy_detail_cancel:
                        if lang_code.upper() != "ES":
                            cancel_policy = policy_detail_cancel.description_en
                        else:
                            cancel_policy = policy_detail_cancel.description_es
                        break
        
        if len(garantiaList) > 0:
            for item in garantiaList:
                for range_date in item.available_dates:
                    start_date = datetime.datetime.strptime(range_date.get("start_date"), '%Y-%m-%d')
                    end_date = datetime.datetime.strptime(range_date.get("end_date"), '%Y-%m-%d')
                    if booking_start_date >= start_date.date() and booking_start_date <= end_date.date():
                        if lang_code.upper() != "ES":
                            guarantee_policy = item.policy_guarantees[0].description_en
                        else:
                            guarantee_policy = item.policy_guarantees[0].description_es
                        break
            else:
                if lang_code.upper() != "ES":
                    guarantee_policy = garantiaList[0].policy_guarantees[0].description_en
                else:
                    guarantee_policy = garantiaList[0].policy_guarantees[0].description_es
        
        if len(taxList):
            for item in taxList:
                for range_date in item.available_dates:
                    start_date = datetime.datetime.strptime(range_date.get("start_date"), '%Y-%m-%d')
                    end_date = datetime.datetime.strptime(range_date.get("end_date"), '%Y-%m-%d')
                    if booking_start_date >= start_date.date() and booking_start_date <= end_date.date():
                        if lang_code.upper() != "ES":
                            tax_policy = item.policy_tax_groups[0].description_en
                        else:
                            tax_policy = item.policy_tax_groups[0].description_es
                        break
            else:
                if lang_code.upper() != "ES":
                    tax_policy = taxList[0].policy_tax_groups[0].description_en
                else:
                    tax_policy = taxList[0].policy_tax_groups[0].description_es

        data = {
            "cancel_policy":cancel_policy,
            "guarantee_policy":guarantee_policy,
            "tax_policy":tax_policy
        }

        return data