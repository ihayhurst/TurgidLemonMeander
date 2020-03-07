from flask import Flask, render_template, request
import base64
import graph

app = Flask(__name__)

@app.route("/", methods = ['POST', 'GET'])
def index():
    result=[]
    lookup="stuff"
    
    if request.method == 'POST':
        result = request.form
        region = int(result['region'])*6 #3600 sec in hour / delay interval 600
        lookup = "wibble"
    else:
        region = (6*24)

    graphImageData = graph.generateGraph(region, 'Conservatory')
    graphImageData = graphImageData.decode('utf-8')
    title = "Pi weather report"
    return render_template('index.html',title=title, result=result, lookup=lookup, graphImageData=graphImageData)


