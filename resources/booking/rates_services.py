from config import base
#from common.custom_log_request import CustomLogRequest
#from common.external_credentials import ExternalCredentials

class RatesService():
    def __init__(self):
        self.__url = base.get_url("rates")
        self.__uri__mapperattribute_search = "/mapperattribute/search/target/BOOKING_CLEVER/room_type_category/"        
        self.__url__getroominfo = "/rateroomtypecategory/getbyresortroomtype/"
        self.__external_credentials = ExternalCredentials()
    
    def getOperaRoomCode(self, property_code, room_category_clever_code, username = ""):
        '''
            Get Opera room category code

            :param property_code: Property code (Opera)
            :param room_category_clever_code: Room category code (Opera)
            
            :return dict: Room category mapping info
        '''
        response = {
            "error": True,
            "message": "",
            "data": {}
        }

        uri = self.__uri__mapperattribute_search + property_code + "/" + room_category_clever_code

        response_data = self.__do_request(uri, "GET", None, username)

        if response_data != None:
            if response_data["code"] == "404":            
                response["message"] = response_data["messages"]
            else:
                if not response_data["error"]:
                    response["error"] = False
                    response["data"] = response_data["data"][0] if response_data["data"] else {}
        
        return response
    
    def getOperaRoomInfo(self,property_code,room_type_category,username):
        '''
            Metodo para obtener informacion general de la habitacion
            property_code: ZMGR
            room_type_category: RV
        '''
        response = {
            "error": True,
            "message": "",
            "data": {}
        }

        uri = self.__url__getroominfo + property_code + "/" + room_type_category

        response_data = self.__do_request(uri, "GET", None, username)

        if response_data is not None:
            if response_data["error"]==False:
                if response_data["data"] is not None:
                    data = {
                        "beds_avail":response_data["data"]["bed"],
                        "max_adults":response_data["data"]["max_adults"],
                        "max_children":response_data["data"]["max_children"],
                        "max_ocupancy":response_data["data"]["max_occupancy"],
                        "type_ro":response_data["data"]["type_ro"],
                    }
                    response["error"]=False
                    response["data"] = data
                else:
                    data["error"]="Empty data field"
            else:
                data["error"]=response_data["message"]
        else:
            data["error"]="No response data"

        return response
    
    def __do_request(self, endpoint, method, data = None, username = None):
        '''
            Generic method to do request

            :param endpoint: endpoint API Service
            :param method: HTTP method type (post, get, put, patch, etc...)
            :param data: dictionary data to send to API Service
        '''
        
        url = "{}{}".format(self.__url, endpoint)
        token = self.__external_credentials.get_token(base.system_id)
        timeout = 15
        use_token = False
        response = CustomLogRequest.do_request(url=url, method=method, \
            data=data, timeout=timeout, use_token=use_token, token = token, username = username)
        
        return response

