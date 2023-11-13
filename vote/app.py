from flask import Flask, render_template, request, make_response, g, abort
from redis import Redis
import os
import socket
import random
import json
import logging
from algoritmos import manhattan, users, pearson

option_a = os.getenv('OPTION_A', "Bill y Angelica")
option_b = os.getenv('OPTION_B', "Bill y Chan")
hostname = socket.gethostname()

app = Flask(__name__)

gunicorn_error_logger = logging.getLogger('gunicorn.error')
app.logger.handlers.extend(gunicorn_error_logger.handlers)
app.logger.setLevel(logging.INFO)

def get_redis():
    if not hasattr(g, 'redis'):
        g.redis = Redis(host="redis", db=0, socket_timeout=5)
    return g.redis

@app.route("/", methods=['POST','GET'])
def hello():
    voter_id = request.cookies.get('voter_id')
    if not voter_id:
        voter_id = hex(random.getrandbits(64))[2:-1]

    vote = user1 = user2 = None

    if request.method == 'POST':
        redis = get_redis() 
        user1 = request.form['user1']
        user2 = request.form['user2']
        option = request.form['options']
        if option == "1":
            try:
                resultado = str(manhattan(users[user1], users[user2]))
                seleccion = "Manhatan"
            except Exception as e:
                print(f"Se produjo un error: {e}")
                abort(404)
        elif option == "2":
            try:
                resultado = str(pearson(users[user1], users[user2]))
                seleccion = "Pearson"
            except Exception as e:
                print(f"Se produjo un error: {e}")
                abort(404)
            
        else:
            abort(404)
        app.logger.info('Received vote for %s', resultado)
        data = json.dumps({'voter_id': voter_id, 'user1': user1, 'user2': user2, 'option': seleccion, 'result': resultado})
        print (data)
        redis.rpush('votes', data)

    resp = make_response(render_template(
        'index.html',
        option_a=option_a,
        option_b=option_b,
        hostname=hostname,
    ))
    resp.set_cookie('voter_id', voter_id)
    return resp

@app.errorhandler(404)
def not_found_error(error):
    return "El usuario ingresado no existe", 404

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=80, debug=True, threaded=True)
