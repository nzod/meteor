#encoding: UTF-8

import os
import subprocess

from config import conf


def console_get_output(cmd_L):
   return subprocess.Popen(cmd_L, stdout=subprocess.PIPE).communicate()[0]


def execute(fname):
   cmd = '%s "%s"' % (conf['opener_program'], fname)
   os.system(cmd)
