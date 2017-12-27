#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os, re, time, base64, hashlib, logging

from bottle import get,post,request,response
from bottle import jinja2_view,route
from application.viewmodel.user import User, Blog, Comment
import functools
from application.apis import api, Page, APIError, APIValueError, APIPermissionError, APIResourceNotFoundError
from application.config import configs

view = functools.partial(jinja2_view, template_lookup=['templates'])


_RE_EMAIL = re.compile(r'^[a-z0-9\.\-\_]+\@[a-z0-9\-\_]+(\.[a-z0-9\-\_]+){1,4}$')
_RE_MD5 = re.compile(r'^[0-9a-f]{32}$')

_COOKIE_NAME = 'titocarsession'
_COOKIE_KEY = configs.session.secret

@get('/signin')
@view('signin.html')
def signin():
    return dict()

@api
@post('/api/dosignin')
def dosignin():
    email = request.forms.get('email').strip().lower()
    password = request.forms.get('password')
    remember = request.forms.get('remember')
    user = User.find_first('where email=?', email)
    if user is None:
        raise APIError('auth:failed', 'email', 'Invalid email.')
    elif user.password != password:
        raise APIError('auth:failed', 'password', 'Invalid password.')
    # make session cookie:
    max_age = 604800 if remember=='true' else None
    cookie = make_signed_cookie(user.id, user.password, max_age)
    response.set_cookie(_COOKIE_NAME, cookie, max_age=max_age)
    user.password = '******'
    return user

@get('/register')
@view('register.html')
def register():
    return dict()

@api
@post('/api/users')
def register_user():
    name = request.forms.get('name')
    email = request.forms.get('email').strip().lower()
    password = request.forms.get('password')
    if not name:
        raise APIValueError('name')
    if not email or not _RE_EMAIL.match(email):
        raise APIValueError('email')
    if not password or not _RE_MD5.match(password):
        raise APIValueError('password')
    user = User.find_first('where email=?', email)
    if user:
        raise APIError('register:failed', 'email', 'Email is already in use.')
    user = User(name=name, email=email, password=password, image='http://www.gravatar.com/avatar/%s?d=mm&s=120' % hashlib.md5(email).hexdigest())
    user.insert()
    # make session cookie:
    cookie = make_signed_cookie(user.id, user.password, None)
    response.set_cookie(_COOKIE_NAME, cookie)
    return user

def make_signed_cookie(id, password, max_age):
    # build cookie string by: id-expires-md5
    expires = str(int(time.time() + (max_age or 86400)))
    L = [id, expires, hashlib.md5('%s-%s-%s-%s' % (id, password, expires, _COOKIE_KEY)).hexdigest()]
    return '-'.join(L)

@get('/')
@jinja2_view('home.html', template_lookup=['templates'])
def home():
    return {'title': 'Hello world'}

@get('/test_users')
@view('test_users.html')
def test_users():
    users = User.find_all()
    return dict(users=users)

