import json,time,sys
from flask import Flask

sys.path.append('../')
sys.path.append('../predict')
from predict import console

app = Flask(__name__)


@app.route('/testapi/<uid>', methods=['GET', 'POST'])
def firstapi(uid):
    pred, p = console.Predict(uid)
    return json.dumps({'status': 0,'content': {'predict': pred,'p': float(p)}})

if __name__ == "__main__":
    app.run(port=8080, host='0.0.0.0', debug=True, threaded=True)

