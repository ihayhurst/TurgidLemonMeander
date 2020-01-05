from flask import Flask, render_template, request
import base64
import graph

app = Flask(__name__)

@app.route("/", methods = ['POST', 'GET'])
def index():
    result=[]
    graphImageData = graph.generateGraph(14, 'Conservatory')
    graphImageData = graphImageData.decode('utf-8')
    lookup="stuff"
    
    if request.method == 'POST':
        result = request.form
        lookup = "wibble"

    return render_template('index.html', result=result, lookup=lookup, graphImageData=graphImageData)


