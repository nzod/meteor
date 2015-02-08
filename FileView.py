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
   def __init__(self, flist, parent_pane):
      gtk.TreeView.__init__(self, flist)
      ShortkeyMixin.__init__(self)
      
      self.parent_pane = parent_pane
      
      self.flist = flist
      self.flist.fname_markup_fun = fname_markup
      
      self.set_headers_visible(False)
      self.set_grid_lines(gtk.TREE_VIEW_GRID_LINES_NONE)
   
      fname_renderer = gtk.CellRendererText()
      fname_renderer.set_property('editable', True)
      fname_renderer.connect('edited', self.onRenameCommit)
      mark_renderer = gtk.CellRendererText()
      
      self.col_fname = gtk.TreeViewColumn('Name', fname_renderer, markup=2)
      self.col_mark = gtk.TreeViewColumn('Xxx', mark_renderer, background=3)
      
      self.col_fname.set_sizing(gtk.TREE_VIEW_COLUMN_FIXED)
      self.col_fname.set_expand(True)
      #self.col_mark.set_sizing(gtk.TREE_VIEW_COLUMN_AUTOSIZE)
      self.col_mark.set_expand(False)
      self.col_mark.set_property('min-width', 9)
      self.col_mark.set_property('max-width', 9)
      
      self.append_column(self.col_mark)
      self.append_column(self.col_fname)
      
      gtk.rc_parse_string( """
        style "filelist-style-active"{
            GtkTreeView::odd-row-color = "#eee"
            GtkTreeView::even-row-color = "#eee"
            GtkTreeView::allow-rules = 1
        }
        style "filelist-style-inactive"{
            GtkTreeView::odd-row-color = "#ccc"
            GtkTreeView::even-row-color = "#ccc"
            GtkTreeView::allow-rules = 1
        }
        widget "*filelist_view_active*" style "filelist-style-active"
        widget "*filelist_view_inactive*" style "filelist-style-inactive"
    """)
      self.set_name('filelist_view_inactive')
      self.set_rules_hint(True)
      
      self.marked_names = {}
      
      #-- hotkeys
      self.bind_shortkey(conf['k-nav-up'], self.onNavUp)
      self.bind_shortkey(conf['k-nav-home'], self.onNavHome)
      self.bind_shortkey(conf['k-reload'], self.onNavReload)
      self.bind_shortkey(conf['k-toggle-hidden'], self.onToggleHidden)
      self.bind_shortkey(conf['k-file-rename'], self.onBeginRename)
      self.bind_shortkey('Return', self.onItemEnter)
      self.bind_shortkey(conf['k-file-delete'], self.onDoDelete)
      self.bind_shortkey(conf['k-new-file'], self.onDoNewFile)
      self.bind_shortkey(conf['k-mark'], self.onToggleMark)
      self.bind_shortkey(conf['k-mark-all'], self.onToggleMarkAll)
      self.bind_shortkey(conf['k-mark-section'], self.onMarkSection)
      self.bind_shortkey(conf['k-mark-inverse'], self.onMarkInverse)
      
      #-- model init
      self.flist.connect('cwd-changed', self.onCwdChanged)
      self.flist.connect('file-deleted', self.onFileDeleted)
      
   
   def clear(self):
      self.flist.clear()
      
   def getFileList(self):
      return self.flist
   
   def getPane(self):
      return self.parent_pane
      
   def setActive(self, active):
      self.set_name('filelist_view_%s' % ('active' if active else 'inactive'))
      
   def makeCellVisible(self, i):
      self.scroll_to_cell(i)
            
   def onCwdChanged(self, srcobj, cwd):
      self.marked_names = {}
   
   def onFileDeleted(self, srcobj, fname):
      try:
         del self.marked_names[fname]
      except KeyError:
         pass
   
   def onNavUp(self):
      currname = self.flist.getCwdName()
      self.flist.setCwdUp()
      i = self.flist.findItemByFname(currname)
      if i != -1:
         self.get_selection().select_path(i)
         self.makeCellVisible(i)
      
   def onNavHome(self):
      self.flist.setCwdHome()
      if len(self.flist) > 0:
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
         if len(self.flist) > 0:
            self.get_selection().select_path(0)
            self.makeCellVisible(0)
      else:
         f_ops.execute( self.flist.getItemFullPath(fname) )
   
   def onDoDelete(self):
      f_ops.delete( self.flist.getCwd(), self.marked_names.keys() )
   
   def onDoNewFile(self):
      self.parent_pane.showEditor()
   
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

   def onToggleMark(self):
      (model,i) = self.get_selection().get_selected()
      if i is None:
         return
      fname = model.get_value(i, 1)
      if fname in self.marked_names:
         del self.marked_names[fname]
         model.rmMark(i)
      else:
         self.marked_names[fname] = None
         model.addMark(i)
      
   def onToggleMarkAll(self):
      if len(self.flist)==len(self.marked_names):
         self.flist.rmAllMarks()
         self.marked_names = {}
      else:
         for i,row in enumerate(self.flist):
            fname = row[1]
            if fname not in self.marked_names:
               self.marked_names[fname] = None
               self.flist.addMark(self.flist.get_iter(i))

   def onMarkSection(self):
      (model,i) = self.get_selection().get_selected()
      if i is None:
         return
      #TODO

   def onMarkInverse(self):
      for i,row in enumerate(self.flist):
         fname = row[1]
         if fname in self.marked_names:
            del self.marked_names[fname]
            self.flist.rmMark(self.flist.get_iter(i))
         else:
            self.marked_names[fname] = None
            self.flist.addMark(self.flist.get_iter(i))

   def anyMarked(self):
      return bool(self.marked_names)
   
   def iterMarked(self):
      for name in self.marked_names:
         yield name
               

