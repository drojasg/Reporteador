#**********************
import pandas as pd
import xlwt
import os
#************************
from flask import Flask, request
from flask_restful import Resource
from pandas import ExcelWriter
from models.price_type import PriceTypeSchema as ModelSchema, GetPriceTypeSchema as GetModelSchema, PriceType as Model
from common.util import Util


class Panda(Resource):
    def get(self, nombre_archivo):
        response = {}
        try:

            schema = ModelSchema(exclude=Util.get_default_excludes())
            data = Model.query.filter(Model.estado==1)
            schema = ModelSchema(exclude=Util.get_default_excludes(), many=True)

            dataJson = schema.dump(data)
            datos = pd.DataFrame (dataJson)

            ruta = '/var/html/' + nombre_archivo + '.xls'

            if os.path.isfile(ruta, mode='a'):
                raise Exception("El archivo ya existe, por favor ingrese un nombre de archivo diferente.")

            writer = ExcelWriter(ruta)
            datos.to_excel(writer, 'Hoja de prueba', index=False)
            writer.save()


            if os.path.isfile(ruta) is None:
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
                    "data": "se ha guardado el archivo en la ruta indicada"
                }
        except Exception as e:
            response = {
                "Code": 500,
                "Msg": str(e),
                "Error": True,
                "data": {}
            }

        
        return response