from flask import Flask, request
from flask_restful import Resource
from marshmallow import ValidationError

from config import db, base
from models.cross_out_config import CrossOutConfigSchema as ModelSchema, CrossOutConfigResSchema as SchemaRes, GetCrossOutConfigSchema as GetModelSchema, GetListCrossOutConfigSchema as GetListModelSchema , GetListSearchCrossOutConfigSchema as GetListSearchModelSchema, CrossOutConfig as Model, GetExternalCrossout as ExternalCrossout
from models.sistemas import SistemasSchema as SModelSchema, Sistemas as SModel
from models.crossout_rate_plan import CrossoutRatePlanSchema as CRPModelSchema, CrossoutRatePlan as CRPModel
from models.rateplan import RatePlanSchema as RPModelSchema, RatePlan as RPModel
from models.crossout_restrictions import CrossoutRastriction as crModel, CrossoutRestrictionSchema as crSchema
from models.restriction import Restriction as resModel, RestrictionSchema as resSchema
from common.util import Util
from sqlalchemy import or_, and_

class CrossOutConfig(Resource):
    #api-cross-out-config-get-by-id
    # @base.access_middleware
    def get(self, id):
        try:
            schema = GetModelSchema(exclude=Util.get_default_excludes())
            data = Model.query.get(id)

            resData = resModel.query.join(crModel,crModel.iddef_restriction == \
            resModel.iddef_restriction).filter(crModel.idop_crossout==id,\
            crModel.estado==1)
            
            dataDump = schema.dump(data)

            listRestrictions = []
            for dataItem in resData:
                schemaDetail = resSchema(exclude=Util.get_default_excludes())
                dataResDump = schemaDetail.dump(dataItem)
                listRestrictions.append(dataResDump)

            dataDump["restrictions"] = listRestrictions

            if data is None:
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
                    "data": dataDump
                }
        except Exception as e:
            response = {
                "Code": 500,
                "Msg": str(e),
                "Error": True,
                "data": {}
            }

        return response

    #api-cross-out-config-put
    # @base.access_middleware
    def put(self, id):
        response = {}
        try:
            json_data = request.get_json(force=True)
            schema = SchemaRes(exclude=Util.get_default_excludes())
            data = schema.load(json_data)
            model = Model.query.get(id)
            user_data = base.get_token_data()
            user_name = user_data['user']['username']

            if model is None:
                return {
                    "Code": 404,
                    "Msg": "data not found",
                    "Error": True,
                    "data": {}
                }

            model.cross_out_name = data["cross_out_name"]
            model.id_sistema = data["id_sistema"]
            model.date_start = data["date_start"]
            model.date_end = data["date_end"]
            model.percent = data["percent"]
            model.estado = data["estado"]
            model.usuario_ultima_modificacion=user_name
            db.session.commit()


            crData = crModel.query.filter(crModel.idop_crossout==id).all()
            #reData = resModel.query.all()

            if crData is not None and len(crData) > 0:

                for datos in crData:
                    datos.estado = 0
                    db.session.add(datos)                    
                db.session.commit()

                for restriction in data["restriction"]:
                    if restriction not in [x.iddef_restriction for x in crData]:
                        crInsert = crModel()
                        crInsert.idop_crossout = id
                        crInsert.iddef_restriction = restriction
                        crInsert.estado = 1
                        crInsert.usuario_creacion = user_name
                        db.session.add(crInsert)
                    else:
                        valueRes = {"data":x for x in crData if x.iddef_restriction == restriction \
                        and x.idop_crossout == id}
                        valueRes["data"].estado = 1
                        valueRes["data"].usuario_ultima_modificacion=user_name
                        db.session.add(valueRes["data"])

                db.session.commit()                

            response = {
                "Code": 200,
                "Msg": "Success",
                "Error": False,
                "data": schema.dump(model)
            }
        except ValidationError as error:
            response = {
                "Code": 500,
                "Msg": error.messages,
                "Error": True,
                "data": {}
            }
        except Exception as e:
            db.session.rollback()
            response = {
                "Code": 500,
                "Msg": str(e),
                "Error": True,
                "data": {}
            }

        return response

    #api-cross-out-config-delete
    # @base.access_middleware
    def delete(self, id):
        response = {}
        try:
            schema = ModelSchema(exclude=Util.get_default_excludes())
            model = Model.query.get(id)
            user_data = base.get_token_data()
            user_name = user_data['user']['username']

            if model is None:
                return {
                    "Code": 404,
                    "Msg": "data not found",
                    "Error": True,
                    "data": {}
                }

            model.estado = 0
            model.usuario_ultima_modificacion = user_name
            db.session.commit()

            response = {
                "Code": 200,
                "Msg": "Success",
                "Error": False,
                "data": schema.dump(model)
            }
        except ValidationError as error:
            response = {
                "Code": 500,
                "Msg": error.messages,
                "Error": True,
                "data": {}
            }
        except Exception as e:
            db.session.rollback()
            response = {
                "Code": 500,
                "Msg": str(e),
                "Error": True,
                "data": {}
            }

        return response

    #api-cross-out-config-post
    # @base.access_middleware
    def post(self):
        response = {}
        try:
            json_data = request.get_json(force=True)
            schema = SchemaRes(exclude=Util.get_default_excludes())
            data = schema.load(json_data)
            user_data = base.get_token_data()
            user_name = user_data['user']['username']
            model = Model()

            model.cross_out_name = data["cross_out_name"]
            model.id_sistema = data["id_sistema"]
            model.date_start = data["date_start"]
            model.date_end = data["date_end"]
            model.percent = data["percent"]
            model.estado = 1
            model.usuario_creacion = user_name
            db.session.add(model)
            db.session.commit()

            dataDump = schema.dump(model)

            if dataDump["idop_cross_out_config"] is not None:
                restrictionsId = []
                for restrictions in data["restriction"]:
                    crModelo = crModel()
                    crModelo.estado = 1
                    crModelo.usuario_creacion=user_name
                    crModelo.iddef_restriction = restrictions
                    crModelo.idop_crossout = dataDump["idop_cross_out_config"]
                    db.session.add(crModelo)
                    db.session.commit()
                    restrictionsId.append(restrictions)
                dataDump["restrictions"]=restrictionsId

            response = {
                "Code": 200,
                "Msg": "Success",
                "Error": False,
                "data": dataDump
            }
        except ValidationError as error:
            db.session.rollback()
            response = {
                "Code": 500,
                "Msg": error.messages,
                "Error": True,
                "data": {}
            }
        except Exception as e:
            db.session.rollback()
            response = {
                "Code": 500,
                "Msg": str(e),
                "Error": True,
                "data": {}
            }

        return response

