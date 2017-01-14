# -*- coding: utf-8 -*-
import datetime
import pymongo

from app.db import db

def get_increment_id(_id, increment_amount=1):
    ret = db['increments'].find_one_and_update({'_id': _id},{
        '$inc': {
            'count': increment_amount,
        },
        '$set': {
            'modified_at': datetime.datetime.now(),
        }
    }, upsert=True, return_document=pymongo.ReturnDocument.AFTER)
    return ret['count']

if __name__ == '__main__':
    print get_increment_id('test')
