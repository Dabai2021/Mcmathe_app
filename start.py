#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys

os.chdir(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from main import MathMainApp

if __name__ == '__main__':
    MathMainApp().run()