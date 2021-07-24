from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from geoalchemy2 import Geometry
from sqlalchemy.sql.functions import func
from flask_cors import CORS, cross_origin
from decouple import config as config_decouple
from config import config
import uuid
import statistics

enviroment = config['development']
if config_decouple('PRODUCTION', default=False):
    enviroment = config['production']

app = Flask(__name__)
CORS(app)
app.config.from_object(enviroment)
db = SQLAlchemy(app)

class Restaurants(db.Model):
    id = db.Column(db.Text, primary_key=True)
    rating = db.Column(db.Integer)
    name = db.Column(db.Text)
    site = db.Column(db.Text)
    email = db.Column(db.Text)
    phone = db.Column(db.Text)
    street = db.Column(db.Text)
    city = db.Column(db.Text)
    state = db.Column(db.Text)
    lat = db.Column(db.Float)
    lng = db.Column(db.Float)

    def to_json(self):
        return {
            'id': self.id,
            'rating': self.rating,
            'name': self.name,
            'site': self.site,
            'email': self.email,
            'phone' : self.phone,
            'street' : self.street,
            'city' : self.city,
            'state' : self.state,
            'lat' : self.lat,
            'lng' : self.lng
        }


@app.route('/', methods = ['GET'])
@cross_origin()
def prendas():
    return jsonify({'Api':'Restaurants Api', 'developer': 'Victor Bohorquez'}), 200

@app.route('/create-restaurant', methods = ['POST'])
@cross_origin()
def create_restaurant():
    data = request.get_json()
    restaurant = Restaurants.query.filter_by(name = data['name']).first()
    if(restaurant):
        return jsonify({'msj': 'El restaurante ya existe'}),400
    elif(data['rating']<0 or data['rating']>4):
        return jsonify({'msj': 'El rating debe se entre 0 y 4'}),400
    id = uuid.uuid4()
    new_restaurant = Restaurants(id = id, rating = data['rating'], name=data['name'] , site=data['site'], email=data['email'], 
        phone=data['phone'], street=data['street'], city=data['city'], state=data['state'], lat=data['lat'], lng=data['lng'])
    db.session.add(new_restaurant)
    db.session.commit()
    return jsonify({'msj': 'Restaurante creado correctamente'}),200

@app.route('/getrestaurants', methods=['GET'])
@cross_origin()
def getrestaurants():
    restaurant = Restaurants.query.all()
    restaurants = []
    for element in restaurant:
        restaurants.append(element.to_json())
    return jsonify({'restaurants': restaurants}),200

@app.route('/getrestaurants/<rest>', methods=['GET'])
@cross_origin()
def getuser(rest):
    restaurant = Restaurants.query.filter_by(id = rest).first()
    if not restaurant:
         return jsonify({'msj': 'No se encontró el restaurante'}),400
    
    return jsonify({'Restaurant': restaurant.to_json()}),200

@app.route('/delete-restaurant/<id>', methods = ['DELETE'])
@cross_origin()
def delete_restaurant(id):
     restaurant = Restaurants.query.filter_by(id = id).first()
     if not restaurant:
         return jsonify({'msj': 'No se encontró el restaurante'}),400
    
     db.session.delete(restaurant)
     db.session.commit()
     return jsonify({'msj': 'Restaurante eliminado'}),200

@app.route('/update-restaurant', methods = ['PUT'])
@cross_origin()
def update_restaurant():
    data = request.get_json()
    restaurant = Restaurants.query.filter_by(id = data['id']).first()
    if not (restaurant):
        return jsonify({'msj': 'El restaurante no existe'}),400
    if(data['rating']<0 or data['rating']>4):
        return jsonify({'msj': 'El rating debe se entre 0 y 4'}),400
    restaurant.rating = data['rating']
    restaurant.name=data['name']
    restaurant.site=data['site']
    restaurant.email=data['email']
    restaurant. phone=data['phone']
    restaurant.street=data['street']
    restaurant.city=data['city']
    restaurant.state=data['state']
    restaurant.lat=data['lat']
    restaurant.lng=data['lng']
    db.session.commit()
    return jsonify({'msj': 'Restaurante actualizado'}),200

@app.route('/restaurants/statistics', methods=['GET'])
@cross_origin()
def satatistics():
    lat = float(request.args.get('latitude'))
    lng = float(request.args.get('longitude'))
    r = float(request.args.get('radius'))
    near = db.session.query(Restaurants).filter(func.ST_Distance_Sphere(func.ST_MakePoint(Restaurants.lng,Restaurants.lat),func.ST_MakePoint(lng,lat)) <= r ).all()
    count = len(near)
    rates = []
    for element in near:
        rates.append(int(element.rating))
    dev = 0
    if len(rates)>1:
        dev = statistics.stdev(rates)
    return jsonify({'Restaurants': count, 'Average Rating': statistics.mean(rates), 'Standard Deviation': dev}),200

@app.route('/getbyrate/<rate>', methods=['GET'])
@cross_origin()
def getrate(rate):
    restaurant = Restaurants.query.filter_by(rating = int(rate)).all()
    if not restaurant:
         return jsonify({'msj': 'No se encontraron restaurantes'}),400
    restaurants = []
    for element in restaurant:
        restaurants.append(element.to_json())
    return jsonify({'Restaurants': restaurants}),200

if __name__ == '__main__':
    app.run()