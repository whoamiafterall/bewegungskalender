import os, os.path
import errno

# inspired and adapted from https://stackoverflow.com/questions/23793987/write-a-file-to-a-directory-that-doesnt-exist

def make_dir(path):
    try:
        os.makedirs(path)
    except OSError as exc:
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else: raise

def safe_open_write(path):
    make_dir(os.path.dirname(path))
    return open(path, "w")


