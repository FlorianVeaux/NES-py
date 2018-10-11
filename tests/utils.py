import os
import cProfile

def abs_path(path):
    _dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(_dir, path)

class Profiler:
    def __init__(self, filename):
        self.filename = filename
    def __enter__(self):
        self.pr = cProfile.Profile()
        self.pr.enable()
        return self.filename

    def __exit__(self, *args):
        self.pr.disable()
        self.pr.dump_stats(abs_path(self.filename))