class CrossOutConfigListSearch(Resource):
    #api-cross-out-config-get-all
    # @base.access_middleware
    def get(self):
        try:
            isAll = request.args.get("all")
            sistemId = request.args.get("sistem")

            data = Model()

            conditions = []
            conditions.append(Model.estado==1)

            if isAll is not None:
                conditions.pop()
            
            if sistemId is None:
                sistemId = 1
            
            conditions.append(Model.id_sistema==sistemId)

            data = Model.query.filter(and_(*conditions))
            
            schema = ModelSchema(exclude=Util.get_default_excludes(), many=True)

            if data is None:
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
                    "data": schema.dump(data)
                }
        except Exception as e:
            response = {
                "Code": 500,
                "Msg": str(e),
                "Error": True,
                "data": {}
            }

        return response

class GetExternalCrossout(Resource):
    def post(self):

        response = {
            "code":200,
            "msg":"Success",
            "error":False,
            "data":[]
        }

        try:

            dataRq = request.get_json(force=True)
            schema = ExternalCrossout()
            data_Rq = schema.load(dataRq)

            data_test = [{"channel_id":23,"crossout":15},{"channel_id":24,"crossout":18}]

            dump_data = schema.dump(data_test,many=True)

            response["data"]=data_test

        except ValidationError as data:
            db.session.rollback()
            response = {
                "code": 500,
                "msg": data.messages,
                "error": True,
                "data": []
            }
        except Exception as e:
            db.session.rollback()
            response = {
                "code": 500,
                "msg": str(e),
                "Error": True,
                "data": []
            }

        return response


#Pendiente revisar funcionalidad
class CrossOutConfigList(Resource):
    #api-cross-out-config-post-all
    # @base.access_middleware
    def post(self):

        response = {}

        try:
            schema = GetListModelSchema(exclude=('time_start','time_end','estado','usuario_creacion', 'fecha_creacion', 'usuario_ultima_modificacion', 'fecha_ultima_modificacion',))
            data = schema.load(request.get_json(force=True))

            iddef_property = request.json.get("iddef_property")
            id_sistema = request.json.get("id_sistema")
            idop_rateplan = request.json.get("idop_rateplan")
            date_start = request.json.get("date_start")
            date_end = request.json.get("date_end")
            #resultFilter = Model.query.join(SModel).join(CRPModel).join(RPModel).filter(Model.iddef_property == iddef_property, Model.id_sistema == id_sistema, RPModel.idop_rateplan==idop_rateplan, Model.estado==1, Model.date_start<=date_start, Model.date_end>=date_end).all()
            #resultFilter = Model.query.join(SModel).join(CRPModel).join(RPModel).filter(or_(and_(RPModel.iddef_property == iddef_property, Model.id_sistema == id_sistema, RPModel.idop_rateplan==idop_rateplan, Model.estado==1, Model.date_start<=date_start, Model.date_end>=date_end),(or_(Model.date_start.between(date_start, date_end), Model.date_end.between(date_start, date_end))))).all()
            resultFilter = Model.query.join(SModel).join(CRPModel).join(RPModel).filter(and_(RPModel.idProperty == iddef_property, \
            Model.id_sistema == id_sistema, RPModel.idop_rateplan==idop_rateplan, Model.estado==1, \
            or_(and_(Model.date_start<=date_start, Model.date_end>=date_end), \
            or_(Model.date_start.between(date_start, date_end), Model.date_end.between(date_start, date_end))))).all()
            
            if resultFilter is None:
                return {
                    "Code": 404,
                    "Msg": "data not found",
                    "Error": True,
                    "data": {}
                }
            else:
                response = {
                    "Code": 200,
                    "Msg": "Success",
                    "Error": False,
                    "data": schema.dump(resultFilter,many=True)
                }
        except ValidationError as data:
            db.session.rollback()
            response = {
                "Code": 500,
                "Msg": data.messages,
                "Error": True,
                "data": {}
            }
        except Exception as e:
            db.session.rollback()
            response = {
                "Code": 500,
                "Msg": str(e),
                "Error": True,
                "data": {}
            }
        return response