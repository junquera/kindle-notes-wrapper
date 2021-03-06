#!flask/bin/python
#-*- coding: utf-8 -*-
from app import app
from flask import render_template, request
import json
from hashlib import md5
import re
from datetime import datetime

# TODO El 'Añ' no funciona, creo que por la Ñ
date_regex = ur'Añadid[oa] el ([^\s,]+),? ([1-9]|[1-3][0-9]?) de ([^\s]+) de ([0-9]+) (?:([0-9]+)\:([0-9]+)|([0-9]+)H([0-9]+)\')'

# TODO Hay que cambiar las claves de estos diccionarios para evitar caracteres UNICODE
week_days = {'lunes': 1, 'martes': 2, u'miércoles': 3, 'jueves': 4, 'viernes': 5, u'sábado': 6, 'domingo': 7}
months = {'enero': 1, 'febrero': 2, 'marzo': 3, 'abril': 4, 'mayo': 5, 'junio': 6, 'julio': 7, 'agosto': 8, 'septiembre': 9, 'octubre': 10, 'noviembre': 11, 'diciembre': 12}

class Meta():
    def __init__(self, **kwargs):
       if 'page' in kwargs:
           self.page = kwargs['page']
       if 'position' in kwargs:
           self.position = kwargs['position']
       if 'date' in kwargs:
           self.date = kwargs['date']

    def parse(self, raw):
        parts = raw.split('|')
        if len(parts) < 3:
            raise Exception("Bad metad")
        page_raw = parts[0].strip()
        position_raw = parts[1].strip()
        date_raw = parts[2].strip()
        try:
            self.page = re.search(r'[0-9]+$', page_raw).group(0)
        except:
            self.page = page_raw

        try:
            self.position = re.search(r'[0-9]+\-[0-9]+$', position_raw).group(0)
        except:
            self.position = position_raw

        date_parts = re.search(date_regex, date_raw, re.UNICODE)
        try:
            date_parts = date_parts.groups()
            aux = []
            for part in date_parts:
                if part is not None:
                    aux.append(part)
            date_parts = aux
            self.date = datetime(int(date_parts[3]), int(months[date_parts[2]]), int(week_days[date_parts[0]]), hour=int(date_parts[4]), minute=int(date_parts[5]))
        except Exception as e:
            print(e)
            print(date_raw)
            self.date = date_raw

        return self


class Nota():
    def genBody(self, body_parts):
        return ''.join("%s\n" % paragraph for paragraph in body_parts)

    def __init__(self, **kwargs):
                if 'title' in kwargs:
                    self.title = kwargs['title']
                if 'meta' in kwargs:
                    self.meta = kwargs['meta']
                if 'body' in kwargs:
                    self.body = kwargs['body']
    def parse(self, raw):
        note_elements = raw.split('\n')
        elements = []
        for raw_element in note_elements:
            if len(raw_element.strip()) > 0:
                elements.append(raw_element)

        if len(elements) > 2:
            self.title = elements[0]
            self.meta = Meta().parse(elements[1])
            self.body = self.genBody(elements[2:])
        else:
            raise Exception("Nota incorrecta")

        return self

    def title_key(self):
        bb = bytearray(self.title, 'utf-8')
        return md5(bb).hexdigest()

    @property
    def serialize(self):
        return '{"title": "%r", "meta": "%r", "body": "%r"}' % (self.title, self.meta, self.body)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'GET':
        return render_template('index.html')
    elif request.method == 'POST':
        clips = request.files['notas'].read().decode('utf-8')
        notes = clips.split('==========')
        notas = {}
        for note in notes:
            try:
                n = Nota().parse(note)
            except Exception as e:
                continue
            key = n.title_key()
            if key in notas:
                notas[key].append(n)
            else:
                notas[key] = [n]
        return render_template('notas.html', title='Notas', n=len(notas), notas=notas)
