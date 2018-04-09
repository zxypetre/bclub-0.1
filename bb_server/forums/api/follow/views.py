#!/usr/bin/env python
# -*- coding: utf-8 -*-
# **************************************************************************
# Copyright © 2016 jianglin
# File Name: views.py
# Author: jianglin
# Email: xiyang0807@gmail.com
# Created: 2016-12-22 21:49:05 (CST)
# Last Update:星期六 2017-4-1 19:52:14 (CST)
#          By:
# Description:
# **************************************************************************
from flask import render_template, request

from forums.api.tag.models import Tags
from forums.api.topic.models import Topic
from forums.api.collect.models import Collect
from forums.api.user.models import User
from forums.common.response import HTTPResponse
from forums.common.views import IsAuthMethodView as MethodView
from forums.api.message.models import MessageClient
from forums.func import object_as_dict, get_json


class FollowingTagsView(MethodView):
    def get(self):
        user = request.user
        page, number = self.page_info
        filter_dict = {'followers__username': user.username}
        tags = Tags.query.filter_by(**filter_dict).paginate(page, number, True)
        data = {'tags': tags}
        return render_template('follow/following_tags.html', **data)

    def post(self):
        user = request.user
        post_data = request.data
        tag_id = post_data.pop('tagId', None)
        if tag_id is not None and not User.query.filter_by(
                following_tags__id=tag_id).exists():
            tag = Tags.query.filter_by(id=tag_id).first_or_404()
            user.following_tags.append(tag)
            user.save()
        return HTTPResponse(HTTPResponse.NORMAL_STATUS).to_response()

    def delete(self):
        user = request.user
        post_data = request.data
        tag_id = post_data.pop('tagId', None)
        if tag_id is not None and User.query.filter_by(
                following_tags__id=tag_id).exists():
            tag = Tags.query.filter_by(id=tag_id).first_or_404()
            user.following_tags.remove(tag)
            user.save()
        return HTTPResponse(HTTPResponse.NORMAL_STATUS).to_response()


class FollowingTopicsView(MethodView):
    def get(self):
        user = request.user
        page, number = self.page_info
        filter_dict = {'followers__username': user.username}
        topics = Topic.query.filter_by(**filter_dict).paginate(page, number,
                                                               True)
        data = {'topics': topics}
        return render_template('follow/following_topics.html', **data)

    def post(self):
        user = request.user
        post_data = request.data
        topic_id = post_data.pop('topicId', None)
        if topic_id is not None and not User.query.filter_by(
                following_topics__id=topic_id).exists():
            topic = Topic.query.filter_by(id=topic_id).first_or_404()
            user.following_topics.append(topic)
            user.save()
            # notice
            MessageClient.follow(topic)
        return HTTPResponse(HTTPResponse.NORMAL_STATUS).to_response()

    def delete(self):
        user = request.user
        post_data = request.data
        topic_id = post_data.pop('topicId', None)
        if topic_id is not None and User.query.filter_by(
                following_topics__id=topic_id).exists():
            topic = Topic.query.filter_by(id=topic_id).first_or_404()
            user.following_topics.remove(topic)
            user.save()
        return HTTPResponse(HTTPResponse.NORMAL_STATUS).to_response()


class FollowingUsersView(MethodView):
    def get(self):
        user = request.user
        page, number = self.page_info
        users = user.following_users.paginate(page, number, True)
        data = {'users': users}
        return render_template('follow/following_users.html', **data)

    def post(self):
        user = request.user
        post_data = request.data
        user_id = post_data.pop('userId', None)
        if user_id is not None:
            f_user = User.query.filter_by(id=user_id).first_or_404()
            if not f_user.is_followed(user):
                user.following_users.append(f_user)
                user.save()
            MessageClient.follow(f_user)
        return HTTPResponse(HTTPResponse.NORMAL_STATUS).to_response()

    def delete(self):
        user = request.user
        post_data = request.data
        user_id = post_data.pop('userId', None)
        if user_id is not None:
            f_user = User.query.filter_by(id=user_id).first_or_404()
            if f_user.is_followed(user):
                user.following_users.remove(f_user)
                user.save()
        return HTTPResponse(HTTPResponse.NORMAL_STATUS).to_response()


class FollowingCollectsView(MethodView):
    def get(self):
        user = request.user
        #user = User.query.filter_by(id=1).first()
        #page, number = self.page_info
        collects = Collect.query.filter_by(author_id=user.id).all()#.paginate(page, number, True)
        topics = []
        for i in collects:
            topic = Topic.query.filter_by(id = i.topic_id).first()
            topics.append(object_as_dict(topic))
        data = {'topic':topics}
        return get_json(1, '收藏信息', data)

    def post(self):
        user = request.user
        #user = User.query.filter_by(id=1).first()
        post_data = request.data
        topic_id = post_data.pop('topic_id', None)
        collect = Collect(author_id = user.id, topic_id = topic_id)
        collect.save()
        return get_json(1, 'success', {})

    def delete(self):
        user = request.user
        post_data = request.data
        collect_id = post_data.pop('collectId', None)
        if collect_id is not None and User.query.filter_by(
                following_collects__id=collect_id).exists():
            collect = Collect.query.filter_by(id=collect_id).first_or_404()
            user.following_collects.remove(collect)
            user.save()
        return HTTPResponse(HTTPResponse.NORMAL_STATUS).to_response()
