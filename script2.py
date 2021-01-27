import sys
import hashlib
import json
import os
import re
import subprocess
from datetime import datetime
from optparse import OptionParser
from os.path import dirname, exists, join, realpath, relpath, splitext


import mistletoe
import requests
from mistletoe.ast_renderer import ASTRenderer
from unquietcode.tools.martek import LatexRenderer

def main():
  md_file_path = sys.argv[1]
  tex_file_path = sys.argv[2]

  with open(md_file_path, 'r') as fin:
    data = fin.read()
  rendered = mistletoe.markdown(data, LatexRenderer)

  with open(tex_file_path, "w") as f:
    f.write(rendered)

if __name__ == '__main__':
  main()