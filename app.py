# mongo.py

from flask import Flask
from flask import jsonify
from flask import request
from flask import render_template
from flask_pymongo import PyMongo
import os

app = Flask(__name__)

app.config['MONGO_DBNAME'] = 'restdb'
app.config['MONGO_URI'] =  os.environ['MONGODB_URL']
#'mongodb://test:test@mongodb-0.mongodb-headless:27017,mongodb-1.mongodb-headless/restdb?authSource=restdb'

mongo = PyMongo(app)

@app.route('/star', methods=['GET'])
def get_all_stars():
  star = mongo.db.stars
  output = []
  for s in star.find():
    output.append({'name' : s['name'], 'distance' : s['distance']})
  return render_template('index.html', title='Home', stars=output)

@app.route('/star/', methods=['GET'])
def get_one_star(name):
  star = mongo.db.stars
  s = star.find_one({'name' : name})
  if s:
    output = {'name' : s['name'], 'distance' : s['distance']}
  else:
    output = "No such name"
  return jsonify({'result' : output})

@app.route('/star', methods=['POST'])
def add_star():
  star = mongo.db.stars
  name = request.json['name']
  distance = request.json['distance']
  star_id = star.insert({'name': name, 'distance': distance})
  new_star = star.find_one({'_id': star_id })
  output = {'name' : new_star['name'], 'distance' : new_star['distance']}
  return jsonify({'result' : output})

if __name__ == '__main__':
    app.run(host='0.0.0.0',debug=True)