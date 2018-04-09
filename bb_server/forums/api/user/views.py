#!/usr/bin/env python
# -*- coding: utf-8 -*-
# **************************************************************************
# Copyright © 2016 jianglin
# File Name: views.py
# Author: jianglin
# Email: xiyang0807@gmail.com
# Created: 2016-12-15 22:08:06 (CST)
# Last Update:星期日 2017-4-2 11:51:33 (CST)
#          By:
# Description:
# **************************************************************************
from flask import redirect, render_template, request, url_for
from flask_login import current_user, login_required
from forums.api.forums.models import Board
from forums.api.tag.models import Tags
from forums.api.topic.models import Topic, Reply
from forums.api.collect.models import Collect
from forums.common.utils import gen_filter_dict, gen_order_by
from forums.common.views import BaseMethodView as MethodView
from forums.func import get_json, object_as_dict 

from .models import User


class UserListView(MethodView):
    @login_required
    def get(self):
        query_dict = request.data
        #page, number = self.page_info
        keys = ['username']
        order_by = gen_order_by(query_dict, keys)
        filter_dict = gen_filter_dict(query_dict, keys)
        users = User.query.filter_by(
            **filter_dict).order_by(*order_by).all()#.paginate(page, number, True)
        data = []
        for i in users:
            data.append(object_as_dict(i))
        return get_json(1, '所有用户', data)


class UserView(MethodView):
    def get(self, username):
        query_dict = request.data
        user = User.query.filter_by(username=username).first_or_404()
        #page, number = self.page_info
        keys = ['title']
        order_by = gen_order_by(query_dict, keys)
        filter_dict = gen_filter_dict(query_dict, keys)
        filter_dict.update(author_id=user.id)
        topics = Topic.query.filter_by(
            **filter_dict).order_by(*order_by).all()#.paginate(page, number, True)
        setting = user.setting
        user = object_as_dict(user)
        keys = ['password', 'last_login', 'register_time', 'phone', 'id', 'email', 'integral', 'user_code', 'recommender_code']
        for i in keys:
            user.pop(i)
        if user.pop('is_confirmed'):
            user['is_confirm'] = '邮箱未认证'
        if user.pop('is_superuser'):
            user['Authority'] = '管理员'
        else:
            user['Authority'] = '普通用户'
        #topic_is_allowed = False
        #if setting.topic_list == 1 or (setting.topic_list == 2 and
        #                               current_user.is_authenticated):
        #    topic_is_allowed = True
        #if current_user.is_authenticated and current_user.id == user.id:
        #    topic_is_allowed = True
        data = {
            'topics': [object_as_dict(i) for i in topics],
            'user': user
        #    'topic_is_allowed': topic_is_allowed
        }
        return get_json(1, '文章信息', data)


class UserReplyListView(MethodView):
    def get(self, username):
        query_dict = request.data
        user = User.query.filter_by(username=username).first_or_404()
        #page, number = self.page_info
        keys = ['title']
        order_by = gen_order_by(query_dict, keys)
        filter_dict = gen_filter_dict(query_dict, keys)
        filter_dict.update(author_id=user.id)
        replies = Reply.query.filter_by(
            **filter_dict).order_by(*order_by).all()#.paginate(page, number, True)
        #setting = user.setting
        #replies_is_allowed = False
        #if setting.rep_list == 1 or (current_user.is_authenticated and
        #                             setting.rep_list == 2):
        #    replies_is_allowed = True
        #if current_user.is_authenticated and current_user.id == user.id:
        #    replies_is_allowed = True
        reply = []
        for i in replies:
            reply.append(object_as_dict(i))
        data = {
            'replies': reply,
            'user': object_as_dict(user)
            #'replies_is_allowed': replies_is_allowed
        }
        return get_json(1, '回复信息', data)


class UserFollowerListView(MethodView):
    @login_required
    def get(self, username):
        user = User.query.filter_by(username=username).first_or_404()
        page, number = self.page_info
        followers = user.followers.paginate(page, number, True)
        data = {'followers': followers, 'user': user}
        return render_template('user/followers.html', **data)


class UserFollowingListView(MethodView):
    def get(self):
        return redirect(url_for('follow.topic'))


class UserCollectListView(MethodView):
    def get(self, username):
        return redirect(url_for('follow.collect'))
