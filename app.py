from flask import Flask, request, jsonify, session
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///events.db'
app.config['SECRET_KEY'] = 'supersecretkey'
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)

class Admin(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)

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

@app.route('/admin/register', methods=['POST'])
def register_admin():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    if Admin.query.filter_by(username=username).first():
        return jsonify({'error': 'Username already exists'}), 400
    hashed_pw = bcrypt.generate_password_hash(password).decode('utf-8')
    new_admin = Admin(username=username, password=hashed_pw)
    db.session.add(new_admin)
    db.session.commit()
    return jsonify({'message': 'Admin registered successfully!'})

@app.route('/admin/login', methods=['POST'])
def login_admin():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    admin = Admin.query.filter_by(username=username).first()
    if admin and bcrypt.check_password_hash(admin.password, password):
        session['admin'] = username
        return jsonify({'message': f'Welcome back, {username}!'})
    return jsonify({'error': 'Invalid username or password'}), 401

@app.route('/admin/logout', methods=['POST'])
def logout_admin():
    session.pop('admin', None)
    return jsonify({'message': 'Logged out successfully'})

@app.route('/admin/add_event', methods=['POST'])
def add_event():
    if 'admin' not in session:
        return jsonify({'error': 'Unauthorized. Please log in as admin.'}), 401
    data = request.get_json()
    new_event = Event(
        name=data['name'],
        date=data['date'],
        location=data['location'],
        description=data.get('description', '')
    )
    db.session.add(new_event)
    db.session.commit()
    return jsonify({'message': f"Event '{data['name']}' added by {session['admin']}!"})

@app.route('/admin/events', methods=['GET'])
def view_all_events():
    if 'admin' not in session:
        return jsonify({'error': 'Unauthorized. Please log in as admin.'}), 401
    events = Event.query.all()
    return jsonify([{
        'id': e.id,
        'name': e.name,
        'date': e.date,
        'location': e.location,
        'description': e.description
    } for e in events])

if __name__ == '__main__':
    app.run(debug=True)
