from flask import Flask, request, render_template
import requests
from flask_cors import CORS, cross_origin
from secretary import Secretary

app = Flask(__name__)
app.debug = True
cors = CORS(app)


secretary = Secretary()
@app.route('/', methods=['POST'])
def getPost():
    try:
        if request.method == 'POST':
            data = request.json
            secretary.main(data)
            return ''

    except Exception as error:
        print(error)

if __name__ == "__main__":
    app.run(port=9003)
