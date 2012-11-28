#encoding: UTF-8

import os
from subprocess import Popen

from config import conf


def __get_output(cmd_L):
   return Popen(cmd_L, stdout=subprocess.PIPE).communicate()[0]


def execute(full_fn):
   cmd = [conf['opener-program'], full_fn]
   Popen(cmd)

def rename(pth, fn1, fn2):
   cmd = ['mv', os.path.join(pth, fn1),
                os.path.join(pth, fn2)]
   Popen(cmd)

def delete(pth, fns):
   cmd = ['rm', '-rf']
   cmd.extend( [os.path.join(pth,fn) for fn in fns] )
   Popen(cmd)

def move(pth, fns, t_pth):
   cmd = ['mv', '-f']
   cmd.extend( [os.path.join(pth,fn) for fn in fns] )
   cmd.append( t_pth )
   Popen(cmd)

def newfile(pth, fn):
   cmd = ['touch', os.path.join(pth, fn)]
   Popen(cmd)

def newdir(pth, fn):
   cmd = ['mkdir', os.path.join(pth, fn)]
   Popen(cmd)
