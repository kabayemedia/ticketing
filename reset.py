#!/usr/bin/env python3
"""
Quick fix script to create missing templates
Run this script in your project directory to create all missing templates
"""

import os

def create_missing_templates():
    # Create templates directory if it doesn't exist
    if not os.path.exists('templates'):
        os.makedirs('templates')
        print("✅ Created templates directory")
    
    # Template contents
    templates = {
        'base.html': '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{% block title %}Smart Ticketing System{% endblock %}</title>
    <link href="https://cdnjs.cloudflare.com/ajax/libs/bootstrap/5.3.0/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css" rel="stylesheet">
    <style>
        .qr-code-container { text-align: center; margin: 20px 0; }
        .ticket-card { border: 2px solid #007bff; border-radius: 10px; padding: 20px; margin: 10px 0; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }
        .status-paid { border-color: #28a745; }
        .status-pending { border-color: #ffc107; }
        .status-failed { border-color: #dc3545; }
        .navbar-brand { font-weight: bold; }
        .footer { margin-top: 50px; padding: 20px 0; background-color: #f8f9fa; }
    </style>
</head>
<body>
    <nav class="navbar navbar-expand-lg navbar-dark bg-primary">
        <div class="container">
            <a class="navbar-brand" href="{{ url_for('index') }}">
                <i class="fas fa-ticket-alt"></i> Smart Ticketing
            </a>
            <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNav">
                <span class="navbar-toggler-icon"></span>
            </button>
            <div class="collapse navbar-collapse" id="navbarNav">
                <ul class="navbar-nav me-auto">
                    <li class="nav-item"><a class="nav-link" href="{{ url_for('index') }}">Events</a></li>
                    {% if current_user.is_authenticated %}
                    <li class="nav-item"><a class="nav-link" href="{{ url_for('dashboard') }}">My Tickets</a></li>
                    {% if current_user.is_admin %}
                    <li class="nav-item dropdown">
                        <a class="nav-link dropdown-toggle" href="#" role="button" data-bs-toggle="dropdown">Admin</a>
                        <ul class="dropdown-menu">
                            <li><a class="dropdown-item" href="{{ url_for('admin_dashboard') }}">Dashboard</a></li>
                            <li><a class="dropdown-item" href="{{ url_for('manage_events') }}">Manage Events</a></li>
                            <li><a class="dropdown-item" href="{{ url_for('manage_users') }}">Manage Users</a></li>
                        </ul>
                    </li>
                    {% endif %}
                    {% endif %}
                </ul>
                <ul class="navbar-nav">
                    {% if current_user.is_authenticated %}
                    <li class="nav-item dropdown">
                        <a class="nav-link dropdown-toggle" href="#" role="button" data-bs-toggle="dropdown">
                            <i class="fas fa-user"></i> {{ current_user.username }}
                        </a>
                        <ul class="dropdown-menu">
                            <li><a class="dropdown-item" href="{{ url_for('logout') }}">Logout</a></li>
                        </ul>
                    </li>
                    {% else %}
                    <li class="nav-item"><a class="nav-link" href="{{ url_for('login') }}">Login</a></li>
                    <li class="nav-item"><a class="nav-link" href="{{ url_for('register') }}">Register</a></li>
                    {% endif %}
                </ul>
            </div>
        </div>
    </nav>
    <main class="container mt-4">
        {% with messages = get_flashed_messages() %}
            {% if messages %}
                {% for message in messages %}
                    <div class="alert alert-info alert-dismissible fade show" role="alert">
                        {{ message }}
                        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
                    </div>
                {% endfor %}
            {% endif %}
        {% endwith %}
        {% block content %}{% endblock %}
    </main>
    <footer class="footer mt-auto bg-light">
        <div class="container text-center">
            <span class="text-muted">&copy; 2025 Smart Ticketing System - Secure, Fast, Efficient</span>
        </div>
    </footer>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/bootstrap/5.3.0/js/bootstrap.bundle.min.js"></script>
    {% block scripts %}{% endblock %}
</body>
</html>''',

        'index.html': '''{% extends "base.html" %}
{% block title %}Events - Smart Ticketing{% endblock %}
{% block content %}
<div class="row">
    <div class="col-12">
        <h1 class="mb-4"><i class="fas fa-calendar-alt"></i> Available Events</h1>
    </div>
</div>
{% if events %}
<div class="row">
    {% for event in events %}
    <div class="col-md-6 col-lg-4 mb-4">
        <div class="card h-100">
            <div class="card-body">
                <h5 class="card-title">{{ event.name }}</h5>
                <p class="card-text">{{ event.description }}</p>
                <div class="mb-2"><strong><i class="fas fa-map-marker-alt"></i> Location:</strong> {{ event.location }}</div>
                <div class="mb-2"><strong><i class="fas fa-calendar"></i> Date:</strong> {{ event.date.strftime('%Y-%m-%d %H:%M') }}</div>
                <div class="mb-2"><strong><i class="fas fa-users"></i> Capacity:</strong> {{ event.max_capacity }}</div>
                <div class="mb-3"><strong><i class="fas fa-money-bill"></i> Price:</strong> <span class="text-success">{{ "{:,.0f}".format(event.price) }} RWF</span></div>
            </div>
            <div class="card-footer">
                {% if current_user.is_authenticated %}
                    <a href="{{ url_for('purchase_ticket', event_id=event.id) }}" class="btn btn-primary w-100">
                        <i class="fas fa-shopping-cart"></i> Purchase Ticket
                    </a>
                {% else %}
                    <a href="{{ url_for('login') }}" class="btn btn-outline-primary w-100">Login to Purchase</a>
                {% endif %}
            </div>
        </div>
    </div>
    {% endfor %}
</div>
{% else %}
<div class="text-center">
    <i class="fas fa-calendar-times fa-5x text-muted mb-3"></i>
    <h3>No Events Available</h3>
    <p class="text-muted">Check back later for upcoming events!</p>
</div>
{% endif %}
{% endblock %}''',

        'login.html': '''{% extends "base.html" %}
{% block title %}Login - Smart Ticketing{% endblock %}
{% block content %}
<div class="row justify-content-center">
    <div class="col-md-6">
        <div class="card">
            <div class="card-body">
                <h2 class="card-title text-center mb-4"><i class="fas fa-sign-in-alt"></i> Login</h2>
                <form method="POST">
                    <div class="mb-3">
                        <label for="username" class="form-label">Username</label>
                        <input type="text" class="form-control" id="username" name="username" required>
                    </div>
                    <div class="mb-3">
                        <label for="password" class="form-label">Password</label>
                        <input type="password" class="form-control" id="password" name="password" required>
                    </div>
                    <button type="submit" class="btn btn-primary w-100">Login</button>
                </form>
                <div class="text-center mt-3">
                    <p>Don't have an account? <a href="{{ url_for('register') }}">Register here</a></p>
                </div>
            </div>
        </div>
    </div>
</div>
{% endblock %}''',

        'register.html': '''{% extends "base.html" %}
{% block title %}Register - Smart Ticketing{% endblock %}
{% block content %}
<div class="row justify-content-center">
    <div class="col-md-6">
        <div class="card">
            <div class="card-body">
                <h2 class="card-title text-center mb-4"><i class="fas fa-user-plus"></i> Register</h2>
                <form method="POST">
                    <div class="mb-3">
                        <label for="username" class="form-label">Username</label>
                        <input type="text" class="form-control" id="username" name="username" required>
                    </div>
                    <div class="mb-3">
                        <label for="email" class="form-label">Email</label>
                        <input type="email" class="form-control" id="email" name="email" required>
                    </div>
                    <div class="mb-3">
                        <label for="phone" class="form-label">Phone Number</label>
                        <input type="tel" class="form-control" id="phone" name="phone" placeholder="+250788000000" required>
                    </div>
                    <div class="mb-3">
                        <label for="password" class="form-label">Password</label>
                        <input type="password" class="form-control" id="password" name="password" required>
                    </div>
                    <button type="submit" class="btn btn-primary w-100">Register</button>
                </form>
                <div class="text-center mt-3">
                    <p>Already have an account? <a href="{{ url_for('login') }}">Login here</a></p>
                </div>
            </div>
        </div>
    </div>
</div>
{% endblock %}''',

        'dashboard.html': '''{% extends "base.html" %}
{% block title %}Dashboard - Smart Ticketing{% endblock %}
{% block content %}
<div class="row">
    <div class="col-12">
        <h1 class="mb-4"><i class="fas fa-tickets-alt"></i> My Tickets</h1>
    </div>
</div>
{% if tickets %}
<div class="row">
    {% for ticket in tickets %}
    <div class="col-md-6 col-lg-4 mb-4">
        <div class="ticket-card status-{{ ticket.payment_status }}">
            <h5>{{ ticket.event.name }}</h5>
            <p><strong>Location:</strong> {{ ticket.event.location }}</p>
            <p><strong>Date:</strong> {{ ticket.event.date.strftime('%Y-%m-%d %H:%M') }}</p>
            <p><strong>Price:</strong> {{ "{:,.0f}".format(ticket.event.price) }} RWF</p>
            <div class="status-badge mb-3">
                {% if ticket.payment_status == 'paid' %}
                    {% if ticket.is_used %}
                        <span class="badge bg-secondary">Used</span>
                    {% else %}
                        <span class="badge bg-success">Valid</span>
                    {% endif %}
                {% elif ticket.payment_status == 'pending' %}
                    <span class="badge bg-warning">Payment Pending</span>
                {% else %}
                    <span class="badge bg-danger">Payment Failed</span>
                {% endif %}
            </div>
            {% if ticket.payment_status == 'paid' %}
            <div class="qr-code-container">
                <img src="data:image/png;base64,{{ ticket.qr_image_data }}" alt="QR Code" class="img-fluid" style="max-width: 200px;">
            </div>
            {% endif %}
            <div class="d-grid">
                <a href="{{ url_for('view_ticket', ticket_id=ticket.ticket_id) }}" class="btn btn-outline-primary">View Details</a>
            </div>
        </div>
    </div>
    {% endfor %}
</div>
{% else %}
<div class="text-center">
    <i class="fas fa-ticket-alt fa-5x text-muted mb-3"></i>
    <h3>No Tickets Yet</h3>
    <p class="text-muted">Start by purchasing tickets for upcoming events!</p>
    <a href="{{ url_for('index') }}" class="btn btn-primary">Browse Events</a>
</div>
{% endif %}
{% endblock %}''',

        'admin_dashboard.html': '''{% extends "base.html" %}
{% block title %}Admin Dashboard - Smart Ticketing{% endblock %}
{% block content %}
<div class="row">
    <div class="col-12">
        <h1 class="mb-4"><i class="fas fa-tachometer-alt"></i> Admin Dashboard</h1>
    </div>
</div>
<div class="row mb-4">
    <div class="col-md-3">
        <div class="card text-white bg-primary">
            <div class="card-body">
                <h5>Total Tickets</h5>
                <h2>{{ stats.total_tickets }}</h2>
            </div>
        </div>
    </div>
    <div class="col-md-3">
        <div class="card text-white bg-success">
            <div class="card-body">
                <h5>Paid Tickets</h5>
                <h2>{{ stats.paid_tickets }}</h2>
            </div>
        </div>
    </div>
    <div class="col-md-3">
        <div class="card text-white bg-info">
            <div class="card-body">
                <h5>Used Tickets</h5>
                <h2>{{ stats.used_tickets }}</h2>
            </div>
        </div>
    </div>
    <div class="col-md-3">
        <div class="card text-white bg-warning">
            <div class="card-body">
                <h5>Revenue</h5>
                <h2>{{ "{:,.0f}".format(stats.revenue) }} RWF</h2>
            </div>
        </div>
    </div>
</div>
<div class="row">
    <div class="col-12">
        <h3>Recent Entry Logs</h3>
        <div class="table-responsive">
            <table class="table table-striped">
                <thead>
                    <tr>
                        <th>Time</th>
                        <th>Ticket ID</th>
                        <th>User</th>
                        <th>Event</th>
                        <th>Status</th>
                        <th>Device</th>
                    </tr>
                </thead>
                <tbody>
                    {% for entry in recent_entries %}
                    <tr>
                        <td>{{ entry.entry_time.strftime('%Y-%m-%d %H:%M:%S') }}</td>
                        <td>{{ entry.ticket.ticket_id if entry.ticket else 'N/A' }}</td>
                        <td>{{ entry.ticket.user.username if entry.ticket else 'Unknown' }}</td>
                        <td>{{ entry.ticket.event.name if entry.ticket else 'Unknown' }}</td>
                        <td>
                            {% if entry.status == 'granted' %}
                                <span class="badge bg-success">{{ entry.status }}</span>
                            {% else %}
                                <span class="badge bg-danger">{{ entry.status }}</span>
                            {% endif %}
                        </td>
                        <td>{{ entry.device_id }}</td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
        </div>
    </div>
</div>
{% endblock %}''',

        'manage_events.html': '''{% extends "base.html" %}
{% block title %}Manage Events - Admin{% endblock %}
{% block content %}
<div class="row">
    <div class="col-12">
        <h1 class="mb-4"><i class="fas fa-calendar-plus"></i> Manage Events</h1>
    </div>
</div>
<div class="row mb-4">
    <div class="col-12">
        <button class="btn btn-primary" data-bs-toggle="modal" data-bs-target="#addEventModal">
            <i class="fas fa-plus"></i> Add New Event
        </button>
    </div>
</div>
<div class="row">
    <div class="col-12">
        <div class="table-responsive">
            <table class="table table-striped">
                <thead>
                    <tr>
                        <th>Name</th>
                        <th>Date</th>
                        <th>Location</th>
                        <th>Price</th>
                        <th>Capacity</th>
                        <th>Tickets Sold</th>
                        <th>Status</th>
                        <th>Actions</th>
                    </tr>
                </thead>
                <tbody>
                    {% for event in events %}
                    <tr>
                        <td>{{ event.name }}</td>
                        <td>{{ event.date.strftime('%Y-%m-%d %H:%M') }}</td>
                        <td>{{ event.location }}</td>
                        <td>{{ "{:,.0f}".format(event.price) }} RWF</td>
                        <td>{{ event.max_capacity }}</td>
                        <td>{{ event.tickets|selectattr('payment_status', 'equalto', 'paid')|list|length }}</td>
                        <td>
                            {% if event.is_active %}
                                <span class="badge bg-success">Active</span>
                            {% else %}
                                <span class="badge bg-secondary">Inactive</span>
                            {% endif %}
                        </td>
                        <td>
                            <button class="btn btn-sm btn-outline-primary">Edit</button>
                            <button class="btn btn-sm btn-outline-danger">Delete</button>
                        </td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
        </div>
    </div>
</div>
<div class="modal fade" id="addEventModal" tabindex="-1">
    <div class="modal-dialog">
        <div class="modal-content">
            <div class="modal-header">
                <h5 class="modal-title">Add New Event</h5>
                <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
            </div>
            <form method="POST">
                <div class="modal-body">
                    <div class="mb-3">
                        <label for="name" class="form-label">Event Name</label>
                        <input type="text" class="form-control" id="name" name="name" required>
                    </div>
                    <div class="mb-3">
                        <label for="description" class="form-label">Description</label>
                        <textarea class="form-control" id="description" name="description" rows="3"></textarea>
                    </div>
                    <div class="mb-3">
                        <label for="date" class="form-label">Date & Time</label>
                        <input type="datetime-local" class="form-control" id="date" name="date" required>
                    </div>
                    <div class="mb-3">
                        <label for="location" class="form-label">Location</label>
                        <input type="text" class="form-control" id="location" name="location" required>
                    </div>
                    <div class="row">
                        <div class="col-md-6">
                            <div class="mb-3">
                                <label for="price" class="form-label">Price (RWF)</label>
                                <input type="number" class="form-control" id="price" name="price" min="0" required>
                            </div>
                        </div>
                        <div class="col-md-6">
                            <div class="mb-3">
                                <label for="max_capacity" class="form-label">Max Capacity</label>
                                <input type="number" class="form-control" id="max_capacity" name="max_capacity" min="1" required>
                            </div>
                        </div>
                    </div>
                </div>
                <div class="modal-footer">
                    <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
                    <button type="submit" class="btn btn-primary">Create Event</button>
                </div>
            </form>
        </div>
    </div>
</div>
{% endblock %}''',

        'manage_users.html': '''{% extends "base.html" %}
{% block title %}Manage Users - Admin{% endblock %}
{% block content %}
<div class="row">
    <div class="col-12">
        <h1 class="mb-4"><i class="fas fa-users"></i> Manage Users</h1>
    </div>
</div>
<div class="row">
    <div class="col-12">
        <div class="table-responsive">
            <table class="table table-striped">
                <thead>
                    <tr>
                        <th>ID</th>
                        <th>Username</th>
                        <th>Email</th>
                        <th>Phone</th>
                        <th>Registered</th>
                        <th>Tickets</th>
                        <th>Status</th>
                        <th>Actions</th>
                    </tr>
                </thead>
                <tbody>
                    {% for user in users %}
                    <tr>
                        <td>{{ user.id }}</td>
                        <td>{{ user.username }}</td>
                        <td>{{ user.email }}</td>
                        <td>{{ user.phone }}</td>
                        <td>{{ user.created_at.strftime('%Y-%m-%d') }}</td>
                        <td>{{ user.tickets|length }}</td>
                        <td>
                            {% if user.is_admin %}
                                <span class="badge bg-danger">Admin</span>
                            {% else %}
                                <span class="badge bg-primary">User</span>
                            {% endif %}
                        </td>
                        <td>
                            <button class="btn btn-sm btn-outline-info">View</button>
                            {% if not user.is_admin %}
                            <button class="btn btn-sm btn-outline-warning">Suspend</button>
                            {% endif %}
                        </td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
        </div>
    </div>
</div>
{% endblock %}''',

        'purchase.html': '''{% extends "base.html" %}
{% block title %}Purchase Ticket - {{ event.name }}{% endblock %}
{% block content %}
<div class="row justify-content-center">
    <div class="col-md-8">
        <div class="card">
            <div class="card-body">
                <h2 class="card-title text-center mb-4"><i class="fas fa-shopping-cart"></i> Purchase Ticket</h2>
                <div class="event-details mb-4">
                    <h4>{{ event.name }}</h4>
                    <p>{{ event.description }}</p>
                    <div class="row">
                        <div class="col-md-6">
                            <p><strong><i class="fas fa-map-marker-alt"></i> Location:</strong> {{ event.location }}</p>
                            <p><strong><i class="fas fa-calendar"></i> Date:</strong> {{ event.date.strftime('%Y-%m-%d %H:%M') }}</p>
                        </div>
                        <div class="col-md-6">
                            <p><strong><i class="fas fa-users"></i> Capacity:</strong> {{ event.max_capacity }}</p>
                            <p><strong><i class="fas fa-money-bill"></i> Price:</strong> <span class="text-success fs-4">{{ "{:,.0f}".format(event.price) }} RWF</span></p>
                        </div>
                    </div>
                </div>
                <form method="POST">
                    <div class="alert alert-info">
                        <i class="fas fa-info-circle"></i>
                        <strong>Payment Information:</strong><br>
                        Payment will be processed via mobile money from your registered phone number: {{ current_user.phone }}
                    </div>
                    <div class="d-grid">
                        <button type="submit" class="btn btn-success btn-lg">
                            <i class="fas fa-credit-card"></i> Pay {{ "{:,.0f}".format(event.price) }} RWF
                        </button>
                    </div>
                </form>
                <div class="text-center mt-3">
                    <a href="{{ url_for('index') }}" class="btn btn-outline-secondary">
                        <i class="fas fa-arrow-left"></i> Back to Events
                    </a>
                </div>
            </div>
        </div>
    </div>
</div>
{% endblock %}''',

        'ticket_detail.html': '''{% extends "base.html" %}
{% block title %}Ticket Details - {{ ticket.event.name }}{% endblock %}
{% block content %}
<div class="row justify-content-center">
    <div class="col-md-8">
        <div class="card">
            <div class="card-body text-center">
                <h2 class="card-title mb-4"><i class="fas fa-ticket-alt"></i> Digital Ticket</h2>
                <div class="ticket-info mb-4">
                    <h3>{{ ticket.event.name }}</h3>
                    <p class="text-muted">Ticket ID: {{ ticket.ticket_id }}</p>
                    <div class="row mt-3">
                        <div class="col-md-6">
                            <p><strong>Holder:</strong> {{ ticket.user.username }}</p>
                            <p><strong>Location:</strong> {{ ticket.event.location }}</p>
                            <p><strong>Date:</strong> {{ ticket.event.date.strftime('%Y-%m-%d %H:%M') }}</p>
                        </div>
                        <div class="col-md-6">
                            <p><strong>Price:</strong> {{ "{:,.0f}".format(ticket.event.price) }} RWF</p>
                            <p><strong>Status:</strong> 
                                {% if ticket.payment_status == 'paid' %}
                                    {% if ticket.is_used %}
                                        <span class="badge bg-secondary">Used on {{ ticket.used_date.strftime('%Y-%m-%d %H:%M') }}</span>
                                    {% else %}
                                        <span class="badge bg-success">Valid</span>
                                    {% endif %}
                                {% elif ticket.payment_status == 'pending' %}
                                    <span class="badge bg-warning">Payment Pending</span>
                                {% else %}
                                    <span class="badge bg-danger">Payment Failed</span>
                                {% endif %}
                            </p>
                        </div>
                    </div>
                </div>
                {% if ticket.payment_status == 'paid' %}
                <div class="qr-code-container mb-4">
                    <div class="border p-3 d-inline-block bg-white">
                        <img src="data:image/png;base64,{{ ticket.qr_image_data }}" alt="QR Code" class="img-fluid" style="max-width: 300px;">
                    </div>
                    <p class="text-muted mt-2">Present this QR code at the entrance</p>
                </div>
                {% endif %}
                <div class="d-grid gap-2 d-md-flex justify-content-md-center">
                    <a href="{{ url_for('dashboard') }}" class="btn btn-primary">
                        <i class="fas fa-arrow-left"></i> Back to Dashboard
                    </a>
                    {% if ticket.payment_status == 'paid' and not ticket.is_used %}
                    <button class="btn btn-outline-secondary" onclick="window.print()">
                        <i class="fas fa-print"></i> Print Ticket
                    </button>
                    {% endif %}
                </div>
            </div>
        </div>
    </div>
</div>
{% endblock %}'''
    }
    
    created_count = 0
    for filename, content in templates.items():
        filepath = os.path.join('templates', filename)
        if not os.path.exists(filepath):
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"✅ Created {filepath}")
            created_count += 1
        else:
            print(f"⚠️  {filepath} already exists, skipping")
    
    print(f"\n🎉 Created {created_count} template files!")
    
    if created_count > 0:
        print("\n📁 Your templates folder now contains:")
        for filename in templates.keys():
            print(f"   - templates/{filename}")
    
    print("\n🚀 You can now run: python app.py")

if __name__ == '__main__':
    print("🔧 Creating missing templates for Smart Ticketing System...")
    create_missing_templates()