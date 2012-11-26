#encoding: UTF-8

import pygtk
pygtk.require('2.0')
import gtk


class FileView(gtk.TreeView):
   def __init__(self, flist):
      self.store = gtk.ListStore(bool, str, str)   # is_dir; original filename; markup
      
      gtk.TreeView.__init__(self, self.store)
      
      self.get_selection().set_mode(gtk.SELECTION_MULTIPLE)
      #self.set_rubber_banding(True)
      
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
      
      #-- model init
      self.connect('row-activated', self.onRowActivated)
      
      self.flist = flist
      self.flist.connect('cwd-changed', self.onCwdChanged)
   
   def clear(self):
      self.store.clear()
      
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
      for p_i in path:
         m_iter = model.get_iter(p_i)
         
         is_dir = model.get_value(m_iter, 0)
         fname = model.get_value(m_iter, 1)
         
         if is_dir:
            self.flist.setCwdInto(fname)
         else:
            pass
      