#!flask/bin/python
from app import app
from flask import render_template, request
import json

class Nota():
    def __init__(self, title, meta, body):
        self.title = title
        self.meta = meta
        self.body = ''
        for e in body:
            self.body += "%s\n" % e
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
        notas = []
        for note in notes:
            note_elements = note.split('\n')
            elements = []
            for raw_element in note_elements:
                if len(raw_element.strip()) > 0:
                    elements.append(raw_element)
            if len(elements) <= 2:
                print(elements)
                continue
            notas.append(Nota(elements[0], elements[1], elements[2:]))

        return render_template('notas.html', title='Notas', n=len(notas), notas=notas)  

    
