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


@get('/manager')
@view('manager.html')
def manager():
    return dict()

#创建一个新的blog
@api
@post('/api/blogs')
def api_create_blog():
    name = text.tounicode(request.forms.get('name').strip())
    summary = text.tounicode(request.forms.get('summary').strip())
    content = text.tounicode(request.forms.get('content').strip())
    if text.isempty(name):
        print(type(name))
        print(name)
        raise APIValueError('name', 'name cannot be empty.')
    if text.isempty(summary):
        print(type(summary))
        print(summary)
        raise APIValueError('summary', 'summary cannot be empty.')
    if text.isempty(content):
        print(type(content))
        print(content)
        raise APIValueError('content', 'content cannot be empty.')

    cookie = request.get_cookie(_COOKIE_NAME,None,_COOKIE_KEY)
    user = parse_signed_cookie(cookie)
    blog = Blog(user_id=user.id,user_name=user.name, name=name, summary=summary, content=content)
    blog.insert()
    return blog

@get('/api/blogs')
def api_get_blogs():
    #此处要区分网页版本和客户端
    format = 'html'
    blogs, page = _get_blogs_by_page()
    print(format)
    if format=='html':
        for blog in blogs:
            blog.content = markdown2.markdown(blog.content)
    return ujson.dumps(dict(blogs=blogs,page=page))

#获取blog信息
@api
@get('/api/blogs/:blog_id')
def api_get_blog(blog_id):
    blog = Blog.get(blog_id)
    if blog:
        return blog
    raise APIResourceNotFoundError('Blog')


#创建博客
@get('/manage/blogs/create')
@view('manage_blog_edit.html')
def manage_blogs_create():
    cookie = request.get_cookie(_COOKIE_NAME,secret=_COOKIE_KEY)
    user = parse_signed_cookie(cookie)
    return dict(id=None, action='/api/blogs', redirect='/manage/blogs', user=user)

@get('/api/comments')
def api_get_comments():
    total = Comment.count_all()
    page = Page(total, _get_page_index())
    comments = Comment.find_by('order by created_at desc limit ?,?', page.offset, page.limit)
    return ujson.dumps(dict(comments=comments, page=page))

@post('/api/blogs/:blog_id/comments')
def api_create_blog_comment(blog_id):
    cookie = request.get_cookie(_COOKIE_NAME,secret=_COOKIE_KEY)
    user = parse_signed_cookie(cookie)
    if text.isempty(user.name):
        raise APIPermissionError('Need signin.')
    blog = Blog.get(blog_id)
    if blog is None:
        raise APIResourceNotFoundError('Blog')
    #content = request.input(content='').content.strip()
    content = text.tounicode(request.forms.get("content").strip())
    if text.isempty(content):
        raise APIValueError('content')
    c = Comment(blog_id=blog_id, user_id=user.id, user_name=user.name, user_image=user.image, content=content)
    c.insert()
    return ujson.dumps(dict(comment=c))

#查看博客列表
@get('/manage/blogs')
@view('manage_blog_list.html')
def manage_blogs():
    cookie = request.get_cookie(_COOKIE_NAME,secret=_COOKIE_KEY)
    user = parse_signed_cookie(cookie)
    return dict(page_index=_get_page_index(), user=user)

@get('/blog/:blog_id')
@view('blog.html')
def blog(blog_id):
    blog = Blog.get(blog_id)
    if blog is None:
        raise APIResourceNotFoundError
    blog.html_content = markdown2.markdown(blog.content)
    comments = Comment.find_by('where blog_id=? order by created_at desc limit 1000', blog_id)
    cookie = request.get_cookie(_COOKIE_NAME,secret=_COOKIE_KEY)
    user = parse_signed_cookie(cookie)
    return dict(blog=blog, comments=comments, user=user)

@get('/manage/users')
@view('manage_user_list.html')
def manage_users():
    cookie = request.get_cookie(_COOKIE_NAME,secret=_COOKIE_KEY)
    user = parse_signed_cookie(cookie)
    return dict(page_index=_get_page_index(), user=user)

@get('/api/users')
def api_get_users():
    total = User.count_all()
    page = Page(total, _get_page_index())
    users = User.find_by('order by created_at desc limit ?,?', page.offset, page.limit)
    for u in users:
        u.password = '******'
    return ujson.dumps(dict(users=users, page=page))

@get('/manage/comments')
@view('manage_comment_list.html')
def manage_comments():
    cookie = request.get_cookie(_COOKIE_NAME,secret=_COOKIE_KEY)
    user = parse_signed_cookie(cookie)
    return dict(page_index=_get_page_index(), user=user)

@api
@post('/api/comments/:comment_id/delete')
def api_delete_comment(comment_id):
    comment = Comment.get(comment_id)
    if comment is None:
        raise APIResourceNotFoundError('Comment')
    comment.delete()
    return dict(id=comment_id)


@get('/blog')
@view('blog.html')
def index():
    blogs, page = _get_blogs_by_page()
    cookie = request.get_cookie(_COOKIE_NAME,secret=_COOKIE_KEY)
    user = parse_signed_cookie(cookie)
    return dict(page=page, blogs=blogs, user=user)


def _get_blogs_by_page():
    total = Blog.count_all()
    page = Page(total, _get_page_index())
    blogs = Blog.find_by('order by created_at desc limit ?,?', page.offset, page.limit)
    return blogs, page

def _get_page_index():
    page_index = 1
    try:
        page_index = int(request.forms.get('page', '1'))
    except ValueError:
        pass
    return page_index