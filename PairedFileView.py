# encoding: UTF-8

import pygtk
pygtk.require('2.0')
import gtk

from PairedItem import PairedItem
from FileView import FileView
from config import conf


class PairedFileView(FileView, PairedItem):
    
    def __init__(self, flist, parent_pane):
        FileView.__init__(self, flist, parent_pane)
        PairedItem.__init__(self)
        
        self.bind_shortkey(conf['k-target-eq'], self.onTargetEqual)
        self.bind_shortkey(conf['k-target-swap'], self.onTargetSwap)
        
    def onTargetEqual(self):
        self.other.fileList().setCwd(self.fileList().getCwd())
        
    def onTargetSwap(self):
        other_state = self.getOther().getState()
        self_state = self.getState()
        self.setState(other_state)
        self.getOther().setState(self_state)
        
        self.get_toplevel().child_focus(gtk.DIR_TAB_FORWARD)
    