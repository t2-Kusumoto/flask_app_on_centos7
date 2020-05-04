#!/usr/bin/env python3
# -*- coding; utf-8 -*-

import os
from flask import Flask

app = Flask(__name__)

from application import view
