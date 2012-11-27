#encoding: UTF-8

import pygtk
pygtk.require('2.0')
import gtk


def ctrl_down(state):
   return state & gtk.gdk.CONTROL_MASK

def alt_down(state):
   return state & gtk.gdk.MOD1_MASK


class ShortkeyMixin(object):
   def __init__(self):
      self.bindings = {  None: {},
                         'C' : {},
                         'M' : {},
                         'CM': {}  }
      
      self.connect('key-press-event', self.on_keypress)

   def bind_shortkey(self, s, func):
      mod, keyval = s.split('+')
      keyval = gtk.gdk.keyval_from_name(keyval)
      self.bindings[mod][keyval] = func

   def on_keypress(self, widget, data=None):
      mod = None
      
      if ctrl_down(data.state) and alt_down(data.state):
         mod = 'CM'
      elif ctrl_down(data.state) and data.keyval != 65513:
         mod = 'C'
      elif alt_down(data.state) and data.keyval != 65507:
         mod = 'M'
      
      if data.keyval in self.bindings[mod]:
         self.bindings[mod][data.keyval] ()
         return True
            
      return False

