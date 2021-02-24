from flask import Flask, request
import requests
from flask_restful import Resource
import os 
from datetime import datetime
from config import base
import PIL 
from PIL import Image
from config import base
import json
import io

class ImgCompress(Resource):
    def post(self):
        try:
            # se obtiene el archivo
            file = request.files["filename"]
            filename = file.filename
            script_dir =  "tmp/"
            hash = self.hash()
            filename_hash = "original_"+hash+filename
            file_path = os.path.join(script_dir, filename_hash)

            #se crea archivo binario temporal
            newFile = open(file_path, 'wb')
            newFileByteArray = bytearray(file.read())
            newFile.write(newFileByteArray)
            newFile.close()
            
            
            #se comprime la imagen
            img= Image.open(file_path)
            widthImg, heightImg = img.size

            width = 455
            scaleFactor = width / widthImg
            height = heightImg * scaleFactor

            img = img.resize((width, round(height) ),PIL.Image.ANTIALIAS)
            file_compress_path = script_dir+hash+filename 
            img.save(file_compress_path)

            
            #Cortamos con un ratio 21:9
            img= Image.open(file_compress_path)
            widthImg, heightImg = img.size

            if heightImg > 235:

                xcenter = widthImg/2
                ycenter = heightImg/2
                
                x1 = xcenter - 227.5
                y1 = ycenter - 117.5
                
                x2 = xcenter + 227.5
                y2 = ycenter + 117.5

                cropped = img.crop((x1, y1, x2, y2))
                cropped.save(file_compress_path)
            
            #si la imagen no alcanza la altura minima(432) ha hacer el recorte en vertical
            else:
                img= Image.open(file_path)
                widthImg, heightImg = img.size

                height = 235
                scaleFactor = height / heightImg
                width = widthImg * scaleFactor

                img = img.resize((round(width), height ),PIL.Image.ANTIALIAS)
                img.save(file_compress_path)

                img= Image.open(file_compress_path)
                widthImg, heightImg = img.size

                xcenter = widthImg/2
                ycenter = heightImg/2
                
                x1 = xcenter - 227.5
                y1 = ycenter - 117.5
                
                x2 = xcenter + 227.5
                y2 = ycenter + 117.5

                cropped = img.crop((x1, y1, x2, y2))
                cropped.save(file_compress_path)
            
            #se envia el archivo temporal al bucket
            files = {'filename': open(file_compress_path,'rb')}
            r = requests.post(base.get_url("apiAssetsPy") + "/s3upload/booking_engine", files=files)


            #validamos contra la respuesta del post
            d = json.loads(r.text)

            if d["success"] == True:
                #se remueve archivo temporal
                os.remove(file_path) 
                os.remove(file_compress_path) 
                return d
            else:
                #se remueve archivo temporal
                response = {
                "success": False, 
                "status": 500, 
                "message": "Error Bucket: " + d["message"], 
                "data": {}
                }

                os.remove(file_path)
                os.remove(file_compress_path) 

                return response

        except Exception as e:          
            os.remove(file_path)
            os.remove(file_compress_path) 

            response = {
                "success": False, 
                "status": 500, 
                "message": "Error API BE: " + str(e), 
                "data": {}
                }
        
        return response
        

    def hash(self):
        now = datetime.now()
        current_time = now.strftime("%Y-%d-%m-%H-%M-%S-%f")
        return (current_time)



