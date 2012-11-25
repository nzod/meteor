#encoding: UTF-8

import pygtk
pygtk.require('2.0')
import gtk


class FileView(gtk.TreeView):
   def __init__(self, flist):
      self.store = gtk.ListStore(bool, str, str)   # is_dir; original filename; markup
      
      gtk.TreeView.__init__(self, self.store)
      
      self.set_headers_visible(False)
      self.set_grid_lines(gtk.TREE_VIEW_GRID_LINES_NONE)
   
      fname_renderer = gtk.CellRendererText()
      fname_renderer.set_property('editable', True)
      fname_renderer.connect('edited', self.onFilenameEdited)
      
      self.col_fname = gtk.TreeViewColumn('Name', fname_renderer, markup=2)
      #self.col_counter = gtk.TreeViewColumn('Count', counter_renderer, markup=2)
      
      self.col_fname.set_sizing(gtk.TREE_VIEW_COLUMN_FIXED)
      self.col_fname.set_expand(True)
      
      self.append_column(self.col_fname)
      
      gtk.rc_parse_string( """
        style "taglist-style"{
            GtkTreeView::odd-row-color = "#ddd"
            GtkTreeView::even-row-color = "#eee"
            GtkTreeView::allow-rules = 1
        }
        widget "*taglist_view*" style "taglist-style"
    """)
      self.set_name("taglist_view" )
      self.set_rules_hint(True)
      
      
      #-- model init
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
