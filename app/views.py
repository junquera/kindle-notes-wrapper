#!flask/bin/python
from app import app
from flask import render_template, request
import json
from hashlib import md5 

class Nota():
    def __init__(self, **kwargs):
                if 'title' in kwargs:
                    self.title = kwargs['title']
                if 'meta' in kwargs:
                    self.meta = kwargs['meta']
                if 'body' in kwargs:
                    self.body = kwargs['body']

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
            note_elements = note.split('\n')
            elements = []
            for raw_element in note_elements:
                if len(raw_element.strip()) > 0:
                    elements.append(raw_element)
            if len(elements) <= 2:
                continue
            
            n = Nota(title=elements[0], meta=elements[1], body=''.join(paragraph for paragraph in elements[2:]))
            key = n.title_key()
            if key in notas:
                notas[key].append(n)
            else:
                notas[key] = [n]
        return render_template('notas.html', title='Notas', n=len(notas), notas=notas)  

    
