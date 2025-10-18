from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///events.db'
db = SQLAlchemy(app)

class Event(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    date = db.Column(db.String(50), nullable=False)
    location = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(300))

class Registration(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_name = db.Column(db.String(100), nullable=False)
    event_id = db.Column(db.Integer, db.ForeignKey('event.id'), nullable=False)
    event = db.relationship('Event', backref=db.backref('registrations', lazy=True))

with app.app_context():
    db.create_all()

@app.route('/events', methods=['GET'])
def get_events():
    events = Event.query.all()
    return jsonify([{
        'id': e.id,
        'name': e.name,
        'date': e.date,
        'location': e.location,
        'description': e.description
    } for e in events])

@app.route('/event', methods=['POST'])
def add_event():
    data = request.get_json()
    new_event = Event(
        name=data['name'],
        date=data['date'],
        location=data['location'],
        description=data.get('description', '')
    )
    db.session.add(new_event)
    db.session.commit()
    return jsonify({'message': 'Event added successfully!'})

@app.route('/register', methods=['POST'])
def register_user():
    data = request.get_json()
    registration = Registration(
        user_name=data['user_name'],
        event_id=data['event_id']
    )
    db.session.add(registration)
    db.session.commit()
    return jsonify({'message': f"{data['user_name']} registered for event ID {data['event_id']}"})

@app.route('/registrations', methods=['GET'])
def get_registrations():
    regs = Registration.query.all()
    return jsonify([{
        'id': r.id,
        'user_name': r.user_name,
        'event': r.event.name
    } for r in regs])

@app.route('/cancel/<int:reg_id>', methods=['DELETE'])
def cancel_registration(reg_id):
    reg = Registration.query.get(reg_id)
    if not reg:
        return jsonify({'error': 'Registration not found'}), 404
    db.session.delete(reg)
    db.session.commit()
    return jsonify({'message': 'Registration cancelled successfully'})

if __name__ == '__main__':
    app.run(debug=True)
