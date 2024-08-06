import os
from pathlib import Path


ROOT = Path(__file__).parents[1]
"""
  Absolute path of root in this project
"""


BUFSIZE = 1024 * 1024 if os.name == 'nt' else 64 * 1024
"""
  Size of buffer for read and write\n
  Windows (`nt`) perform better with 1mb (1024 * 1024) size
"""
