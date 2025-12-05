import json

import flask
import cwa

with open('env.json', encoding='utf-8') as f:
    env = json.load(f)

app = flask.Flask(__name__)

cwa_key = env['key']

@app.route("/cwa", methods=['GET', 'POST'])
def cwa_():
    '''http://127.0.0.1:5000/cwa?site=臺北''' 
    site = flask.request.args.get('site')
    if site:
        return cwa.tostr(cwa.cwa(site, cwa_key), ', ')
    return 'Bad Request', 400

if __name__ == "__main__":
    app.run()