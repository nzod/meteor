#encoding: UTF-8

import pygtk
pygtk.require('2.0')
import gtk
import gtk.gdk as gdk


class ShortkeyMixin(object):
   def __init__(self):
      self.bindings = {  None: {},
                         'C' : {},
                         'M' : {},
                         'CM': {}  }
      
      self.connect('key-press-event', self.on_keypress)

   def bind_shortkey(self, s, func):
      parts = s.split('+')
      if len(parts)>1:
         mod,keyval = parts
      else:
         mod = None
         keyval = parts[0]
      keyval = gtk.gdk.keyval_from_name(keyval)
      self.bindings[mod][keyval] = func

   def on_keypress(self, widget, data=None):
      mod = None
      sta = data.state

      if sta & gdk.CONTROL_MASK and sta & gdk.MOD1_MASK:
         mod = 'CM'
      elif sta & gdk.CONTROL_MASK:
         mod = 'C'
      elif sta & gdk.MOD1_MASK:
         mod = 'M'
      
      if data.keyval in self.bindings[mod]:
         self.bindings[mod][data.keyval] ()
         return True
            
      return False

