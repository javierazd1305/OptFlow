#!/usr/bin/env python
# -*- coding: utf-8 -*-
import cv2
import numpy as np
from math import atan2, degrees, pi, sin, cos, radians
from read import *
from cluster import *
from shapely.geometry import Point

inList, outList, inDraw, outDraw, entradas, centerPoints,  streetsIn, segmentsIn, streetsOut, segmentsOut = extract_point()


def drawAreas(image):
    for i in inDraw:
        cv2.polylines(image, np.int32([i[2]]), 1, (0, 255, 0))

    for i in outDraw:
        cv2.polylines(image, np.int32([i[2]]), 1, (0, 0, 255))

    for i in centerPoints:
        cv2.circle(image, (i[0], i[1]), 2, (255, 0, 255), 2)


def euclideanDistance(x1, x2, y1, y2):
    distance = ((x1 - x2)**2 + (y1 - y2)**2)**0.5
    return distance


def inZona(clusters):
    for i in clusters:
        loc = Point(i.x, i.y)
        for index, zona in enumerate(inList):
            if (zona[2].contains(loc)):
                print loc
        for index, zona in enumerate(outList):
            if (zona[2].contains(loc)):
                print loc


class IterRegistry(type):
    def __iter__(cls):
        return iter(cls.registry)


