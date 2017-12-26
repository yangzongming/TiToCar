# -*- coding: utf-8 -*-

from riceball.storage import storage
from riceball.storage.xmodel import XModelObject
from riceball.storage.xmodel.engine import CachedEngine
from riceball.storage.xmodel import model_config,xfield,XModelValue

__author__ = 'leoyang'

@storage
class User(XModelObject):
    """
    用户
    """
    model_config = model_config('id',auto_creatable=True)
    model_engine = CachedEngine.mysql_object(table='user')

    id = xfield.int(None)
    nickname=xfield.unicode(u'')
    gender=xfield.int(0)

"""
CREATE TABLE `user`(
`id` int(10) unsigned NOT NULL AUTO_INCREMENT,
`nickname` varchar(50) COLLATE uft8mb4_bin DEFAULT NULL,
`gender` int(10) unsigned DEFAULT '0',
PRIMARY KEY (`id`),
UNIQUE KEY `nickname`
)ENGIN=InnoDB DEFAULT CJARSET=utf8mb4 COLLATE=utf8mb4_bin;
SHOW CREATE TABLE `user`;
"""