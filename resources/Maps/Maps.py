import googlemaps
import gmaps
#import png
import tempfile
from datetime import datetime
import requests
from flask_restful import Resource
from flask import send_file, make_response
import os
from config import base, app, api
import random
import string
from matplotlib import pyplot as plt
import json
import base64

MIME = "image/png"

def get_bulk(charsize=12):
    """ Generate a Random hash """
    hash_list = string.ascii_uppercase + string.ascii_lowercase
    code = "".join(
        random.SystemRandom().choice(hash_list) for _ in range(charsize)
    ) + str(datetime.now().strftime("%Y-%m-%d %H%M%S"))
    return code
class Maps(Resource):
    def get(self):

        img = os.path.join(
            base.app_config("TMP_PATH"),
            "{}".format("maps.png", get_bulk(charsize=7)),
        )

        api_key = "AIzaSyDcCb0E1ydxpFn8efgdO3Zh2QpWjRAvGbY"
        gmaps.configure(api_key=api_key)
        cordinates = (20.979819,20.979819)
        #f= gmaps.figure(center=cordinates, zoom_level=12)

        # with open(img, 'w+b') as temp:
        #         html_layer = open(img, 'w')
        #         html_layer.write(f.content)
        #         html_layer.close()


        url = "https://maps.googleapis.com/maps/api/staticmap?"
  
        # center defines the center of the map, 
        # equidistant from all edges of the map.  
        center = "20.979819,-86.834"
        
        # zoom defines the zoom 
        # level of the map
        zoom = 15
        
        # get method of requests module 
        # return response object 

        url2 = (url + "center=" + center + "&zoom="+
                           str(zoom) + "&size=400x400&key="+api_key+"&sensor=true&markers="+center)

                           
        r = requests.get(url + "center=" + center + "&zoom=" +
                           str(zoom) + "&size=400x400&key=" +
                           api_key+"&sensor=false&markers="+center)
        
        f= open(img, 'wb')

        #w= png.Writer(len(r.content),1, greyscale=False)

        #w.write(f,len(r.content))

        f.write(r.content)
        f.close()
        
        # with open(img, 'w+b') as temp:
        #         html_layer = open(img, 'w')
        #         html_layer.write(r.content)
        #         html_layer.close()

        #img_base64 = self.convert_base64(img)
        
        upload_buck = self.upload_bucket(self,img)
        #return make_response(img_base64)
        return upload_buck

    @staticmethod
    def convert_base64(img):
        with open(img, "rb") as img_file:
            my_string = base64.b64encode(img_file.read())

        return my_string

    @staticmethod
    def upload_bucket(self,xlsx_report):
        #Creamos la subida al bucket
            files = {'filename': open(xlsx_report,'rb')}
            #nombre del bucket: booking_reports
            #nombre de subcarpeta/booking_engine/reports
            if base.environment == "pro":
                url = "/s3upload/clever-palace-prod/booking_reports"
            else:
                url = "/s3upload/clever-palace-dev/booking_reports"
            r = requests.post(base.get_url("apiAssetsPy") + "/s3upload/booking_engine", files=files)
            
            #validamos contra la respuesta del post
            d = json.loads(r.text)

            if d["success"] == True:
                #se remueve archivo temporal
                #pre_signed_url = self.create_presigned_url('clever-palace-dev',d['data']['ETag'],3600)
                return d['data']#pre_signed_url #d['data']
            else:
                #se remueve archivo temporal
                response = {
                "success": False, 
                "status": 500, 
                "message": "Error Bucket: " + d["message"], 
                "data": {}
                }
                return response