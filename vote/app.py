from flask import Flask, render_template, request, make_response, g
from redis import Redis
import os
import socket
import random
import json
import logging

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
users={
    "Angelica":{'Blues Traveler': 3.5, 'Broken Bells': 2.0, 'Norah Jones': 4.5, 'Phoenix': 5.0, 'Sligtly Stoopid': 1.5, 'The Strokes': 2.5, 'Vampire Weekend': 2.0},
    "Bill":{'Blues Traveler': 2.0, 'Broken Bells': 3.5, 'Deadmau5': 4.0, 'Phoenix': 2.0, 'Sligtly Stoopid': 3.5, 'Vampire Weekend': 3.0},
    "Chan":{'Blues Traveler': 5.0, 'Broken Bells': 1.0, 'Deadmau5': 1.0, 'Norah Jones': 3.0, 'Phoenix': 5.0, 'Sligtly Stoopid': 1.0},
    "Dan":{'Blues Traveler': 3.0, 'Broken Bells': 4.0, 'Deadmau5': 4.5, 'Phoenix': 3.0, 'Sligtly Stoopid': 4.5, 'The Strokes': 4.0, 'Vampire Weekend': 2.0},
    "Hailey":{'Broken Bells': 4.0, 'Deadmau5': 1.0, 'Norah Jones': 4.0, 'The Strokes': 4.0, 'Vampire Weekend': 1.0},
    "Jordym":{'Broken Bells': 4.5, 'Deadmau5': 4.0, 'Norah Jones': 5.0, 'Phoenix': 5.0, 'Sligtly Stoopid': 4.5, 'The Strokes': 4.0, 'Vampire Weekend': 4.0},
    "Sam":{'Blues Traveler': 5.0, 'Broken Bells': 2.0, 'Norah Jones': 3.0, 'Phoenix': 5.0, 'Sligtly Stoopid': 4.0, 'The Strokes': 5.0},
    "Veronica":{'Blues Traveler': 3.0, 'Norah Jones': 5.0, 'Phoenix': 4.0, 'Sligtly Stoopid': 2.5, 'The Strokes': 3.0},
}

def manhattan(rating1, rating2):
    distance = 0
    total = 0
    for key in rating1:
        if key in rating2:
            distance += abs(rating1[key] - rating2[key])
            total += 1
    if total > 0:
        return distance / total
    else:
        return -1

@app.route("/", methods=['POST','GET'])
def hello():
    voter_id = request.cookies.get('voter_id')
    if not voter_id:
        voter_id = hex(random.getrandbits(64))[2:-1]

    vote = None

    if request.method == 'POST':
        redis = get_redis() 
        vote = request.form['vote']
        if vote == 'a':
            manhatan = manhattan(users['Angelica'], users["Bill"])
        else:
            manhatan = manhattan(users['Chan'], users["Bill"])
            print(voter_id,vote)
        print(manhatan)
        app.logger.info('Received vote for %s', vote)
        data = json.dumps({'voter_id': voter_id, 'vote': vote, 'manhatan': manhatan})
        print (data)
        redis.rpush('votes', data)

    resp = make_response(render_template(
        'index.html',
        option_a=option_a,
        option_b=option_b,
        hostname=hostname,
        vote=vote,
    ))
    resp.set_cookie('voter_id', voter_id)
    return resp


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=80, debug=True, threaded=True)
