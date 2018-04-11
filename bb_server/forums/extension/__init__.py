#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ********************************************************************************
# Copyright © 2018 jianglin
# File Name: __init__.py
# Author: jianglin
# Email: xiyang0807@gmail.com
# Created: 2018-02-11 14:52:12 (CST)
# Last Update: 星期日 2018-02-11 15:31:19 (CST)
#          By:
# Description:
# ********************************************************************************
from flask import request, current_app
from flask_wtf.csrf import CSRFProtect
from flask_auth.models import db
from flask_auth.redis import Redis
from flask_auth.mail import Mail
from flask_principal import Principal
from flask_msearch import Search
from flask_caching import Cache
from . import babel, login, maple

db = db
#csrf = CSRFProtect()
redis_data = Redis()
cache = Cache()
mail = Mail()
principal = Principal()
search = Search(db=db)


class AvatarCache(object):
    def __init__(self, app=None):
        if app is not None:
            self.app = app
            self.init_app(self.app)
        else:
            self.app = None

    def init_app(self, app):
        #avatar = app.config.get('AVATAR_URL', 'avatar')
        app.add_url_rule('/api/<text>/avatar', 'avatar', self.avatar)

    def avatar(self, text, width=128):
        from flask import abort, make_response
        from flask_avatar.avatar import GenAvatar
        width_range = current_app.config.get('AVATAR_RANGE', [0, 512])
        if width < width_range[0] or width > width_range[1]:
            abort(404)
        stream = GenAvatar.generate(width, text, filetype="PNG")
        buf_value = stream.getvalue()
        response = make_response(buf_value)
        response.headers['Content-Type'] = 'image/png'
        return response


avatar = AvatarCache()


def init_app(app):
    db.init_app(app)
    avatar.init_app(app)
    cache.init_app(app)
    #csrf.init_app(app)
    principal.init_app(app)
    redis_data.init_app(app)
    mail.init_app(app)
    search.init_app(app)

    babel.init_app(app)
    login.init_app(app)
    maple.init_app(app)
