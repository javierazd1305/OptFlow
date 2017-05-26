import cv2
import numpy as np
import time
from shapely.geometry import Point
from read import *


def euclideanDistance1(x, y):
    dist = ((x.x - y.x)**2 + (x.y - y.y)**2)**(0.5)
    return dist


inList, outList, inDraw, outDraw, entradas, centerPoints,  streetsIn, segmentsIn, streetsOut, segmentsOut = extract_point()


class IterRegistry(type):
    def __iter__(cls):
        return iter(cls.registry)


class clustering:
    next_id = 0
    __metaclass__ = IterRegistry
    registry = []

    def __init__(self, cluster, time):
        self.ident = clustering.next_id
        self.x = cluster.x
        self.y = cluster.y
        self.registry.append(self)
        self.time = time
        self.ellapseTime = 0

    def update(self, x, y, time):
        self.x = x
        self.y = y
        self.time = time

    def updateTime(self, time):
        self.ellapseTime = time - self.time

    @classmethod
    def isNear(cls, cluster, threshold):
        minDist = 10000
        for i in clustering.registry:
            dist = euclideanDistance1(i, cluster)
            if dist < minDist:
                minDist = dist
        if minDist < threshold:
            return False
        else:
            # print minDist
            return True

    @classmethod
    def updateAllTime(cls, time):
        for i in clustering.registry:
            i.ellapseTime = time - i.time

    @classmethod
    def tracking(cls, clusters_new, threshold):
        for index_1, i in enumerate(clustering.registry):
            minDist = 100000
            index = None
            for index_2, j in enumerate(clusters_new.registry):
                dist = euclideanDistance1(i, j)
                if dist < minDist:
                    minDist = dist
                    index = index_2
            if index != None:
                if minDist < threshold:
                    i.update(
                        clusters_new.registry[index].x, clusters_new.registry[index].y, time.time())
                    clusters_new.registry.pop(index)
                else:
                    pass
                    # print minDist
                    #clustering(clusters_new.registry[index], time.time())

    @classmethod
    def draw(cls, image):
        for i in clustering.registry:
            cv2.circle(image, (int(i.x), int(i.y)), 6, (0, 255, 255), -1)
            cv2.putText(image, "time: {}".format(i.ellapseTime), (10, 20),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
        #cont = clustering.count()
        # print cont

    @classmethod
    def pruneCluster(cls):
        for index, i in enumerate(clustering.registry):
            if i.ellapseTime > 4:
                clustering.registry.pop(index)

    @classmethod
    def count(cls):
        cont = 0
        for i in clustering.registry:
            cont += 1
        return cont

    @classmethod
    def detectZone(cls):
        for i in clustering.registry:
            loc = Point(i.x, i.y)
            for index, zona in enumerate(inList):
                if (zona[2].contains(loc)):
                    print loc
            for index, zona in enumerate(outList):
                if (zona[2].contains(loc)):
                    print loc
