# encoding: UTF-8

import re
import os
import Queue

import pygtk
pygtk.require('2.0')
import gtk
import gobject

import pyinotify


gobject.threads_init()


def natural_sort(l):
    convert = lambda text: int(text) if text.isdigit() else text.lower()
    alphanum_key = lambda key: [convert(c) for c in re.split('([0-9]+)', key)]
    return sorted(l, key=alphanum_key)


class FileList(gtk.ListStore):
    MARK_COLOR = '#bebebe'
    MARK_SEL_COLOR = '#DA8B21'

    def __init__(self):
        gtk.ListStore.__init__(self, bool, str, str, str)
        # is_dir, fname, fname_markup, marktxt

        self.valid = False
        self.use_hidden_files = False
        self.cwd = ''

        self.lst_dirs = []
        self.lst_files = []
        self.marked_names = {}

        self.name_markup_fun = None  # assigned later by owner list

        self.watch_mgr = pyinotify.WatchManager()
        evt_handler = FsEvtHandler()
        evt_handler.flist_inst = self
        self.watch_notifier = pyinotify.ThreadedNotifier(
            self.watch_mgr, evt_handler)
        self.watch_dd = None
        self.watch_notifier.start()

        self.mod_que = Queue.Queue()
        self.mod_funs = {
            '+': self.mod_AddFile,
            '-': self.mod_DeleteFile
        }
        self.mod_q_timer = None

    def isValid(self):
        return self.valid

    def teardown(self):
        self.watch_notifier.stop()

    def getCwd(self):
        return self.cwd

    def getCwdName(self):
        return os.path.split(self.cwd)[1]

    def hasFilename(self, fname):
        return (fname in os.listdir(self.cwd))

    def findItemByFname(self, fname):
        for i, row in enumerate(self):
            if row[1] == fname:
                return i
        return -1

    def addMark(self, i):
        self.set(i, 3, FileList.MARK_SEL_COLOR)

    def rmMark(self, i):
        self.set(i, 3, FileList.MARK_COLOR)

    def rmAllMarks(self):
        for i in xrange(len(self)):
            self.rmMark(self.get_iter(i))

    def __f_filter(self, target_path, fn, is_dir):
        # reads:  self.cwd, self.use_hidden_files
        if fn.startswith('.') and (not self.use_hidden_files):
            return False
        val = os.path.isdir(os.path.join(target_path, fn))
        return (val if is_dir else (not val))

    def loadCwdList(self, new_path=None):
        target_path = (new_path if new_path else self.cwd)
        try:
            lst = os.listdir(target_path)
        except OSError:
            return False
            
        self.lst_dirs = natural_sort(
            [fn for fn in lst if self.__f_filter(target_path, fn, True)])
        self.lst_dirs.insert(0, '..')
        self.lst_files = natural_sort(
            [fn for fn in lst if self.__f_filter(target_path, fn, False)])

        self.clear()
        for fname in self.lst_dirs:
            self.append(
                (True, fname, self.fname_markup_fun(fname, True), FileList.MARK_COLOR))
        for fname in self.lst_files:
            self.append(
                (False, fname, self.fname_markup_fun(fname, False), FileList.MARK_COLOR))
            
        return True

    def getItemFullPath(self, fn):
        if not self.isValid():
            raise Exception('calling itemFullPath with no cwd')
        return os.path.join(self.cwd, fn)

    def setUseHiddenFiles(self, val):
        self.use_hidden_files = val
        self.loadCwdList()
        self.emit('cwd-changed', self.cwd)

    def setCwd(self, pth, follow_watch=True):
        if not os.path.isdir(pth):
            print('FileList: not a directory: ' + pth)
            return False
        cwd = (pth.rstrip('/') if len(pth) > 1 else pth)
        if self.loadCwdList(cwd):
            if cwd != self.cwd and follow_watch:
                self.moveWatch(cwd)
            self.cwd = cwd #TODO: make this a property
            self.valid = True
            self.emit('cwd-changed', self.cwd)
        else:
            print 'Could not acccess', pth
        return self.valid

    def setCwdUp(self):
        prev_selname = self.getCwdName()
        if self.setCwd(os.path.split(self.cwd)[0]):
            self.emit('cwd-up', prev_selname)
            return True

    def setCwdInto(self, dirname):
        return (self.setCwdUp() if dirname == '..' else \
                self.setCwd(self.getItemFullPath(dirname)))

    def setCwdHome(self):
        return self.setCwd(os.path.expanduser('~'))

    def onCwdGone(self):
        cwd = self.cwd
        while True:
            cwd = os.path.split(cwd)[0]
            cwd = (cwd.rstrip('/') if len(cwd) > 1 else cwd)
            if self.setCwd(cwd, False):
                self.moveWatch(cwd)
                break

    def beginWatch(self, pth):
        self.watch_dd = self.watch_mgr.add_watch(pth,
                             pyinotify.IN_DELETE | pyinotify.IN_CREATE |
                             pyinotify.IN_MOVED_FROM | pyinotify.IN_MOVED_TO |
                             pyinotify.IN_DELETE_SELF | pyinotify.IN_MOVE_SELF,
                             rec=False)
        self.mod_q_timer = gobject.timeout_add_seconds(2, self.eatModQueue)

    def endWatch(self):
        if self.watch_dd is not None:
            self.watch_mgr.rm_watch(self.watch_dd.values())
            self.watch_dd = None
            gobject.source_remove(self.mod_q_timer)
            self.eatModQueue()
            
    def moveWatch(self, pth):
        self.endWatch()
        self.beginWatch(pth)

    def eatModQueue(self, widget=None, data=None):
        while True:
            try:
                item = self.mod_que.get(False)
                self.execMod(item)
            except Queue.Empty:
                return True

    def onFileCreated(self, pth):
        try:
            self.mod_que.put(('+', pth), False)
        except Queue.Full:
            print 'mod queue is full!'

    def onFileDeleted(self, pth):
        try:
            self.mod_que.put(('-', pth), False)
        except Queue.Full:
            print 'mod queue is full!'

    def execMod(self, item):
        cmd, pth = item
        self.mod_funs[cmd](pth)

    def mod_AddFile(self, pth):
        _, fname = os.path.split(pth)
        if fname.startswith('.') and (not self.use_hidden_files):
            return
        is_dir = os.path.isdir(pth)
        if is_dir:
            self.lst_dirs.append(fname)
            self.lst_dirs = natural_sort(self.lst_dirs)
            i = self.lst_dirs.index(fname)
        else:
            self.lst_files.append(fname)
            self.lst_files = natural_sort(self.lst_files)
            i = len(self.lst_dirs) + self.lst_files.index(fname)
        self.insert(
            i, (is_dir, fname, self.fname_markup_fun(fname, is_dir), FileList.MARK_COLOR))
        self.emit('file-created', fname)

    def mod_DeleteFile(self, pth):
        _, fname = os.path.split(pth)
        i = self.findItemByFname(fname)
        if i != -1:
            self.remove(self.get_iter(i))
            try:
                self.lst_dirs.remove(fname)
                self.lst_files.remove(fname)
            except:
                pass
            self.emit('file-deleted', fname)


