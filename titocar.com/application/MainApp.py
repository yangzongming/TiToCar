#!/usr/bin/env python
# -*- coding: utf-8 -*-

from bottle import get
import bottle
from application.transwarp import db
from application.config import configs
from application.transwarp.web import WSGIApplication, Jinja2TemplateEngine
import os


@get('/index')
def index():
    return "Welcome to 车天通'HomePage"

def gen_reformd_bottle():
    bottle.BaseRequest.MEMFILE_MAX = 1024 * 1024

    template_engine = Jinja2TemplateEngine(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates'))
    bottle.jinja2_template = template_engine;

    return bottle.default_app()


def load_action_module():
    """
    加载项目
    """
    action_modules = ['user','manager']
    action_base = 'application.actions'
    from importlib import import_module
    for fi_actionmodule in action_modules:
        try:
            if fi_actionmodule is None:
                import_module(action_base)
            elif fi_actionmodule.startswith('.'):
                import_module(fi_actionmodule[1:])
            else:
                import_module('%s.%s' % (action_base,fi_actionmodule))
                print(fi_actionmodule)
        except Exception, ex:
            print 'load module error'

def load_db_config():
    # 初始化数据库:
    db.create_engine(**configs.db)



print('TiToCar Prepair Start.........')

application = gen_reformd_bottle()
load_action_module()
load_db_config()

print('TiToCar Server Start Sucessfull.........\n')

