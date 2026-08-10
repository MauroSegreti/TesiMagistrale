"""
Duplica tutto quello che va a schermo anche su file, cosi' le tabelle
stampate a console restano insieme ai plot invece di perdersi nel terminale.

Uso:
    from logtee import Tee
    with Tee("images/log_analisi.txt"):
        ...
"""

import os
import sys
import datetime


class _Fork:
    def __init__(self, *streams):
        self.streams = streams

    def write(self, data):
        for s in self.streams:
            s.write(data)

    def flush(self):
        for s in self.streams:
            s.flush()


class Tee:
    def __init__(self, path):
        self.path = path
        self._f = None
        self._stdout = None

    def __enter__(self):
        d = os.path.dirname(self.path)
        if d:
            os.makedirs(d, exist_ok=True)
        self._f = open(self.path, "w")
        stamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self._f.write(f"# generato il {stamp}\n")
        self._f.write(f"# comando: {' '.join(sys.argv)}\n\n")
        self._stdout = sys.stdout
        sys.stdout = _Fork(self._stdout, self._f)
        return self

    def __exit__(self, *exc):
        sys.stdout = self._stdout
        if self._f:
            self._f.close()
        print(f"[INFO] Log salvato in {self.path}")
        return False
