from datetime import datetime

from config import db, ma
from marshmallow import Schema, fields, validate


class $class_name$(db.Model):
    __tablename__ = $table_name$
    $attributes$

class $class_name$Schema(ma.Schema):
    $schema_attributes$    