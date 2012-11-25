#encoding: UTF-8


import cPickle


def save(obj, fname):
   f = open(fname, 'w')
   cPickle.dump(obj, f)
   f.close()


def load(fname):
   try:
      f = open(fname, 'r')
      obj = cPickle.load(f)
      f.close()
      return obj
   except (IOError):
      return None
