from flask import Flask, request
from flask_restful import Resource
from marshmallow import ValidationError
from config import db, base
from sqlalchemy import or_, and_
from models.media import Media as MedModel
from models.media_group import MediaGroup as MedGruModel
from models.media_type import MediaType as MedTypModel
from models.media_room import MediaRoom as MedRoomModel
from models.media_property import MediaProperty as MedPropModel

class MediaFunctions():

    @staticmethod
    def GetMediaProperty(idProperty=None, MediaGroup=None, MediaType=None, only_one=True):
        
        conditions = []

        if idProperty == "":
            raise Exception("Campo idProperty Vacio Favor de Validar")

        conditions.append(MedPropModel.estado==1)

        if idProperty is not None:
            conditions.append(MedPropModel.iddef_property==idProperty)

        if MediaGroup is not None:
            conditions.append(MedGruModel.iddef_media_group==MediaGroup)

        if MediaType is not None:
            conditions.append(MedTypModel.iddef_media_type==MediaType)

        if only_one:
            data = MedModel.query.join(MedPropModel, MedPropModel.iddef_media==MedModel.iddef_media\
            ).join(MedGruModel,MedGruModel.iddef_media_group==MedModel.iddef_media_group\
            ).join(MedTypModel,MedTypModel.iddef_media_type==MedModel.iddef_media_type\
            ).filter(and_(*conditions)).order_by(MedPropModel.order).first()
            #data = MedPropModel.query.join(MedModel).join(MedGruModel).join(MedTypModel).filter(and_(*conditions)).first()
        else:
            data = MedModel.query.join(MedPropModel, MedPropModel.iddef_media==MedModel.iddef_media\
            ).join(MedGruModel,MedGruModel.iddef_media_group==MedModel.iddef_media_group\
            ).join(MedTypModel,MedTypModel.iddef_media_type==MedModel.iddef_media_type\
            ).filter(and_(*conditions)).order_by(MedPropModel.order).all()
            #data = MedPropModel.query.join(MedModel).join(MedGruModel).join(MedTypModel).filter(and_(*conditions)).all()

        if data is None:
            raise Exception("Media Property no encontrado, favor de verificar")
        
        return data

    @staticmethod
    def GetMediaRoom(idRoom=None, MediaGroup=None, MediaType=None, only_one=True):
        conditions = []

        if idRoom == "":
            raise Exception("Id de cuarto necesario para continuar, Favor de Validar")

        conditions.append(MedRoomModel.estado==1)

        if idRoom is not None:
            conditions.append(MedRoomModel.iddef_room_type_category==idRoom)

        if MediaGroup is not None:
            conditions.append(MedGruModel.iddef_media_group==MediaGroup)

        if MediaType is not None:
            conditions.append(MedTypModel.iddef_media_type==MediaType)

        if only_one:
            data = MedModel.query.join(MedRoomModel, MedRoomModel.iddef_media==MedModel.iddef_media\
            ).join(MedGruModel,MedGruModel.iddef_media_group==MedModel.iddef_media_group\
            ).join(MedTypModel,MedTypModel.iddef_media_type==MedModel.iddef_media_type\
            ).filter(and_(*conditions)).order_by(MedRoomModel.order).first()
            #data = MedPropModel.query.join(MedModel).join(MedGruModel).join(MedTypModel).filter(and_(*conditions)).first()
        else:
            data = MedModel.query.join(MedRoomModel, MedRoomModel.iddef_media==MedModel.iddef_media\
            ).join(MedGruModel,MedGruModel.iddef_media_group==MedModel.iddef_media_group\
            ).join(MedTypModel,MedTypModel.iddef_media_type==MedModel.iddef_media_type\
            ).filter(and_(*conditions)).order_by(MedRoomModel.order).all()
            #data = MedPropModel.query.join(MedModel).join(MedGruModel).join(MedTypModel).filter(and_(*conditions)).all()

        if data is None:
            raise Exception("Media Room no encontrado, favor de verificar")
        
        return data
