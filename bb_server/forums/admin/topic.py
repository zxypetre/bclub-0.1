#!/usr/bin/env python
# -*- coding: utf-8 -*-
# **************************************************************************
# Copyright © 2016 jianglin
# File Name: topic.py
# Author: jianglin
# Email: xiyang0807@gmail.com
# Created: 2016-12-17 13:01:43 (CST)
# Last Update:星期五 2017-11-10 11:06:21 (CST)
#          By:
# Description:
# **************************************************************************
from forums.extension import db
from forums.api.topic.models import Topic, Reply
from forums.api.collect.models import Collect
from .views import BaseView


class TopicView(BaseView):
    column_searchable_list = ('title', 'content', 'author.username')
    column_filters = ['created_at', 'is_good', 'is_bad', 'author.username']
    column_exclude_list = ['content']
    column_editable_list = ['title', 'is_good', 'is_bad', 'content_type']
    column_default_sort = 'created_at'
    column_formatters = dict(
        content=lambda v, c, m, p: m.content[:100] + '...',
        content_type=lambda v, c, m, p: m.get_choice_display('content_type', 'CONTENT_TYPE')
    )
    form_choices = {'content_type': Topic.CONTENT_TYPE}
    form_widget_args = {'content': {'rows': 10}}
    form_excluded_columns = ('replies', 'collects', 'followers')
    form_ajax_refs = {'tags': {'fields': ('name', ), 'page_size': 10}}


class CollectView(BaseView):
    pass


class ReplyView(BaseView):
    column_searchable_list = ['topic.title', 'content']
    column_filters = ['author.username', 'created_at']
    form_excluded_columns = ['likers']
    form_widget_args = {'content': {'rows': 10}}


def init_admin(admin):
    admin.add_view(
        TopicView(
            Topic,
            db.session,
            name='管理问题',
            endpoint='admin_topic',
            category='管理主题'))
    admin.add_view(
        CollectView(
            Collect,
            db.session,
            name='管理收藏',
            endpoint='admin_collect',
            category='管理主题'))
