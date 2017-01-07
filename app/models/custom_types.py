# -*- coding: utf-8 -*-
import datetime
import bson.objectid
from schematics.exceptions import ConversionError
from schematics.types import BaseType, StringType, DateType, DateTimeType, BooleanType, ListType, ModelType, DecimalType

from app import error

class MongoIdType(BaseType):
    def _mock(self, context=None):
        return bson.objectid.ObjectId()

    def to_native(self, value, context=None):
        if not isinstance(value, bson.objectid.ObjectId):
            try:
                value = bson.objectid.ObjectId(str(value))
            except bson.objectid.InvalidId:
                raise error.ConversionError(self.messages['convert'])
        return value

    def to_primitive(self, value, context=None):
        return str(value)


class MongoDateType(DateType):
    def to_native(self, value, context=None):
        if isinstance(value, datetime.datetime):
            value =  value.date()
        elif isinstance(value, datetime.date):
            pass
        else:
            for fmt in self.formats:
                try:
                    value = datetime.datetime.strptime(value, fmt).date()
                    break
                except (ValueError, TypeError):
                    continue
            else:
                raise ConversionError(self.conversion_errmsg.format(value, ", ".join(self.formats)))

        if context.app_data.get('bson'):
            value = datetime.datetime.combine(value, datetime.time.min)

        return value

    def to_primitive(self, value, context=None):
        return value.strftime(self.serialized_format)

__all__ = ['MongoIdType', 'MongoDateType']
