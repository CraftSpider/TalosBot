
import logging
import sys

DEBUG = logging.DEBUG
INFO = logging.INFO
WARN = logging.WARN

talos = logging.getLogger("talos")
talos.addHandler(logging.StreamHandler(sys.stdout))
talos.setLevel(logging.INFO)
mainlog = talos.getChild("main")
keylog = talos.getChild("keygen")
resplog = talos.getChild("responses")


def setLevel(level):
    talos.setLevel(level)