class ballClass:
    next_id = 0
    __metaclass__ = IterRegistry
    registry = []

    def __init__(self, x, y):
        self.ident = ballClass.next_id
        self.x = x
        self.y = y
        self.registry.append(self)

    def update(self, x, y):
        self.x = x
        self.y = y

    @classmethod
    def draw(cls, image):
        if len(ballClass.registry) > 0:
            for i in ballClass.registry:
                cv2.circle(image, (i.x, i.y), 1, (0, 255, 0), -1)

    @classmethod
    def cleaner(cls, clusters, newPoints, members):
        if clusters != None and newPoints != None:
            # print len(clusters), len(newPoints)
            listaFinal = []
            meanCluster = []
            for index, points in enumerate(newPoints):
                if index < len(newPoints) - 1:
                    minDist = 1000000
                    indices = []
                    for index_1 in range(index + 1, len(newPoints)):
                        # print index, index_1
                        # print points, newPoints[index_1]
                        for point in points[1]:
                            # print 'puntoReferente'
                            # print point
                            for evaluar in newPoints[index_1][1]:
                                # print 'comparar'
                                # print evaluar
                                dist = ((point[0] - evaluar[0])**2 +
                                        (point[1] - evaluar[1])**2)**(0.5)
                                if dist < minDist:
                                    minDist = dist
                                    indices = [index, index_1]
                        listaFinal.append([indices, minDist])
            if len(listaFinal) > 0:
                maxnum = 0
                for i in listaFinal:
                    if maxnum < i[0][1]:
                        maxnum = i[0][1]
                # print "max ", maxnum
                # print len(clusters), len(newPoints), len(members)
                for i in listaFinal:
                    if i[1] < 10:
                        # print i[0]
                        meanCluster.append(clusters[i[0][0]])
                        meanCluster.append(clusters[i[0][1]])
                        newXmean, newYmean = ballClass.meanBall(meanCluster)
                        clusters[i[0][0]].x = newXmean
                        clusters[i[0][0]].y = newYmean
                        clusters.pop(i[0][1])
                        members[i[0][0]].extend(members[i[0][1]])
                        members.pop(i[0][1])
                        newPoints = ballClass.projectNewPoints(
                            clusters, members)
                        return ballClass.cleaner(clusters, newPoints, members)
                        # return clusters, newPoints, members
            return clusters, newPoints, members
        else:
            return clusters, newPoints, members

    @classmethod
    def drawOnlycluster(cls, image):
        colors = [(252, 63, 63), (252, 170, 63),
                  (248, 252, 63), (113, 252, 63), (63, 252, 245), (63, 157, 252), (85, 67, 173), (175, 60, 224), (224, 60, 207), (224, 60, 7)]
        clusters, members = ballClass.getClusters()
        newPoints = ballClass.projectNewPoints(clusters, members)
        if len(members) > 0:
            for index, j in enumerate(members):
                try:
                    color = colors[index]
                except:
                    color = (0, 0, 0)
                for i in j:
                    cv2.circle(image, (int(i.x), int(i.y)),
                               2, color, -1)
        # Draw the projection of the center point
        if len(clusters) > 0:
            for i in clusters:
                cv2.circle(image, (int(i.x), int(i.y)), 6, (255, 255, 255), -1)
        if newPoints != None:
            for point in newPoints:
                puntos = point[1]
                for i in puntos:
                    cv2.circle(image, (int(i[0]), int(i[1])), 3, (0, 0, 0), 1)

    @classmethod
    def drawClusters(cls, image, clusters, newPoints, members):
        colors = [(252, 63, 63), (252, 170, 63),
                  (248, 252, 63), (113, 252, 63), (63, 252, 245), (63, 157, 252), (85, 67, 173), (175, 60, 224), (224, 60, 207), (224, 60, 7)]

        # if clusters != None and newPoints != None:
        # print len(clusters), len(newPoints)

        # print if enter in a zone
        # inZona(clusters)
        # draw the members of a cluster
        if len(members) > 0:
            for index, j in enumerate(members):
                try:
                    color = colors[index]
                except:
                    color = (0, 0, 0)
                for i in j:
                    cv2.circle(image, (int(i.x), int(i.y)),
                               2, color, -1)
        # Draw the projection of the center point
        if len(clusters) > 0:
            for i in clusters:
                cv2.circle(image, (int(i.x), int(i.y)), 6, (255, 255, 255), -1)
        # Draw de center of the cluster
        if newPoints != None:
            for point in newPoints:
                puntos = point[1]
                for i in puntos:
                    cv2.circle(image, (int(i[0]), int(i[1])), 3, (0, 0, 0), 1)

    @classmethod
    def meanBall(cls, listBall):
        xvalue = 0
        yvalue = 0
        for i in listBall:
            xvalue += i.x
            yvalue += i.y
        xvalue = xvalue / len(listBall)
        yvalue = yvalue / len(listBall)
        return xvalue, yvalue

    @classmethod
    def projectNewPoints(cls, clusters, members):
        angles = [0, 45, 90, 135, 180, 225, 270, 315]
        newPoints = []
        if len(clusters) > 0:
            for index, i in enumerate(clusters):
                newPoints.append([index, []])
                # print "members ", len(members[index])
                distance = len(members[index])
                for angle in angles:
                    newX = i.x + cos(angle * pi / 180) * (distance / 3)
                    newY = i.y - sin(angle * pi / 180) * (distance / 3)
                    newPoints[index][1].append([newX, newY])
            return newPoints

    @classmethod
    def getClusters(cls):
        clusters = []
        clustersFinal = []
        mem = []
        if len(ballClass.registry) > 0:
            clusters.append([ballClass.registry[0], []])
            clusters[0][1].append(ballClass.registry[0])
            for index, i in enumerate(ballClass.registry):
                minimo = 100000
                index_p = None
                objeto = None
                for index_c, j in enumerate(clusters):
                    cluster = j[0]
                    evaluado = ballClass.registry[index]
                    dist = euclideanDistance(
                        cluster.x, evaluado.x, cluster.y, evaluado.y)
                    if dist < minimo:
                        minimo = dist
                        index_p = index_c
                        objeto = evaluado
                if minimo > 50:
                    clusters.append([objeto, []])
                    clusters[-1][1].append(objeto)
                else:
                    clusters[index_p][1].append(objeto)
                    valueX, valueY = ballClass.meanBall(
                        clusters[index_p][1])
                    clusters[index_p][0].x = valueX
                    clusters[index_p][0].y = valueY
        # print len(clusters)
        for i in clusters:
            clustersFinal.append(i[0])
            mem.append(i[1])

        return clustersFinal, mem

    @classmethod
    def wrapper(cls):
        # Get the clusters and their members
        clusters, members = ballClass.getClusters()
        # Get the projections of the center of the clusters
        newPoints = ballClass.projectNewPoints(clusters, members)

        # Get the minimiun distance between clusters
        clusters, newPoints, members = ballClass.cleaner(
            clusters, newPoints, members)
        return clusters, newPoints, members

    @classmethod
    def trackClusters(cls, clusters, image, time):
        for i in clusters:
            if len(clustering.registry) > 0:
                # print len(clustering.registry)
                if(clustering.isNear(i, 140)):
                    # print "near"
                    clustering(i, time)
                # else:
                #    clustering.tracking(i, 100)
                clustering.tracking(i, 140)
                clustering.detectZone()
            else:
                clustering(i, time)
        clustering.pruneCluster()
        clustering.updateAllTime(time)
        clustering.draw(image)
