#encoding: UTF-8

import os
from subprocess import Popen

from config import conf


def __get_output(cmd_L):
   return Popen(cmd_L, stdout=subprocess.PIPE).communicate()[0]


def execute(full_fname):
   cmd = [conf['opener-program'], full_fname]
   Popen(cmd)

def rename(pth, fn1, fn2):
   cmd = ['mv', os.path.join(pth, fn1),
                os.path.join(pth, fn2)]
   Popen(cmd)

def newfile(pth, fname):
   cmd = ['touch', os.path.join(pth, fname)]
   Popen(cmd)