gobject.type_register(FileList)
gobject.signal_new('cwd-changed', FileList, gobject.SIGNAL_RUN_FIRST,
                   gobject.TYPE_NONE, (gobject.TYPE_STRING,))
gobject.signal_new('cwd-up', FileList, gobject.SIGNAL_RUN_FIRST,
                   gobject.TYPE_NONE, (gobject.TYPE_STRING,))
gobject.signal_new('file-created', FileList, gobject.SIGNAL_RUN_FIRST,
                   gobject.TYPE_NONE, (gobject.TYPE_STRING,))
gobject.signal_new('file-deleted', FileList, gobject.SIGNAL_RUN_FIRST,
                   gobject.TYPE_NONE, (gobject.TYPE_STRING,))


class FsEvtHandler(pyinotify.ProcessEvent):

    def process_IN_CREATE(self, evt):
        self.flist_inst.onFileCreated(evt.pathname)

    def process_IN_MOVED_TO(self, evt):
        self.flist_inst.onFileCreated(evt.pathname)

    def process_IN_DELETE(self, evt):
        self.flist_inst.onFileDeleted(evt.pathname)

    def process_IN_MOVED_FROM(self, evt):
        self.flist_inst.onFileDeleted(evt.pathname)

    def process_IN_DELETE_SELF(self, evt):
        self.flist_inst.onCwdGone()

    def process_IN_MOVE_SELF(self, evt):
        self.flist_inst.onCwdGone()
