import urllib
import os
import requests
import json
from config import base

class CartaUtil():
    @staticmethod
    def get_welcome_letter_file(property_code, lang_code):
        """
            Get welcome letter File from bucket.
            
            Parameters
            ----------
            property_code : str
                Property code
            lang_code : str
                Language code
            
            Returns
            -------
            file: Stream
                Stream of the file
        """
        try:
            lang_code = lang_code.upper()
            letter_name = "Welcome Letter" if lang_code == "EN" else "Carta de Bienvenida"
            file_name = "{}-{}.pdf".format(property_code, lang_code)
            pdf_report = os.path.join(base.app_config("TMP_PATH"), "{}.pdf".format(letter_name))
            url = "{}/clever/booking_engine/letters/{}".format(base.get_url("webfiles_palace"), file_name)
        
            response = urllib.request.urlopen(url)
            if not response:
                return []

            with open(pdf_report, 'w+b') as f:
                f.write(response.read())
                f.close()

            return [('FILE_PDF', open(pdf_report, 'rb'))]
        except Exception as e:
            return []

    @staticmethod
    def upload_bucket_carta(pdf_carta):
        #metodo para subir archivo al bucket
        response = {
            "success": False, 
            "status": 500, 
            "message": "Error Bucket", 
            "data": {}
        }
        #archivo
        files = {'filename': open(pdf_carta,'rb')}
        uri_upload_file = "/s3upload"

        #ruta carpeta
        if base.environment == "pro":
            url_ruta = "/clever-prod/booking_engine/letters"
        else:
            url_ruta = "/clever-qa/booking_engine"
        
        url = base.get_url("apiAssetsPy") + uri_upload_file + base.get_url("webfiles_palace") + url_ruta

        #realizamos peticion
        process = requests.post(url, files=files)
        
        #formateamos respuesta
        dataResponse = json.loads(process.text)

        if dataResponse["success"] == True:
            response = dataResponse['data']
        else:
            response["message"] = "Error Bucket: " + dataResponse["message"]
                
        return response