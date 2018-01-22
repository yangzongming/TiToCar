#!/usr/bin/env python
# -*- coding: utf-8 -*-

import time, uuid
from application.transwarp.db import next_id
from application.transwarp.orm import Model, StringField, BooleanField, FloatField, TextField,IntegerField

def next_id():
    return '%015d%s000' % (int(time.time() * 1000), uuid.uuid4().hex)

class Message(Model):
    __table__ = 'message'

    id = StringField(primary_key=True, default=next_id, ddl='varchar(50)')
    title = StringField(ddl='varchar(50)')
    content = TextField()
    type = IntegerField()
    target = StringField(ddl='varchar(100)')
    created_at = FloatField(updatable=False, default=time.time)
    is_read = BooleanField(default = False)


"""
create table message (
    `id` varchar(50) not null,
    `title` varchar(50) not null,
    `content` mediumtext not null,
    `type` real not null,
    `target` varchar(100) not null,
    `is_read` real not null,
    `create_time_value` real not null,
    key `idx_created_at` (`created_at`),
    primary key (`id`)
) engine=innodb default charset=utf8;
"""