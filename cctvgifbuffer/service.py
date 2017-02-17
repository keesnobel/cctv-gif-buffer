#!/usr/bin/env python
# Nat Morris (c) 2017

import collections
import copy
import imageio
import logging
import requests
import threading
import time
import io

from cctvgifbuffer import version
from requests.auth import HTTPBasicAuth

LOG = logging.getLogger(__name__)


def camworker(name, config, queue, lock):
    while True:
        with lock:
            respargs = {}
            if "auth" in config:
                if config["auth"] == "basic":
                    respargs["auth"] = HTTPBasicAuth(config["username"], config["password"])
            resp = requests.get(config["url"], **respargs)
            if resp.status_code == 200:
                queue.append(imageio.imread(io.BytesIO(resp.content), format='jpg'))
            if len(queue) > 5:
                queue.popleft()
        time.sleep(2)


class Service(object):

    cameras = None

    def __init__(self, config):
        LOG.info("Initializing service v%s", version())
        self.cameras = {}
        for name, cameracfg in config["cameras"].iteritems():
            self.cameras[name] = {"config": cameracfg }
        LOG.info("%d cameras: %s", len(self.cameras), ', '.join(self.cameras.keys()))
        # setup each camera with its own lock and thread
        for name, camera in self.cameras.iteritems():
            LOG.debug("%s: %s", name, camera)
            camera["buffer"] = collections.deque()
            camera["lock"] = threading.Lock()
            camera["thread"] = threading.Thread(target=camworker, args=(name, camera["config"], camera["buffer"], camera["lock"]))


    def start(self):
        LOG.info("Starting camera threads")
        # start each camera
        for name, camera in self.cameras.iteritems():
            camera["thread"].start()


        while True:
#            with lock1:
#                x = copy.copy(d)
#            print "writing animation"
#               imageio.mimsave("test.gif", x, 'GIF', duration=2)
            time.sleep(10)