from __future__ import unicode_literals, print_function
import os.path
import os
from ds_store import DSStore, DSStoreEntry
import shutil

PSEUDO_USER_TRASH = os.path.expanduser("~/.Trash/")
TRASH_DS_FP = os.path.join(PSEUDO_USER_TRASH, ".DS_Store")
TRASH_IS_OPEN = False


def add_trash_entry(dss, fp):
    assert isinstance(dss, DSStore)
    entry_name = os.path.basename(fp)
    entry_src = os.path.dirname(fp) + "/"
    dss.insert(DSStoreEntry(entry_name, 'ptbN', 'ustr', entry_name))
    dss.insert(DSStoreEntry(entry_name, 'ptbL', 'ustr', entry_src))
    # dss[entry_name]['ptbN'] = ('ustr', entry_name)
    # dss[entry_name]['ptbL'] = ('ustr', entry_src)


class FinderTrash(object):
    def __init__(self):
        self.trash_dss = None

    def open(self):
        global TRASH_IS_OPEN
        if TRASH_IS_OPEN:
            raise Exception("The trash DS_Store is already open!")
        TRASH_IS_OPEN = True
        self.trash_dss = DSStore.open(TRASH_DS_FP, "r+")

    def _add_trash_entry(self, fp):
        entry_name = os.path.basename(fp)
        entry_src = os.path.dirname(fp) + "/"
        ptbN = DSStoreEntry(entry_name, 'ptbN', 'ustr', unicode(entry_name))
        ptbL = DSStoreEntry(entry_name, 'ptbL', 'ustr', unicode(entry_src))
        self.trash_dss.insert(ptbN)
        self.trash_dss.insert(ptbL)
        # self.trash_dss[entry_name]['ptbN'] = ('ustr', entry_name)
        # self.trash_dss[entry_name]['ptbL'] = ('ustr', entry_src)

    def move_to_trash(self, fp):
        self._add_trash_entry(fp)
        trash_dst = os.path.join(PSEUDO_USER_TRASH, os.path.basename(fp))
        shutil.move(fp, trash_dst)

    def close(self):
        if not self.trash_dss.closed():
            self.trash_dss.close()

    def __del__(self):
        self.close()

if __name__ == '__main__':
    ft = FinderTrash()
    ft.open()
    print("hey")
    ft.close()
