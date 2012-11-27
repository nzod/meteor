#encoding: UTF-8

import pygtk
pygtk.require('2.0')
import gtk

from ShortkeyMixin import ShortkeyMixin
import f_ops
from config import conf


def fname_markup(fname, is_dir):
      desc = ''
      if is_dir:
         desc += 'bold'
      desc += ' 10.0'
      return '<span font_desc="%s" foreground="#333">%s</span>' % (desc, fname)
      

class FileView(gtk.TreeView, ShortkeyMixin):
   def __init__(self, flist, group):
      gtk.TreeView.__init__(self, flist)
      ShortkeyMixin.__init__(self)
      
      self.flist = flist
      self.flist.fname_markup_fun = fname_markup
      
      self.get_selection().set_mode(gtk.SELECTION_MULTIPLE)
      #self.set_rubber_banding(True)
      #self.set_enable_search(True)
      
      self.set_headers_visible(False)
      self.set_grid_lines(gtk.TREE_VIEW_GRID_LINES_NONE)
   
      fname_renderer = gtk.CellRendererText()
      fname_renderer.set_property('editable', True)
      fname_renderer.connect('edited', self.onRenameCommit)
      
      self.col_fname = gtk.TreeViewColumn('Name', fname_renderer, markup=2)
      #self.col_counter = gtk.TreeViewColumn('Count', counter_renderer, markup=2)
      
      self.col_fname.set_sizing(gtk.TREE_VIEW_COLUMN_FIXED)
      self.col_fname.set_expand(True)
      
      self.append_column(self.col_fname)
      
      gtk.rc_parse_string( """
        style "filelist-style-active"{
            GtkTreeView::odd-row-color = "#ddd"
            GtkTreeView::even-row-color = "#eee"
            GtkTreeView::allow-rules = 1
        }
        style "filelist-style-inactive"{
            GtkTreeView::odd-row-color = "#bbb"
            GtkTreeView::even-row-color = "#ccc"
            GtkTreeView::allow-rules = 1
        }
        widget "*filelist_view_active*" style "filelist-style-active"
        widget "*filelist_view_inactive*" style "filelist-style-inactive"
    """)
      self.set_name('filelist_view_inactive')
      self.set_rules_hint(True)
      
      #-- hotkeys
      k_co = conf['hotkeys']
      self.bind_shortkey(k_co['fview-nav-up'], self.onNavUp)
      self.bind_shortkey(k_co['fview-nav-home'], self.onNavHome)
      self.bind_shortkey(k_co['fview-reload'], self.onNavReload)
      self.bind_shortkey(k_co['fview-toggle-hidden'], self.onToggleHidden)
      self.bind_shortkey(k_co['file-rename'], self.onBeginRename)
      self.bind_shortkey('Return', self.onItemEnter)
      
      #-- model init
      self.flist.connect('cwd-changed', self.onCwdChanged)
      self.group = group
      
      #self.connect('row-activated', self.onRowActivated)
   
   def clear(self):
      self.flist.clear()
      
   def getFileList(self):
      return self.flist
      
   def setActive(self, active):
      self.set_name('filelist_view_%s' % ('active' if active else 'inactive'))
      
   def makeCellVisible(self, i):
      self.scroll_to_cell(i)
      # a,b = self.get_visible_range()  # always None for some reason...
      # if i<a+1 or i>b-1:
      #    self.scroll_to_cell(i)
            
   def onCwdChanged(self, srcobj, cwd):
      #self.loadFileList()
      pass
   
   def onNavUp(self):
      currname = self.flist.getCwdName()
      self.flist.setCwdUp()
      i = self.flist.findItemByFname(currname)
      self.get_selection().select_path(i)
      self.makeCellVisible(i)
      
   def onNavHome(self):
      self.flist.setCwdHome()
      self.get_selection().select_path(0)
      self.makeCellVisible(0)
      
   def onNavReload(self):
      self.flist.setCwd( self.flist.getCwd() )
   
   def onBeginRename(self):
      sel = self.get_selection()
      if sel.count_selected_rows() != 1:
         return
      (model, pathlist) = sel.get_selected_rows()
      p_i = pathlist[0]
      self.set_cursor(p_i, self.col_fname, True)
   
   def onRenameCommit(self, cell, path, new_name):
      tree_iter = self.flist.get_iter(path)
      is_dir = self.flist.get_value(tree_iter, 0)
      orig_fname = self.flist.get_value(tree_iter, 1)
      
      new_name = new_name.strip()
      if (not new_name) or (new_name==orig_fname):
         return
      if self.flist.hasFilename(new_name):
         return
      
      f_ops.rename(self.flist.getCwd(), orig_fname, new_name)
      self.flist.set_value(tree_iter, 1, new_name)
      self.flist.set_value(tree_iter, 2, self.fname_markup(new_name, is_dir))

   # def onRowActivated(self, view, path, col):
   #    model = self.get_model()
   #    p_i = path[0]
   #    m_iter = model.get_iter(p_i)
      
   #    is_dir = model.get_value(m_iter, 0)
   #    fname = model.get_value(m_iter, 1)
      
   #    if is_dir:
   #       self.flist.setCwdInto(fname)
   #       self.get_selection().select_path(0)
   #       self.makeCellVisible(0)
   #    else:
   #       f_ops.execute( self.flist.getItemFullPath(fname) )
      
   def onItemEnter(self):
      sel = self.get_selection()
      if sel.count_selected_rows() != 1:
         return
      (model, pathlist) = sel.get_selected_rows()
      p_i = pathlist[0]
      m_iter = model.get_iter(p_i)
      
      is_dir = model.get_value(m_iter, 0)
      fname = model.get_value(m_iter, 1)
      
      if is_dir:
         self.flist.setCwdInto(fname)
         self.get_selection().select_path(0)
         self.makeCellVisible(0)
      else:
         f_ops.execute( self.flist.getItemFullPath(fname) )
      
   def onToggleHidden(self):
      sel = self.get_selection()
      (model, pathlist) = sel.get_selected_rows()
      selfiles = []
      for path in pathlist:
         m_iter = model.get_iter(path)
         fname = model.get_value(m_iter, 1)
         selfiles.append(fname)
       
      self.flist.setUseHiddenFiles( not self.flist.use_hidden_files )
      
      first_sel = None
      for selfile in selfiles:
         i = self.flist.findItemByFname(selfile)
         if first_sel is None:
            first_sel = i
         sel.select_path(i)
      
      if first_sel is not None:
         self.makeCellVisible(first_sel)
