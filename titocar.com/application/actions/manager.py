#!/usr/bin/env python
# -*- coding: utf-8 -*-


import functools
from bottle import get,post,request
from bottle import jinja2_view,route


view = functools.partial(jinja2_view, template_lookup=['templates'])


@get('/manager')
@view('manager.html')
def manager():
    return dict()