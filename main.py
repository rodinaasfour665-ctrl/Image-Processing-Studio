"""
Advanced Image Processing Studio
==================================
CS303 - Image Processing Course Project
Entry point: python main.py
"""

import sys
import os

# Ensure project root is in path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from gui.app_ui import App


def main():
    app = App()
    app.mainloop()


if __name__ == "__main__":
    main()
