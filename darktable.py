#!/usr/bin/env python3

from os import access, R_OK
from os.path import isfile
from helper import escape_file_path as ef
import sys, os

class Darktable:
    def __init__(self, path):
        self.original_path = path

    def export(self):
        escaped_file_path = self.original_path
        filename, file_extension = os.path.splitext(self.original_path)
        new_path = filename + ".jpeg"
        cmd = "darktable-cli " + ef(self.original_path) + " " +  ef(new_path)
        os.system(cmd)
        return new_path

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: darktable.py path/to/picture.NEF")
    else:
        img_path = sys.argv[1]
        d = Darktable(img_path)
        print(d.export())
