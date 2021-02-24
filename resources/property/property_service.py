from config import db, base
from models.property import Property as pModel, GetSearchEmailsSchema as eModelSchema
from models.email_contact import EmailContact as ecModel
from models.contact import Contact as cModel
from models.rateplan_policy import RatePlanPolicy as rpModel
from models.policy_guarantee import PolicyGuarantee as pgModel
from sqlalchemy.sql.expression import and_, or_, func
#from common.external_credentials import ExternalCredentials
#from common.custom_log_request import CustomLogRequest
import datetime

class PropertyService():
    @staticmethod
    def get_email_contact(iddef_property, separator = None):
        """
            Return email list contact of the property.
            param: iddef_property ID property
            param: separator Indicate if the email is separate by some special character
            return: Dict with email
        """ 
        data = None
        schema = eModelSchema()
        data_emails = pModel.query.get(iddef_property)
        
        if data_emails is not None:
            info_contacts1 = list(filter(lambda elem_contact: elem_contact.estado == 1 and elem_contact.iddef_contact_type == 1, data_emails.contacts))
            info_contacts2 = list(filter(lambda elem_contact: elem_contact.estado == 1 and elem_contact.iddef_contact_type == 2, data_emails.contacts))
            info_contacts = info_contacts1 + info_contacts2
            ids_contacts = [elem_contacts.iddef_contact for elem_contacts in info_contacts]
            emails = ecModel.query.add_columns(ecModel.email).filter(ecModel.iddef_contact.in_(ids_contacts), ecModel.estado==1, ecModel.notify_booking==1).all()
            data = schema.dump(emails, many=True)
            
            if separator:
                return separator.join(aux["email"] for aux in data)
        
        return data

    @staticmethod
    def validate_code_property(property_code, username):
        response = {
            "error": False,
            "data": {},
            "validate": False,
            "message": ""
        }
        request_service= {
        }
        try:
            method = 'GET'
            url_base = base.get_url("clever_code")
            url_service= '{}/propiedad/search'.format(url_base)

            response_api = PropertyService.do_request(endpoint=url_service, method=method, \
            data=request_service, username = username)
            if len(response_api) > 0:
                filter_property = list(filter(lambda elem_property: elem_property['estado'] == '1', response_api))
                for item in filter_property:
                    if item['id_opera'] == property_code or item['id_hotel'] == property_code:
                        response["validate"] = True
                        
        except Exception as e:
            response["error"] = True
            response["message"] = str(e)

        return response

    @staticmethod
    def do_request(endpoint, method, data, username):
        '''
            Generic method to do request
            :param endpoint: endpoint API Service
            :param method: HTTP method type (post, get, put, patch, etc...)
            :param data: dictionary data to send to API Service
        '''
        external_credentials = ExternalCredentials()
        token = external_credentials.get_token(base.system_id)
        timeout = 15
        use_token = False
        response = CustomLogRequest.do_request(url=endpoint, method=method, \
            data=data, timeout=timeout, use_token=use_token, token = token, username = username)
        
        return response
    
    @staticmethod
    def get_hold_duration_policy(date_today,property_code,from_date,to_date,rooms):
        """
            Return policy guarantee of the property and rateplan.
        """
        data_rate = []
        data = [
            {
            "on_hold": False,
            "hold_duration": 0, 
            "expiry_date": "",
            "min_lead_time":0 
            }
        ]
        for itm in rooms:
            data_polices = pgModel.query.join(rpModel,rpModel.iddef_policy==pgModel.iddef_policy).filter(pgModel.estado==1,\
            rpModel.idop_rateplan == itm['idop_rate_plan'], pgModel.allow_hold_free ==1,\
            or_(pgModel.stay_dates_option==1,\
            and_(pgModel.stay_dates_option==2,\
            or_(and_(func.json_extract(pgModel.stay_dates, '$.start') >= from_date,\
            func.json_extract(pgModel.stay_dates, '$.end') <= to_date),\
            and_(func.json_extract(pgModel.stay_dates, '$.start') < from_date,\
            func.json_extract(pgModel.stay_dates, '$.end') > to_date))),\
            and_(pgModel.stay_dates_option==3,\
            or_(func.json_extract(pgModel.stay_dates, '$.start') < from_date,\
            func.json_extract(pgModel.stay_dates, '$.end') > to_date)))).order_by(pgModel.hold_duration.desc()).first()

            if data_polices is not None:
                expiry_date = date_today + datetime.timedelta(days=data_polices.hold_duration)
                item_rate = {
                    "on_hold": True,
                    "hold_duration": data_polices.hold_duration, 
                    "expiry_date": expiry_date,
                    "min_lead_time": data_polices.min_lead_time
                }
                data_rate.append(item_rate)
            else:
                item_rate = {
                    "on_hold": False,
                    "hold_duration": 0, 
                    "expiry_date": "",
                    "min_lead_time":0 
                }
                data_rate.append(item_rate)

        if len(data_rate) > 0:
            max_lead_time = max([x['min_lead_time'] for x in data_rate])
            if  (from_date - date_today.date()).days > max_lead_time:
                filter_on_hold = list(filter(lambda elem_rate: elem_rate['on_hold'] == False, data_rate))
                if len(filter_on_hold) == 0:
                    max_val = max([x['hold_duration'] for x in data_rate])
                    data = [item for item in data_rate if item['hold_duration'] == max_val]
                    if len(data) > 1:
                        data_temp = []
                        data_filter = [ data_temp.append(x) for x in data if x not in data_temp ]
                        data = data_temp

        return data