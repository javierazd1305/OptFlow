#!/usr/bin/env python
#-*- coding: utf-8 -*-

import xml.etree.ElementTree as ET
import ast
import numpy as np
from shapely.geometry.polygon import Polygon


def obtener_punto(event, x, y, flags, param):
    if event == 4:
        print x, y


def extract_point():
    tree = ET.parse('point-1.xml')
    root = tree.getroot()
    lista = []
    polys = []
    inList = []
    outList = []
    draw = []
    inDraw = []
    outDraw = []
    centerPoints = []
    streetsIn = []
    segmentsIn = []
    streetsOut = []
    segmentsOut = []

    for area in root.iter('poly'):
        for tipo in area:
            lista.append([area.attrib['name'], tipo.attrib['type'],
                          ast.literal_eval(tipo[0].attrib['coords'])])
            draw.append([area.attrib['name'], tipo.attrib['type'],
                         ast.literal_eval(tipo[0].attrib['coords'])])

    # New se ha incorporado en el xml dos caracteristicas nuevas sobre el
    # numero de calle y segmento
    for area in root.iter('poly'):
        for tipo in area:
            if tipo.attrib['type'] == "in":
                streetsIn.append(int(tipo[1].attrib['st_number']))
                segmentsIn.append(int(tipo[2].attrib['sg_number']))
            else:
                streetsOut.append(int(tipo[1].attrib['st_number']))
                segmentsOut.append(int(tipo[2].attrib['sg_number']))

    for poly in root.findall('poly'):
        polys.append(poly.attrib['name'])

    for i in lista:
        if i[1] == 'in':
            inList.append(i)
        else:
            outList.append(i)

    for i in draw:
        if i[1] == 'in':
            inDraw.append(i)
        else:
            outDraw.append(i)

    for i in inList:
        i[2] = Polygon(i[2])
    for i in outList:
        i[2] = Polygon(i[2])

    for i in inDraw:
        i[2] = np.array(i[2])
    for i in outDraw:
        i[2] = np.array(i[2])

    # Se ha añadido esto para obtener los puntos centrales de cada area y se
    # retorna la lista
    for i in inDraw:
        xIn = 0
        yIn = 0
        coords = i[2].tolist()
        for j in range(len(coords)):
            xIn += coords[j][0]
            yIn += coords[j][1]
        centerPoints.append([xIn / len(coords), yIn / len(coords)])
    # print streetsIn, segmentsIn, streetsOut, segmentsOut
    return inList, outList, inDraw, outDraw, polys, centerPoints, streetsIn, segmentsIn, streetsOut, segmentsOut


extract_point()
