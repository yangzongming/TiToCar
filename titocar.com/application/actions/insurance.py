#!/usr/bin/env python
# -*- coding: utf-8 -*-

from bottle import get,post,request
from bottle import jinja2_view
from application.apis import api, Page, APIValueError, APIPermissionError, APIResourceNotFoundError
from application.viewmodel.user import User, Blog, Comment
from application.tools import text
import functools
from application.transwarp import markdown2
import ujson
from application.actions import _COOKIE_NAME,_COOKIE_KEY,parse_signed_cookie

view = functools.partial(jinja2_view, template_lookup=['templates'])


@get('/insurance')
@view('insurance.html')
def insurance():
    return dict()