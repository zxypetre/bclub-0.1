#!/usr/bin/env python
# -*- coding: utf-8 -*-
# **************************************************************************
# Copyright © 2016 jianglin
# File Name: views.py
# Author: jianglin
# Email: xiyang0807@gmail.com
# Created: 2016-12-21 21:56:41 (CST)
# Last Update:星期三 2017-5-10 16:35:21 (CST)
#          By:
# Description:
# **************************************************************************
from flask import (url_for, redirect, send_from_directory, current_app,
                   request, Response)
from flask.views import MethodView
from flask_login import login_required, current_user
from flask_auth.form import form_validate
from forums.api.forms import AvatarForm
from werkzeug.utils import secure_filename
from time import time
from random import randint
from PIL import Image
import os
from .models import File
from forums.func import get_json, object_as_dict

def check_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']

class AvatarView(MethodView):
    decorators = [login_required]

    @form_validate(
        AvatarForm, error=lambda: redirect(url_for('setting.setting')), f='')
    def post(self):
        form = AvatarForm()
        user = request.user
        file = request.files[form.avatar.name]
        filename = user.username + '-' + str(int(time())) + str(
            randint(1000, 9999))
        img = Image.open(file)
        size = 120, 120
        img.thumbnail(size, Image.ANTIALIAS)
        current_app.config.setdefault('AVATAR_FOLDER', os.path.join(
            current_app.static_folder, 'avatars'))
        avatar_path = current_app.config['AVATAR_FOLDER']
        avatar = os.path.join(avatar_path, filename + '.png')
        if not os.path.exists(avatar_path):
            os.makedirs(avatar_path)
        img.save(avatar)
        #img.close()
        info = user.info
        if info.avatar:
            ef = os.path.join(avatar_path, info.avatar)
            if os.path.exists(ef):
                os.remove(ef)
        info.avatar = filename + '.png'
        info.save()
        resp = Response(img, mimetype="image/png")
        return resp


class AvatarFileView(MethodView):
    def get(self, filename):
        current_app.config.setdefault('AVATAR_FOLDER', os.path.join(
            current_app.static_folder, 'avatars'))
        avatar_path = current_app.config['AVATAR_FOLDER']
        if not os.path.exists(os.path.join(avatar_path, filename)):
            filename = filename.split('-')[0]
            return redirect(url_for('avatar', text=filename))
        return send_from_directory(avatar_path, filename)

class GetFileView(MethodView):
    def post(self):
        file_dict = request.files.to_dict()
        for filename in file_dict:
            Files = file_dict[filename]
            if Files and check_file(Files.filename):
                filename = secure_filename(Files.filename)
                n_filename = filename.rsplit('.', 1)[0]
                fix = filename.rsplit('.', 1)[1]
                newfilename = "%s%s%s%s%s%s"%(n_filename, '_', str(int(time())), str(
                        randint(1000, 9999)), '.', fix)
                file_path = current_app.config['PICTURE_FOLDER']
                file = os.path.join(file_path, newfilename)
                if not os.path.exists(file_path):
                    os.makedirs(file_path)
                files = File(
                    front_file = filename,
                    file_path = '/' + file_path + '/' + newfilename)
                files.save()
                files.file_path = '/' + file_path + '/' + newfilename
                Files.save(file)
            else:
                return get_json(0, '格式错误', {})
        return get_json(1, '上传成功', object_as_dict(files))
