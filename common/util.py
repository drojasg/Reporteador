import json
from config import db, base

#from models.translation_message import TranslationMessage
#from common.external_credentials import ExternalCredentials
#from common.custom_log_request import CustomLogRequest
from user_agents import parse as parseUserAgent

class Util():
    device_mobile = "mobile"
    device_tablet = "tablet"
    device_desktop = "desktop"
    
    @staticmethod
    def get_default_excludes():
        return ('usuario_creacion', 'fecha_creacion', 'usuario_ultima_modificacion', 'fecha_ultima_modificacion')

    # @staticmethod
    # def t(lang_code, key, *argv):
    #     '''
    #         use to translate messages.
    #         lang_code: translate to 
    #         key: key of the message to look in the database
    #         *argv: optional attributes to replace the {} (this indicate variables)

    #         return: message translated and with variables replaced.
    #     '''
    #     lang_code = lang_code.lower()
    #     translation = TranslationMessage.query.filter(TranslationMessage.lang_code == lang_code, \
    #         TranslationMessage.key == key, TranslationMessage.estado == 1).first()
        
    #     if translation is None:
    #         return ""
        
    #     text = translation.text
    #     for var in argv:
    #         text = text.replace("{}", str(var), 1)
        
    #     return text
    
    # @staticmethod
    # def send_notification(data, tag_notification, username):
    #     """
    #         Send notification using clever frm api
    #         :param data = Data for the notification template
    #         :param tag_notification = Tag to retrieve the email template
    #         :param username = Username to save api log
    #     """
    #     external_credentials = ExternalCredentials()
    #     token = external_credentials.get_token(base.system_id)
    #     timeout = 15
    #     use_token = False            
    #     endpoint = "{}/notificaciones/notificacion/{}".format(base.get_url("clever-frm"), tag_notification)

    #     service_response = CustomLogRequest.do_request(url=endpoint, method="POST", \
    #         data=data, timeout=timeout, use_token=use_token, token=token, username=username)
        
    #     return json.loads(service_response)
    
    # @staticmethod
    # def send_notification_attachment(data, tag_notification, username, files=[]):
    #     """
    #         Send notification using clever frm api
    #         :param data = Data for the notification template
    #         :param tag_notification = Tag to retrieve the email template
    #         :param username = Username to save api log
    #         :param files = Files to attach in email
    #     """
    #     external_credentials = ExternalCredentials()
    #     token = external_credentials.get_token(base.system_id)
    #     timeout = 15
    #     use_token = False            
    #     endpoint = "{}/notificaciones/notificationAttachment/{}".format(base.get_url("clever-frm"), tag_notification)

    #     service_response = CustomLogRequest.do_request(url=endpoint, method="POST", \
    #         data=data, timeout=timeout, use_token=use_token, token=token, username=username, \
    #         content_type="", files=files)
        
    #     return json.loads(service_response)
    
    @staticmethod
    def is_mobile_request(user_agent_string):
        """
            Get true if the request device is from a mobile device
            :param user_agent_string User agent data as string
            :return boolean
        """
        data_agent = parseUserAgent(user_agent_string)

        if data_agent.is_mobile and data_agent.is_tablet:
            return True
        
        return False
    
    @classmethod
    def get_device_request(cls, user_agent_string):
        """
            Get request device throught user agent data.
            :param user_agent_string User agent data as string
            return string | desktop, mobile, tablet
        """
        data_agent = parseUserAgent(user_agent_string)

        if data_agent.is_mobile:
            return cls.device_mobile
        
        if data_agent.is_tablet:
            return cls.device_tablet
        
        return cls.device_desktop
    
    @classmethod
    def find_nested_error_message(cls, messages):
        """
            Find the first message error in Marshmallow validator messages.
            :param messages Dict with messages nested

            :return String with message error
        """
        for item, value in messages.items():
            if isinstance(value, dict):
                return cls.find_nested_error_message(value)
            else:
                return value[0]
        return ""

    @staticmethod
    def format_address_property(data):
        """
            format address in string
            :param data = Property contact data
            return: address
        """
        address = data["address"]+" "+data["zip_code"]
        if data["city"]:
            address += ", " + data["city"]
        
        if data["country"]:
            address += ", " + data["country_name"]
        
        return address
    
    @staticmethod
    def format_phone_property(data):
        """
            format phone in string
            :param data = Property contact data
            return: phone
        """
        phone = data["country"]+"-"+str(data["area"])+"-"+str(data["number"])
        if data["extension"]:
            phone += "-" + str(data["extension"])
        
        return phone
    
    @staticmethod
    def get_email_group(group_code):
        """
            Get email list by group code.
            :param group_code string Group code to identify email list
            :return Dict Email list
        """
        if not group_code:
            return
        
        email_list = []
        """
            TODO: Implement function to retrieve data
        """
        return email_list
        