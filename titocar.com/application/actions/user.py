#!/usr/bin/env python
# -*- coding: utf-8 -*-

from bottle import get,post,request
from bottle import jinja2_view,route
from application.viewmodel.user import User, Blog, Comment
import functools


view = functools.partial(jinja2_view, template_lookup=['templates'])

@get('/login')
def login():
    # testdb()
    return "Hello World"

@get('/register')
@view('register.html')
def register():
    return dict()


@get('/home')
@jinja2_view('home.html', template_lookup=['templates'])
def home():
    return {'title': 'Hello world'}

@get('/test_users')
@view('test_users.html')
def test_users():
    users = User.find_all()
    return dict(users=users)

