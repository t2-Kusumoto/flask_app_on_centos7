#!/usr/bin/env python3
# -*- coding; utf-8 -*-

from application import app
from flask import render_template
from flask import request

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/response', methods=['POST'])
def Hello():
    name = request.form['username']
    return render_template('hello.tpl', username=name)
