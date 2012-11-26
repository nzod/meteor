#encoding: UTF-8

import pygtk
pygtk.require('2.0')
import gtk

from ShortkeyMixin import ShortkeyMixin
import f_ops


class FileView(gtk.TreeView, ShortkeyMixin):
   def __init__(self, flist):
      self.store = gtk.ListStore(bool, str, str)   # is_dir; original filename; markup
      
      gtk.TreeView.__init__(self, self.store)
      ShortkeyMixin.__init__(self)
      
      self.get_selection().set_mode(gtk.SELECTION_MULTIPLE)
      #self.set_rubber_banding(True)
      #self.set_enable_search(True)
      
      self.set_headers_visible(False)
      self.set_grid_lines(gtk.TREE_VIEW_GRID_LINES_NONE)
   
      fname_renderer = gtk.CellRendererText()
      #fname_renderer.set_property('editable', True)
      #fname_renderer.connect('edited', self.onFilenameEdited)
      
      self.col_fname = gtk.TreeViewColumn('Name', fname_renderer, markup=2)
      #self.col_counter = gtk.TreeViewColumn('Count', counter_renderer, markup=2)
      
      self.col_fname.set_sizing(gtk.TREE_VIEW_COLUMN_FIXED)
      self.col_fname.set_expand(True)
      
      self.append_column(self.col_fname)
      
      gtk.rc_parse_string( """
        style "filelist-style"{
            GtkTreeView::odd-row-color = "#ddd"
            GtkTreeView::even-row-color = "#eee"
            GtkTreeView::allow-rules = 1
        }
        widget "*filelist_view*" style "filelist-style"
    """)
      self.set_name("filelist_view" )
      self.set_rules_hint(True)
      
      #-- hotkeys
      self.bind_shortkey('M+Up', self.onNavUp)
      self.bind_shortkey('M+Home', self.onNavHome)
      self.bind_shortkey('C+r', self.onNavReload)
      
      #-- model init
      self.connect('row-activated', self.onRowActivated)
      
      self.flist = flist
      self.flist.connect('cwd-changed', self.onCwdChanged)
      self.fhistory = {}
   
   def clear(self):
      self.store.clear()
      
   def getFileList(self):
      return self.flist
      
   def makeCellVisible(self, i):
      self.scroll_to_cell(i)
      # a,b = self.get_visible_range()  # always None for some reason...
      # if i<a+1 or i>b-1:
      #    self.scroll_to_cell(i)
      
   def fname_markup(self, fname, is_dir):
      desc = ''
      if is_dir:
         desc += 'bold'
      desc += ' 10.0'
      return '<span font_desc="%s" foreground="#333">%s</span>' % (desc, fname)
      
   def count_markup(self, s):
      return '<span font_desc="7.0" foreground="#666">%s</span>' % s
   
   def loadFileList(self):
      self.store.clear()
      for fname, is_dir in self.flist.lst:
         self.store.append(( is_dir, fname, self.fname_markup(fname, is_dir) ))
      
   def onCwdChanged(self, srcobj, cwd):
      self.loadFileList()
   
   def onNavUp(self):
      currname = self.flist.getCwdName()
      self.flist.setCwdUp()
      try:
         i = self.flist.lst.index((currname,True))
         self.get_selection().select_path(i)
         self.makeCellVisible(i)
      except:
         pass
      
   def onNavHome(self):
      self.flist.setCwdHome()
      self.get_selection().select_path(0)
      self.makeCellVisible(0)
      
   def onNavReload(self):
      self.flist.setCwd( self.flist.getCwd() )
   
   def onFilenameEdited(self, cell, path, new_name):
      tree_iter = self.store.get_iter(path)
      is_dir = self.store.get_value(tree_iter, 0)
      orig_fname = self.store.get_value(tree_iter, 1)
      
      # new_markup = self.fname_markup(tag_id, new_name)
      # if orig_markup != new_markup:
      #    self.store.set_value(tree_iter, 1, new_markup)
      #    self.db.updateTag(tag_id, new_name)

   def onRowActivated(self, view, path, col):
      model = self.get_model()
      p_i = path[0]
      m_iter = model.get_iter(p_i)
      
      is_dir = model.get_value(m_iter, 0)
      fname = model.get_value(m_iter, 1)
      
      if is_dir:
         self.flist.setCwdInto(fname)
         self.get_selection().select_path(0)
         self.makeCellVisible(0)
      else:
         f_ops.execute( self.flist.getItemFullPath(fname) )
      