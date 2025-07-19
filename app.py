from flask import Flask, request, jsonify, render_template, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
import qrcode
import io
import base64
import uuid
import secrets
import requests
import json
from functools import wraps

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-change-this'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///smart_ticketing.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Database Models
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    password_hash = db.Column(db.String(120), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    tickets = db.relationship('Ticket', backref='user', lazy=True)

class Event(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    price = db.Column(db.Float, nullable=False)
    date = db.Column(db.DateTime, nullable=False)
    location = db.Column(db.String(200), nullable=False)
    max_capacity = db.Column(db.Integer, default=100)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    tickets = db.relationship('Ticket', backref='event', lazy=True)

class Ticket(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ticket_id = db.Column(db.String(36), unique=True, nullable=False, default=lambda: str(uuid.uuid4()))
    qr_code = db.Column(db.String(36), unique=True, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    event_id = db.Column(db.Integer, db.ForeignKey('event.id'), nullable=False)
    payment_status = db.Column(db.String(20), default='pending')  # pending, paid, failed
    payment_reference = db.Column(db.String(100))
    is_used = db.Column(db.Boolean, default=False)
    purchase_date = db.Column(db.DateTime, default=datetime.utcnow)
    used_date = db.Column(db.DateTime)
    qr_image_data = db.Column(db.Text)  # Base64 encoded QR image

class EntryLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ticket_id = db.Column(db.Integer, db.ForeignKey('ticket.id'), nullable=False)
    entry_time = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(20))  # granted, denied
    device_id = db.Column(db.String(50))  # ESP32 device identifier
    ticket = db.relationship('Ticket', backref='entry_logs')

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Helper Functions
def generate_qr_code(data):
    """Generate QR code and return base64 encoded image"""
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(data)
    qr.make(fit=True)
    
    img = qr.make_image(fill_color="black", back_color="white")
    buffer = io.BytesIO()
    img.save(buffer, format='PNG')
    buffer.seek(0)
    
    return base64.b64encode(buffer.getvalue()).decode()

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            return jsonify({'error': 'Admin access required'}), 403
        return f(*args, **kwargs)
    return decorated_function

def process_mobile_payment(phone, amount, reference):
    """
    Simulate mobile money payment processing
    In production, integrate with actual mobile money APIs like MTN Mobile Money, Airtel Money
    """
    # This is a simulation - replace with actual mobile money API calls
    try:
        # Simulate API call delay
        import time
        time.sleep(2)
        
        # Simulate 90% success rate
        import random
        if random.random() < 0.9:
            return {
                'status': 'success',
                'transaction_id': f'MM{secrets.token_hex(8).upper()}',
                'message': 'Payment processed successfully'
            }
        else:
            return {
                'status': 'failed',
                'message': 'Payment processing failed'
            }
    except Exception as e:
        return {
            'status': 'failed',
            'message': f'Payment error: {str(e)}'
        }

# Routes
@app.route('/')
def index():
    events = Event.query.filter_by(is_active=True).all()
    return render_template('index.html', events=events)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        data = request.get_json() if request.is_json else request.form
        
        username = data.get('username')
        email = data.get('email')
        phone = data.get('phone')
        password = data.get('password')
        
        if User.query.filter_by(username=username).first():
            if request.is_json:
                return jsonify({'error': 'Username already exists'}), 400
            flash('Username already exists')
            return redirect(url_for('register'))
        
        if User.query.filter_by(email=email).first():
            if request.is_json:
                return jsonify({'error': 'Email already exists'}), 400
            flash('Email already exists')
            return redirect(url_for('register'))
        
        user = User(
            username=username,
            email=email,
            phone=phone,
            password_hash=generate_password_hash(password)
        )
        
        db.session.add(user)
        db.session.commit()
        
        if request.is_json:
            return jsonify({'message': 'User registered successfully'}), 201
        
        flash('Registration successful')
        return redirect(url_for('login'))
    
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        data = request.get_json() if request.is_json else request.form
        
        username = data.get('username')
        password = data.get('password')
        
        user = User.query.filter_by(username=username).first()
        
        if user and check_password_hash(user.password_hash, password):
            login_user(user)
            if request.is_json:
                return jsonify({'message': 'Login successful', 'user_id': user.id}), 200
            return redirect(url_for('dashboard'))
        
        if request.is_json:
            return jsonify({'error': 'Invalid credentials'}), 401
        flash('Invalid credentials')
    
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/dashboard')
@login_required
def dashboard():
    tickets = Ticket.query.filter_by(user_id=current_user.id).order_by(Ticket.purchase_date.desc()).all()
    return render_template('dashboard.html', tickets=tickets)

@app.route('/purchase/<int:event_id>', methods=['GET', 'POST'])
@login_required
def purchase_ticket(event_id):
    event = Event.query.get_or_404(event_id)
    
    if request.method == 'POST':
        # Check if event is still available
        current_tickets = Ticket.query.filter_by(event_id=event_id, payment_status='paid').count()
        if current_tickets >= event.max_capacity:
            if request.is_json:
                return jsonify({'error': 'Event is sold out'}), 400
            flash('Event is sold out')
            return redirect(url_for('index'))
        
        # Create ticket with pending payment
        qr_data = secrets.token_urlsafe(32)
        qr_image = generate_qr_code(qr_data)
        
        ticket = Ticket(
            user_id=current_user.id,
            event_id=event_id,
            qr_code=qr_data,
            qr_image_data=qr_image,
            payment_status='pending'
        )
        
        db.session.add(ticket)
        db.session.commit()
        
        # Process mobile payment
        payment_ref = f'TKT{ticket.id}{secrets.token_hex(4).upper()}'
        payment_result = process_mobile_payment(current_user.phone, event.price, payment_ref)
        
        if payment_result['status'] == 'success':
            ticket.payment_status = 'paid'
            ticket.payment_reference = payment_result['transaction_id']
            db.session.commit()
            
            if request.is_json:
                return jsonify({
                    'message': 'Ticket purchased successfully',
                    'ticket_id': ticket.ticket_id,
                    'qr_code': qr_data
                }), 200
            
            flash('Ticket purchased successfully!')
            return redirect(url_for('dashboard'))
        else:
            ticket.payment_status = 'failed'
            db.session.commit()
            
            if request.is_json:
                return jsonify({'error': payment_result['message']}), 400
            
            flash(f'Payment failed: {payment_result["message"]}')
            return redirect(url_for('index'))
    
    return render_template('purchase.html', event=event)

# ESP32 API Endpoints
@app.route('/api/validate_qr', methods=['POST'])
def validate_qr():
    """
    API endpoint for ESP32 to validate QR codes
    Expected payload: {"qr_code": "qr_code_data", "device_id": "esp32_device_id"}
    """
    data = request.get_json()
    
    if not data or 'qr_code' not in data:
        return jsonify({
            'status': 'error',
            'message': 'QR code is required',
            'access_granted': False
        }), 400
    
    qr_code = data['qr_code']
    device_id = data.get('device_id', 'unknown')
    
    # Find ticket by QR code
    ticket = Ticket.query.filter_by(qr_code=qr_code).first()
    
    if not ticket:
        # Log failed entry attempt
        entry_log = EntryLog(
            ticket_id=None,
            status='denied',
            device_id=device_id
        )
        db.session.add(entry_log)
        db.session.commit()
        
        return jsonify({
            'status': 'error',
            'message': 'Invalid QR code',
            'access_granted': False,
            'display_message': 'ACCESS DENIED\nInvalid Ticket'
        }), 404
    
    # Check if ticket is paid
    if ticket.payment_status != 'paid':
        entry_log = EntryLog(
            ticket_id=ticket.id,
            status='denied',
            device_id=device_id
        )
        db.session.add(entry_log)
        db.session.commit()
        
        return jsonify({
            'status': 'error',
            'message': 'Ticket not paid',
            'access_granted': False,
            'display_message': 'ACCESS DENIED\nTicket Not Paid'
        }), 403
    
    # Check if ticket is already used
    if ticket.is_used:
        entry_log = EntryLog(
            ticket_id=ticket.id,
            status='denied',
            device_id=device_id
        )
        db.session.add(entry_log)
        db.session.commit()
        
        return jsonify({
            'status': 'error',
            'message': 'Ticket already used',
            'access_granted': False,
            'display_message': 'ACCESS DENIED\nTicket Already Used'
        }), 403
    
    # Check if event is today (within 24 hours)
    event_date = ticket.event.date
    now = datetime.utcnow()
    if abs((event_date - now).days) > 1:
        entry_log = EntryLog(
            ticket_id=ticket.id,
            status='denied',
            device_id=device_id
        )
        db.session.add(entry_log)
        db.session.commit()
        
        return jsonify({
            'status': 'error',
            'message': 'Event date mismatch',
            'access_granted': False,
            'display_message': 'ACCESS DENIED\nEvent Not Today'
        }), 403
    
    # All checks passed - grant access
    ticket.is_used = True
    ticket.used_date = datetime.utcnow()
    
    entry_log = EntryLog(
        ticket_id=ticket.id,
        status='granted',
        device_id=device_id
    )
    
    db.session.add(entry_log)
    db.session.commit()
    
    return jsonify({
        'status': 'success',
        'message': 'Access granted',
        'access_granted': True,
        'display_message': f'ACCESS GRANTED\nWelcome {ticket.user.username}',
        'user_name': ticket.user.username,
        'event_name': ticket.event.name,
        'ticket_id': ticket.ticket_id
    }), 200

@app.route('/api/device_status', methods=['POST'])
def device_status():
    """
    API endpoint for ESP32 to report its status
    """
    data = request.get_json()
    device_id = data.get('device_id', 'unknown')
    status = data.get('status', 'unknown')
    
    # Log device status (you might want to create a DeviceStatus model)
    print(f"Device {device_id} status: {status}")
    
    return jsonify({
        'status': 'success',
        'message': 'Status received',
        'server_time': datetime.utcnow().isoformat()
    }), 200

# Admin Routes
@app.route('/admin')
@login_required
@admin_required
def admin_dashboard():
    total_tickets = Ticket.query.count()
    paid_tickets = Ticket.query.filter_by(payment_status='paid').count()
    used_tickets = Ticket.query.filter_by(is_used=True).count()
    recent_entries = EntryLog.query.order_by(EntryLog.entry_time.desc()).limit(10).all()
    
    stats = {
        'total_tickets': total_tickets,
        'paid_tickets': paid_tickets,
        'used_tickets': used_tickets,
        'revenue': sum(ticket.event.price for ticket in Ticket.query.filter_by(payment_status='paid').all())
    }
    
    return render_template('admin_dashboard.html', stats=stats, recent_entries=recent_entries)

@app.route('/admin/events', methods=['GET', 'POST'])
@login_required
@admin_required
def manage_events():
    if request.method == 'POST':
        data = request.get_json() if request.is_json else request.form
        
        event = Event(
            name=data['name'],
            description=data['description'],
            price=float(data['price']),
            date=datetime.strptime(data['date'], '%Y-%m-%dT%H:%M'),
            location=data['location'],
            max_capacity=int(data['max_capacity'])
        )
        
        db.session.add(event)
        db.session.commit()
        
        if request.is_json:
            return jsonify({'message': 'Event created successfully'}), 201
        
        flash('Event created successfully')
    
    events = Event.query.order_by(Event.date.desc()).all()
    return render_template('manage_events.html', events=events)

@app.route('/admin/users')
@login_required
@admin_required
def manage_users():
    users = User.query.order_by(User.created_at.desc()).all()
    return render_template('manage_users.html', users=users)

@app.route('/ticket/<ticket_id>')
@login_required
def view_ticket(ticket_id):
    ticket = Ticket.query.filter_by(ticket_id=ticket_id).first_or_404()
    
    # Check if user owns this ticket or is admin
    if ticket.user_id != current_user.id and not current_user.is_admin:
        flash('Access denied')
        return redirect(url_for('dashboard'))
    
    return render_template('ticket_detail.html', ticket=ticket)

def init_database():
    """Initialize database and create admin user if needed"""
    db.create_all()
    
    # Create admin user if doesn't exist
    admin = User.query.filter_by(username='admin').first()
    if not admin:
        admin = User(
            username='admin',
            email='admin@smartticket.com',
            phone='+250788000000',
            password_hash=generate_password_hash('admin123'),
            is_admin=True
        )
        db.session.add(admin)
        db.session.commit()
        print("Admin user created: username=admin, password=admin123")

if __name__ == '__main__':
    with app.app_context():
        init_database()
    
    app.run(debug=True, host='0.0.0.0', port=5000)