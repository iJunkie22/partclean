from __future__ import unicode_literals, print_function
import os.path
import os
import time
from collections import namedtuple
import glob
import trashupdate

STAT_FIELDS = ('st_mode', 'st_ino', 'st_dev', 'st_nlink', 'st_uid',
               'st_gid', 'st_size', 'st_atime', 'st_mtime', 'st_ctime')

PSEUDO_USER_TRASH = os.path.expanduser("~/.Trash/")

synth_stat = namedtuple('synth_stat', STAT_FIELDS)


trashcan = trashupdate.FinderTrash()


class SynthStat(object):
    def __init__(self):
        self.st_mode = self.st_ino = self.st_dev = self.st_nlink = self.st_uid = 0o0
        self.st_gid = self.st_size = self.st_atime = self.st_mtime = self.st_ctime = 0o0

    @classmethod
    def clone_stat(cls, stat1):
        ss1 = cls()
        ss1.st_mode = stat1.st_mode
        ss1.st_ino = stat1.st_ino
        ss1.st_dev = stat1.st_dev
        ss1.st_nlink = stat1.st_nlink
        ss1.st_uid = stat1.st_uid
        ss1.st_gid = stat1.st_gid
        ss1.st_size = stat1.st_size
        ss1.st_atime = stat1.st_atime
        ss1.st_mtime = stat1.st_mtime
        ss1.st_ctime = stat1.st_ctime
        return ss1

    def frozen(self):
        return synth_stat(self.st_mode, self.st_ino,self.st_dev, self.st_nlink, self.st_uid,
                          self.st_gid, self.st_size, self.st_atime, self.st_mtime, self.st_ctime)

    def __iter__(self):
        return iter(self.frozen())

    def __sub__(self, other):
        delt = synth_stat(*[x - y for x, y in zip(self, other)])
        syn3 = SynthStat.clone_stat(delt)
        return syn3


class StatLogDelta(object):
    def __init__(self, statlog1, statlog2):
        self.log1 = statlog1
        self.log2 = statlog2

    @property
    def log_time_delta(self):
        return self.log1.log_time - self.log2.log_time

    @property
    def log_stat_delta(self):
        syn1 = SynthStat.clone_stat(self.log1.log_stat)
        syn2 = SynthStat.clone_stat(self.log2.log_stat)
        return syn1 - syn2


class StatLogEntry(object):
    def __init__(self, fp):
        self.log_time, self.log_stat = time.time(), os.stat(fp)

    @property
    def size(self):
        return self.log_stat.st_size

    @property
    def atime(self):
        return self.log_stat.st_atime

    @property
    def mtime(self):
        return self.log_stat.st_mtime

    @property
    def ctime(self):
        return self.log_stat.st_ctime

    def __sub__(self, other):
        assert isinstance(other, StatLogEntry)
        return StatLogDelta(self, other)


class PartFile(object):
    def __init__(self, fp):
        self.fp = fp
        self.samples = []
        self.take_sample()

    def take_sample(self):
        self.samples.append(StatLogEntry(self.fp))

    def eval_samples(self, verbose=True):
        try:
            assert len(self.samples) > 1, "Need more than one sample for a diff!"
            sample_diff = self.samples[-1] - self.samples[0]
            assert isinstance(sample_diff, StatLogDelta)
            tstamp_diff = sample_diff.log_time_delta
            stat_diff = sample_diff.log_stat_delta
            if verbose:
                stat_diff_str = "\n".join(["{}: {}".format(k, v) for k, v in zip(STAT_FIELDS, stat_diff)])
                print("File: {}\nTSDelta: {}\n{}\n\n".format(self.fp, tstamp_diff, stat_diff_str))
            return tstamp_diff, stat_diff
        except AssertionError:
            return -1, self.samples[0] - self.samples[0]

    def remove(self):
        #global trashcan
        print("*" * 20, "Trashing", self.fp)
        dst = os.path.join(PSEUDO_USER_TRASH, os.path.basename(self.fp))
        # shutil.move(self.fp, dst)
        trashcan.move_to_trash(self.fp)

    @property
    def active(self):
        t, s = self.eval_samples(False)
        return t < 1 or s.st_size > 0


def prep_trash():
    if not os.path.isdir(PSEUDO_USER_TRASH):
        os.mkdir(PSEUDO_USER_TRASH)

    trashcan.open()


def clean_partfiles():
    part_fps = glob.glob(os.path.expanduser("~/Downloads/") + "*.part")
    part_files = [PartFile(pfp) for pfp in part_fps]

    for x in xrange(10):
        time.sleep(2)
        for pf in part_files:
            pf.take_sample()
            if not pf.active:
                pf.remove()
                part_files.remove(pf)

if __name__ == '__main__':
    prep_trash()
    clean_partfiles()
    trashcan.close()
