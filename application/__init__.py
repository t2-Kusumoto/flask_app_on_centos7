#!/usr/bin/env python3
# -*- coding; utf-8 -*-

from flask import Flask

app = Flask(__name__)

from application import view
