#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import traceback

os.chdir(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from main import MathMainApp
    print("Import successful")
    
    app = MathMainApp()
    print("App created")
    
    print("Starting app run...")
    app.run()
    print("App run completed")
    
except Exception as e:
    print(f"Error: {e}")
    traceback.print_exc()