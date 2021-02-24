from config import base
#from common.custom_log_request import CustomLogRequest

class ChargesService():
    """
        Web service to send reservation payment information to charge pending booking amount.
        Provided by Javier Paredes <jparedes@palaceresorts.com>
    """

    def __init__(self):
        self.__url = base.get_url("charges_service")
        self.__uri_dynamic_insert = "{}".format(self.__url)
    
    
    def send_booking(self, payment_data):
        """
        docstring
        """
        #settings = Settings(strict=False, xml_huge_tree=True)
        #client = Client("http://web-test19:8087/WireServiceInterface/service.asmx", settings=settings)
        
        for item in payment_data:
            request_data = {
                'cobros_regattaRequest': {
                    'Data': {
                        'referencia_regatta': item["code_reservation"],
                        'no_reserva': item["pms_confirm_number"],
                        'hotel': item["property_code"],
                        'checkin_original': item["from_date"],
                        'monto_original': item["amount"],
                        'moneda_original': item["amount_currency"],
                        'card_type': self.get_card_type(item["payment"]["card_type"]),
                        'card_num': item["payment"]["card_number"],
                        'card_first_name': item["payment"]["holder_first_name"],
                        'card_last_name': item["payment"]["holder_last_name"],
                        'card_cvc': item["payment"]["cvv"],
                        'card_exp': item["payment"]["expirity_month"] + "|" + item["payment"]["expirity_year"],
                        'checkin_actualizado': item["from_date"],                        
                        "estatus_cobro": "Pendiente",
                        "estatus": "NoCobrado",
                        "estatus_opera": "Pendiente",
                        'ent_user': item["user"],
                        'ent_date': "2020-09-25T00:00:00",
                        'ent_time': "12:00",
                        'pci': 0                        
                    },
                    'Tag': ""
                }
            }
            #response = client.service.cobros_regatta_InsertarDinamico(request_data)
            # service = client.create_service(
            #     '{http://my-target-namespace-here}myBinding',
            #     'http://my-endpoint.com/acceptance/'
            # )

            #service.submit('something')

            #node = client.service.Method(_soapheaders=[header_value])
            # node = client.service.cobros_regatta_InsertarDinamico(request_data)

            #print(request_data)
            #print(node)
        
    @staticmethod
    def get_card_type(card_code):
        """
            Return card type to charges web service.
            param: card_code String Card code of Booking Engine (exists in payment_card_type table)
        """
        if card_code == "amex":
            return "AX"
        if card_code == "visa":
            return "VI"
        if card_code == "mastercard":
            return "MC"
        
        return ""