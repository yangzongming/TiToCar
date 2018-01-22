# -*- coding: utf-8 -*-


from bottle import get,post,request,response
from application.apis import api, Page, APIError, APIValueError, APIPermissionError, APIResourceNotFoundError
import os, re, time, base64, hashlib, logging
from application.viewmodel.user import User, Blog, Comment
from application.config import configs


_COOKIE_NAME = 'titocarsession'
_COOKIE_KEY = 'AwEsOmE'

def check_admin(next):
    def wrappter(*args,**kw):
        user = request.user
        if user and user.admin:
            next(args,kw)
        else:
            raise APIPermissionError('No permission.')
    return wrappter()


def parse_signed_cookie(cookie_str):
    try:
        L = cookie_str.split('-')
        if len(L) != 3:
            return None
        id, expires, md5 = L
        if int(expires) < time.time():
            return None
        user = User.get(id)
        if user is None:
            return None
        if md5 != hashlib.md5('%s-%s-%s-%s' % (id, user.password, expires, _COOKIE_KEY)).hexdigest():
            return None
        return user
    except:
        return None