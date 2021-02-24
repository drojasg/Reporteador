import matplotlib.pyplot as plt
#**********************
import matplotlib.pyplot as plt
import pandas as pd
import xlwt
import os
#************************
from flask import Flask, request
from flask_restful import Resource
from pandas import ExcelWriter
from common.util import Util
from config import base, app, api
from flask import send_file
from sqlalchemy import text
import random
import string
import json
from datetime import datetime
import xlsxwriter
from config import db
import numpy as np

MIME = 'application/pdf'

class graphs(Resource):
    def post(self):
        #EjeY
        lead_time = ['7 days or less', '8-14 days', '15-21 days', '22-29 days', '30-59 days', '60 days or more']
        y_pos = np.arange(len(lead_time))
        #EjeX
        number_of_searches = ['40K', '10K', '20K', '30K', '40K', '50K', '60K', '70K', '80K', '90K', '100K']
        cantidad_usos = [10,8,6,4,2,1]

        #Se crea la grafica
        plt.barh(y_pos, cantidad_usos, align='center', alpha=0.5)

        #agregamos etiquetas

        #agregamos la etiqueta del eje Y: 
        plt.yticks(y_pos, lead_time)
        #agregamos etiqueta al eje X:
        plt.xlabel('Number of searches')

        #agregamos una etiqueta superior
        plt.title('CONVERSION RATE ON LEAD TIME OF SEARCHES')
        plt.savefig('plot.pdf')
        plt.show()