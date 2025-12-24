import os
from flask import Flask, jsonify, request, redirect, url_for, flash, render_template_string, send_file
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, LoginManager, login_user, logout_user, login_required, current_user
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from sqlalchemy.sql import func
from jinja2 import DictLoader

# ==========================================
# CONFIGURATION & SETUP
# ==========================================
app = Flask(__name__)
# Enable CORS for all routes to allow frontend to communicate from any origin (e.g. local file)
CORS(app)

@app.route('/')
def home():
    client_url = app.config.get('CLIENT_URL')
    if client_url:
        return redirect(client_url)
    return redirect(url_for('login'))

# Database Configuration
# Default to local MySQL, compatible with previous setup
# URI format: sqlite:///salon.db (No password needed for demo)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL') or 'sqlite:///salon.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'dev-secret-key-salon-chic-single-file'
app.config['CLIENT_URL'] = os.environ.get('CLIENT_URL')

db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.login_view = 'login'
login_manager.init_app(app)

# ==========================================
# DATABASE MODELS
# ==========================================
class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)

class Service(db.Model):
    __tablename__ = 'services'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Integer, nullable=False) # stored in cents
    duration = db.Column(db.Integer, nullable=False) # in minutes
    image = db.Column(db.String(512), nullable=False)
    is_featured = db.Column(db.Boolean, default=False)

class Stylist(db.Model):
    __tablename__ = 'stylists'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(100), nullable=False)
    bio = db.Column(db.Text, nullable=False)
    image = db.Column(db.String(512), nullable=False)
    specialties = db.Column(db.Text) 

    def get_specialties_list(self):
        if self.specialties:
            return self.specialties.split(',')
        return []

class Testimonial(db.Model):
    __tablename__ = 'testimonials'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(100))
    content = db.Column(db.Text, nullable=False)
    rating = db.Column(db.Integer, nullable=False)
    avatar = db.Column(db.String(512))

class Offer(db.Model):
    __tablename__ = 'offers'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=False)
    code = db.Column(db.String(50))
    discount = db.Column(db.String(50), nullable=False)
    expiry = db.Column(db.String(50))

class Booking(db.Model):
    __tablename__ = 'bookings'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(255), nullable=False)
    phone = db.Column(db.String(50), nullable=False)
    service_id = db.Column(db.Integer, db.ForeignKey('services.id'), nullable=False)
    stylist_id = db.Column(db.Integer, db.ForeignKey('stylists.id'))
    date = db.Column(db.String(50), nullable=False)
    time = db.Column(db.String(50), nullable=False)
    message = db.Column(db.Text)
    created_at = db.Column(db.DateTime(timezone=True), server_default=func.now())
    
    service = db.relationship('Service')
    stylist = db.relationship('Stylist')

class Message(db.Model):
    __tablename__ = 'messages'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(255), nullable=False)
    subject = db.Column(db.String(255), nullable=False)
    message = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), server_default=func.now())

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# ==========================================
# ADMIN TEMPLATES (EMBEDDED)
# ==========================================

TPL_BASE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Salon Chic Admin</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.1/font/bootstrap-icons.css">
    <style>
        :root {
            --sidebar-bg: #121212;
            --sidebar-text: #a0a0a0;
            --sidebar-active: #ffffff;
            --accent-color: #d4af37; /* Gold */
            --bg-color: #f4f5f7;
        }
        body { font-family: 'Outfit', sans-serif; background-color: var(--bg-color); color: #333; }
        
        /* Sidebar */
        .sidebar { position: fixed; top: 0; bottom: 0; left: 0; z-index: 100; padding: 0; background: var(--sidebar-bg); width: 260px; transition: all 0.3s; }
        .sidebar-brand { height: 70px; display: flex; align-items: center; padding: 0 1.5rem; color: white; font-size: 1.25rem; font-weight: 600; letter-spacing: 1px; border-bottom: 1px solid rgba(255,255,255,0.1); }
        .sidebar-brand i { color: var(--accent-color); margin-right: 10px; }
        
        .nav-link { color: var(--sidebar-text); padding: 1rem 1.5rem; font-weight: 400; display: flex; align-items: center; gap: 12px; transition: all 0.2s; border-left: 3px solid transparent; }
        .nav-link:hover { color: white; background: rgba(255,255,255,0.03); }
        .nav-link.active { color: var(--sidebar-active); background: rgba(212, 175, 55, 0.1); border-left-color: var(--accent-color); }
        .nav-link i { font-size: 1.1rem; }
        
        /* Top Navbar */
        .navbar { margin-left: 260px; background: white; height: 70px; padding: 0 2rem; box-shadow: 0 2px 4px rgba(0,0,0,0.02); display: flex; justify-content: flex-end; align-items: center; }
        .user-menu a { text-decoration: none; color: #333; font-weight: 500; font-size: 0.9rem; }
        
        /* Main Content */
        main { margin-left: 260px; padding: 2.5rem; }
        .page-header { margin-bottom: 2.5rem; display: flex; justify-content: space-between; align-items: center; }
        .page-title { font-size: 1.75rem; font-weight: 600; color: #1a1a1a; margin: 0; }
        
        /* Cards */
        .card { border: none; border-radius: 16px; box-shadow: 0 4px 20px rgba(0,0,0,0.03); background: white; transition: transform 0.2s; }
        .stat-card .card-body { padding: 1.5rem; }
        .stat-value { font-size: 2.2rem; font-weight: 600; margin-bottom: 0.2rem; color: #1a1a1a; }
        .stat-label { color: #888; font-size: 0.85rem; font-weight: 500; text-transform: uppercase; letter-spacing: 0.5px; }
        .stat-icon { font-size: 2.5rem; opacity: 1; color: var(--accent-color); background: rgba(212, 175, 55, 0.1); width: 60px; height: 60px; display:flex; align-items:center; justify-content:center; border-radius: 12px; }
        
        /* Tables */
        .table-custom { background: white; border-radius: 16px; overflow: hidden; box-shadow: 0 4px 20px rgba(0,0,0,0.03); padding: 0.5rem; }
        .table { margin-bottom: 0; }
        .table thead th { background: transparent; border-bottom: 1px solid #eee; font-weight: 600; text-transform: uppercase; font-size: 0.75rem; letter-spacing: 0.5px; color: #888; padding: 1.25rem 1.5rem; }
        .table tbody td { padding: 1.25rem 1.5rem; vertical-align: middle; color: #444; border-bottom: 1px solid #f8f8f8; font-size: 0.95rem; }
        .table tbody tr:last-child td { border-bottom: none; }
        
        /* Buttons */
        .btn-primary { background: #1a1a1a; border: none; padding: 0.6rem 1.5rem; border-radius: 10px; font-weight: 500; transition: all 0.2s; }
        .btn-primary:hover { background: var(--accent-color); color: #000; transform: translateY(-1px); }
        .btn-outline-secondary { border-color: #ddd; color: #666; border-radius: 8px; }
        .btn-outline-secondary:hover { background: #f8f8f8; color: #333; border-color: #ccc; }
        .badge { font-weight: 500; padding: 0.5em 0.8em; letter-spacing: 0.3px; }

        /* Forms */
        .form-control, .form-select { padding: 0.75rem 1rem; border-radius: 10px; border: 1px solid #e0e0e0; background: #fcfcfc; }
        .form-control:focus { border-color: var(--accent-color); box-shadow: 0 0 0 3px rgba(212, 175, 55, 0.1); background: white; }
        
        @media (max-width: 768px) {
            .sidebar { transform: translateX(-100%); width: 260px; }
            .navbar, main { margin-left: 0; }
            .sidebar.active { transform: translateX(0); }
        }
    </style>
</head>
<body>
    <!-- Sidebar -->
    <nav class="sidebar">
        <div class="sidebar-brand">
            <i class="bi bi-scissors"></i> SALON CHIC
        </div>
        <ul class="nav flex-column mt-4">
            <li class="nav-item">
                <a class="nav-link {{ 'active' if request.endpoint == 'dashboard' else '' }}" href="{{ url_for('dashboard') }}">
                    <i class="bi bi-grid-fill"></i> Dashboard
                </a>
            </li>
            <li class="nav-item">
                <a class="nav-link {{ 'active' if 'bookings' in request.endpoint else '' }}" href="{{ url_for('bookings_list') }}">
                    <i class="bi bi-calendar2-check-fill"></i> Bookings
                </a>
            </li>
            <li class="nav-item">
                <a class="nav-link {{ 'active' if 'services' in request.endpoint else '' }}" href="{{ url_for('services_list') }}">
                    <i class="bi bi-stars"></i> Services
                </a>
            </li>
             <li class="nav-item">
                <a class="nav-link {{ 'active' if 'stylists' in request.endpoint else '' }}" href="{{ url_for('stylists_list') }}">
                    <i class="bi bi-people-fill"></i> Stylists
                </a>
            </li>
            <li class="nav-item">
                <a class="nav-link {{ 'active' if 'messages' in request.endpoint else '' }}" href="{{ url_for('messages_list') }}">
                    <i class="bi bi-chat-right-text-fill"></i> Messages
                </a>
            </li>
        </ul>
    </nav>

    <!-- Top Header -->
    <nav class="navbar">
        <div class="user-menu">
            <a href="{{ url_for('logout') }}"><i class="bi bi-box-arrow-right me-2"></i>Sign Out</a>
        </div>
    </nav>

    <!-- Main Content -->
    <main>
        {% with messages = get_flashed_messages() %}
          {% if messages %}
            <div class="alert alert-info shadow-sm border-0 rounded-3 mb-4">
              {% for message in messages %}
                <div><i class="bi bi-info-circle me-2"></i>{{ message }}</div>
              {% endfor %}
            </div>
          {% endif %}
        {% endwith %}

        {% block content %}{% endblock %}
    </main>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>
"""

TPL_LOGIN = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Login - Salon Chic Admin</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&display=swap" rel="stylesheet">
    <style>
        body { font-family: 'Inter', sans-serif; display: flex; align-items: center; justify-content: center; height: 100vh; background: #f0f2f5; }
        .login-card { width: 100%; max-width: 400px; padding: 2.5rem; border-radius: 16px; background: white; box-shadow: 0 10px 40px rgba(0,0,0,0.08); }
        .login-header { text-align: center; margin-bottom: 2rem; }
        .login-header h1 { font-size: 1.5rem; font-weight: 700; color: #1a1a1a; margin-bottom: 0.5rem; }
        .login-header p { color: #6c757d; font-size: 0.9rem; }
        .form-control { padding: 0.75rem 1rem; border-radius: 8px; margin-bottom: 1rem; }
        .btn-primary { width: 100%; padding: 0.75rem; font-weight: 600; border-radius: 8px; background: #000; border: none; }
        .btn-primary:hover { background: #333; }
    </style>
</head>
<body>
    <div class="login-card">
        <div class="login-header">
            <h1>Welcome Back</h1>
            <p>Sign in to Salon Chic Admin</p>
        </div>
        <form method="POST">
            {% with messages = get_flashed_messages() %}
                {% if messages %}
                    <div class="alert alert-danger py-2 fs-6">{{ messages[0] }}</div>
                {% endif %}
            {% endwith %}
            <div class="mb-3">
                <input type="text" name="username" class="form-control" placeholder="Username" required autofocus>
            </div>
            <div class="mb-3">
                <input type="password" name="password" class="form-control" placeholder="Password" required>
            </div>
            <button class="btn btn-lg btn-primary" type="submit">Sign in</button>
        </form>
        {% if client_url %}
        <a href="{{ client_url }}" class="btn btn-outline-secondary w-100 mt-3" style="border: 1px solid #ddd; padding: 0.75rem;">Back to Website</a>
        {% endif %}
        <p class="text-center mt-4 text-muted small">&copy; 2025 Salon Chic</p>
    </div>
</body>
</html>
"""

TPL_DASHBOARD = """
{% extends "base.html" %}
{% block content %}
<div class="page-header">
    <h1 class="page-title">Dashboard Overview</h1>
    <span class="text-muted">{{ now }}</span>
</div>
<div class="row g-4">
    <div class="col-md-3">
        <div class="card stat-card h-100">
            <div class="card-body d-flex justify-content-between align-items-center">
                <div>
                    <h5 class="stat-value">{{ stats.bookings }}</h5>
                    <p class="stat-label">Total Bookings</p>
                </div>
                <div class="stat-icon"><i class="bi bi-calendar-check"></i></div>
            </div>
        </div>
    </div>
    <div class="col-md-3">
        <div class="card stat-card h-100">
            <div class="card-body d-flex justify-content-between align-items-center">
                <div>
                    <h5 class="stat-value">{{ stats.services }}</h5>
                    <p class="stat-label">Active Services</p>
                </div>
                <div class="stat-icon"><i class="bi bi-stars"></i></div>
            </div>
        </div>
    </div>
    <div class="col-md-3">
        <div class="card stat-card h-100">
            <div class="card-body d-flex justify-content-between align-items-center">
                <div>
                    <h5 class="stat-value">{{ stats.stylists }}</h5>
                    <p class="stat-label">Team Members</p>
                </div>
                <div class="stat-icon"><i class="bi bi-people"></i></div>
            </div>
        </div>
    </div>
    <div class="col-md-3">
        <div class="card stat-card h-100">
            <div class="card-body d-flex justify-content-between align-items-center">
                <div>
                    <h5 class="stat-value">{{ stats.messages }}</h5>
                    <p class="stat-label">New Messages</p>
                </div>
                <div class="stat-icon"><i class="bi bi-envelope"></i></div>
            </div>
        </div>
    </div>
</div>
{% endblock %}
"""

TPL_SERVICES = """
{% extends "base.html" %}
{% block content %}
<div class="page-header">
    <h1 class="page-title">Services</h1>
    <a href="{{ url_for('services_create') }}" class="btn btn-primary"><i class="bi bi-plus-lg"></i> New Service</a>
</div>
<div class="table-responsive table-custom">
    <table class="table table-hover mb-0">
        <thead>
            <tr>
                <th width="50">ID</th>
                <th>Service Name</th>
                <th>Category</th>
                <th>Price</th>
                <th>Duration</th>
                <th class="text-end">Actions</th>
            </tr>
        </thead>
        <tbody>
        {% for service in services %}
        <tr>
            <td><span class="text-muted">#{{ service.id }}</span></td>
            <td>
                <div class="d-flex align-items-center">
                    {% if service.image %}<img src="{{ service.image }}" style="width:40px;height:40px;border-radius:6px;object-fit:cover;margin-right:12px">{% endif %}
                    <div>
                        <div class="fw-bold">{{ service.title }}</div>
                        {% if service.is_featured %}<span class="badge bg-warning text-dark" style="font-size:10px">FEATURED</span>{% endif %}
                    </div>
                </div>
            </td>
            <td><span class="badge bg-light text-dark border">{{ service.category }}</span></td>
            <td class="fw-bold">₹{{ "%.2f"|format(service.price / 100) }}</td>
            <td>{{ service.duration }} min</td>
            <td class="text-end">
                <a href="{{ url_for('services_edit', id=service.id) }}" class="btn btn-sm btn-outline-secondary me-1"><i class="bi bi-pencil"></i></a>
                <form action="{{ url_for('services_delete', id=service.id) }}" method="POST" style="display:inline" onsubmit="return confirm('Are you sure you want to delete this service?');">
                    <button type="submit" class="btn btn-sm btn-outline-danger"><i class="bi bi-trash"></i></button>
                </form>
            </td>
        </tr>
        {% endfor %}
        </tbody>
    </table>
</div>
{% endblock %}
"""

TPL_SERVICE_FORM = """
{% extends "base.html" %}
{% block content %}
<div class="row justify-content-center">
    <div class="col-lg-8">
        <div class="page-header">
            <h1 class="page-title">{{ 'Edit' if service else 'New' }} Service</h1>
            <a href="{{ url_for('services_list') }}" class="btn btn-outline-secondary">Back to List</a>
        </div>
        <div class="card p-4">
            <form method="POST">
                <div class="mb-4">
                    <label class="form-label fw-bold small text-uppercase text-muted">Service Details</label>
                    <div class="mb-3">
                        <label class="form-label">Service Title</label>
                        <input type="text" class="form-control" name="title" value="{{ service.title if service else '' }}" required placeholder="e.g. Luxury Hair Spa">
                    </div>
                    <div class="mb-3">
                        <label class="form-label">Description</label>
                        <textarea class="form-control" name="description" rows="3" required>{{ service.description if service else '' }}</textarea>
                    </div>
                </div>
                
                <div class="row mb-4">
                     <div class="col-md-6 mb-3">
                        <label class="form-label">Category</label>
                        <select class="form-select" name="category" required>
                            <option value="">Select Category</option>
                            {% for cat in ['Hair', 'Skin', 'Nails', 'Massage', 'Bridal'] %}
                            <option value="{{ cat }}" {{ 'selected' if service and service.category == cat else '' }}>{{ cat }}</option>
                            {% endfor %}
                        </select>
                    </div>
                    <div class="col-md-3 mb-3">
                        <label class="form-label">Price (Rupees)</label>
                        <div class="input-group">
                            <span class="input-group-text">₹</span>
                            <input type="number" step="0.01" class="form-control" name="price" value="{{ '%.2f'|format(service.price / 100) if service else '' }}" required help="Enter in Rupees (e.g. 50.00)">
                        </div>
                    </div>
                    <div class="col-md-3 mb-3">
                        <label class="form-label">Duration</label>
                        <div class="input-group">
                            <input type="number" class="form-control" name="duration" value="{{ service.duration if service else '' }}" required>
                            <span class="input-group-text">min</span>
                        </div>
                    </div>
                </div>

                <div class="mb-4">
                    <label class="form-label">Image URL</label>
                    <input type="text" class="form-control" name="image" value="{{ service.image if service else '' }}" required placeholder="https://...">
                     {% if service and service.image %}
                        <div class="mt-2"><img src="{{ service.image }}" height="100" class="rounded"></div>
                    {% endif %}
                </div>

                <div class="mb-4 form-check form-switch">
                    <input type="checkbox" class="form-check-input" name="is_featured" role="switch" id="feat" {{ 'checked' if service and service.is_featured else '' }}>
                    <label class="form-check-label" for="feat">Feature this on homepage?</label>
                </div>

                <div class="d-grid gap-2">
                    <button type="submit" class="btn btn-primary btn-lg">Save Service</button>
                </div>
            </form>
        </div>
    </div>
</div>
{% endblock %}
"""

TPL_STYLISTS = """
{% extends "base.html" %}
{% block content %}
<div class="page-header">
    <h1 class="page-title">Stylists</h1>
    <a href="{{ url_for('stylists_create') }}" class="btn btn-primary"><i class="bi bi-plus-lg"></i> New Stylist</a>
</div>
<div class="row g-4">
    {% for s in stylists %}
    <div class="col-md-4 col-lg-3">
        <div class="card h-100 text-center p-3">
            <div class="mx-auto mb-3" style="width:80px;height:80px;border-radius:50%;overflow:hidden;">
                <img src="{{ s.image }}" style="width:100%;height:100%;object-fit:cover;">
            </div>
            <h5 class="mb-1">{{ s.name }}</h5>
            <p class="text-muted small mb-2">{{ s.role }}</p>
            <div class="mb-3">
                 {% for spec in s.get_specialties_list() %}
                    <span class="badge bg-light text-dark border">{{ spec }}</span>
                 {% endfor %}
            </div>
            <div class="mt-auto">
                 <a href="{{ url_for('stylists_edit', id=s.id) }}" class="btn btn-sm btn-outline-secondary w-100 mb-2">Edit Profile</a>
                 <form action="{{ url_for('stylists_delete', id=s.id) }}" method="POST" onsubmit="return confirm('Remove this stylist?');">
                    <button type="submit" class="btn btn-sm btn-outline-danger w-100">Remove</button>
                </form>
            </div>
        </div>
    </div>
    {% endfor %}
</div>
{% endblock %}
"""

TPL_STYLIST_FORM = """
{% extends "base.html" %}
{% block content %}
<div class="row justify-content-center">
    <div class="col-lg-6">
        <div class="page-header">
            <h1 class="page-title">{{ 'Edit' if stylist else 'Add' }} Stylist</h1>
            <a href="{{ url_for('stylists_list') }}" class="btn btn-outline-secondary">Back</a>
        </div>
        <div class="card p-4">
            <form method="POST">
                <div class="text-center mb-4">
                    <div style="width:100px;height:100px;background:#f0f0f0;border-radius:50%;margin:auto;display:flex;align-items:center;justify-content:center;overflow:hidden">
                        {% if stylist and stylist.image %}
                            <img src="{{ stylist.image }}" style="width:100%;height:100%;object-fit:cover">
                        {% else %}
                            <i class="bi bi-person text-muted" style="font-size:2rem"></i>
                        {% endif %}
                    </div>
                </div>
                <div class="row">
                    <div class="col-md-6 mb-3">
                        <label class="form-label">Full Name</label>
                        <input type="text" class="form-control" name="name" value="{{ stylist.name if stylist else '' }}" required>
                    </div>
                    <div class="col-md-6 mb-3">
                        <label class="form-label">Role / Title</label>
                        <input type="text" class="form-control" name="role" value="{{ stylist.role if stylist else '' }}" required placeholder="e.g. Senior Stylist">
                    </div>
                </div>
                <div class="mb-3">
                    <label class="form-label">Bio</label>
                    <textarea class="form-control" name="bio" rows="3" required>{{ stylist.bio if stylist else '' }}</textarea>
                </div>
                <div class="mb-3">
                    <label class="form-label">Profile Image URL</label>
                    <input type="text" class="form-control" name="image" value="{{ stylist.image if stylist else '' }}" required>
                </div>
                <div class="mb-4">
                    <label class="form-label">Specialties</label>
                    <input type="text" class="form-control" name="specialties" value="{{ stylist.specialties if stylist else '' }}" placeholder="Hair, Color, Spa (comma separated)">
                </div>
                <button type="submit" class="btn btn-primary w-100">Save Stylist</button>
            </form>
        </div>
    </div>
</div>
{% endblock %}
"""

TPL_BOOKINGS = """
{% extends "base.html" %}
{% block content %}
<div class="page-header">
    <h1 class="page-title">Appointment Bookings</h1>
    <button class="btn btn-outline-primary" onclick="window.print()"><i class="bi bi-printer"></i> Print</button>
</div>
<div class="table-responsive table-custom">
    <table class="table table-hover mb-0">
        <thead>
            <tr>
                <th>Status</th>
                <th>Client</th>
                <th>Service</th>
                <th>Appointment Time</th>
                <th>Contact</th>
                <th>Booked On</th>
            </tr>
        </thead>
        <tbody>
        {% for b in bookings %}
        <tr>
            <td><span class="badge bg-success bg-opacity-10 text-success rounded-pill px-3">CONFIRMED</span></td>
            <td>
                <div class="fw-bold">{{ b.name }}</div>
                <div class="small text-muted">{{ b.email }}</div>
            </td>
            <td>
                {% if b.service %}
                    <span class="fw-medium">{{ b.service.title }}</span>
                {% else %}
                    <span class="text-danger">Deleted Service (ID: {{ b.service_id }})</span>
                {% endif %}
                {% if b.stylist %}
                    <div class="small text-muted">with {{ b.stylist.name }}</div>
                {% endif %}
            </td>
            <td>
                <div class="fw-bold"><i class="bi bi-clock me-1"></i>{{ b.time }}</div>
                <div class="small">{{ b.date }}</div>
            </td>
            <td>{{ b.phone }}</td>
            <td class="small text-muted">{{ b.created_at.strftime('%Y-%m-%d') }}</td>
        </tr>
        {% endfor %}
        </tbody>
    </table>
</div>
{% endblock %}
"""

TPL_MESSAGES = """
{% extends "base.html" %}
{% block content %}
<div class="page-header">
    <h1 class="page-title">Inbox</h1>
</div>
<div class="row g-3">
    {% for m in messages %}
    <div class="col-12">
        <div class="card p-3 d-flex flex-row align-items-start gap-3">
            <div class="bg-light rounded-circle d-flex align-items-center justify-content-center flex-shrink-0" style="width:48px;height:48px;font-weight:bold;color:#555">
                {{ m.name[0] | upper }}
            </div>
            <div class="flex-grow-1">
                <div class="d-flex justify-content-between">
                    <div>
                        <h6 class="mb-0 fw-bold">{{ m.subject }}</h6>
                        <span class="small text-muted">From: {{ m.name }} &lt;{{ m.email }}&gt;</span>
                    </div>
                    <small class="text-muted">{{ m.created_at.strftime('%b %d, %I:%M %p') }}</small>
                </div>
                <p class="mt-2 mb-0 text-secondary bg-light p-2 rounded" style="font-size:0.95rem">{{ m.message }}</p>
            </div>
        </div>
    </div>
    {% endfor %}
</div>
{% endblock %}
"""

# ==========================================
# ROUTES: ADMIN
# ==========================================
# Session Configuration
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
app.config['SESSION_COOKIE_SECURE'] = False

@app.route('/admin/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated: return redirect(url_for('dashboard'))
    if request.method == 'POST':
        user = User.query.filter_by(username=request.form.get('username')).first()
        if user and check_password_hash(user.password_hash, request.form.get('password')):
            login_user(user)
            return redirect(url_for('dashboard'))
        flash('Invalid credentials')
    return render_template_string(TPL_LOGIN, client_url=app.config['CLIENT_URL'])

@app.route('/admin/logout')
@login_required
def logout():
    logout_user()
    client_url = app.config.get('CLIENT_URL')
    if client_url:
        return redirect(client_url)
    return redirect(url_for('login'))

@app.route('/admin')
@app.route('/admin/dashboard')
@login_required
def dashboard():
    stats = { 'services': Service.query.count(), 'stylists': Stylist.query.count(), 
              'bookings': Booking.query.count(), 'messages': Message.query.count() }
    return render_template_string(TPL_DASHBOARD, stats=stats)

# Services CRUD
@app.route('/admin/services')
@login_required
def services_list(): return render_template_string(TPL_SERVICES, services=Service.query.all())

@app.route('/admin/services/new', methods=['GET', 'POST'])
@login_required
def services_create():
    if request.method == 'POST':
        s = Service(title=request.form['title'], description=request.form['description'], category=request.form['category'],
                    price=int(float(request.form['price']) * 100), duration=int(request.form['duration']), image=request.form['image'],
                    is_featured='is_featured' in request.form)
        db.session.add(s); db.session.commit()
        return redirect(url_for('services_list'))
    return render_template_string(TPL_SERVICE_FORM, service=None)

@app.route('/admin/services/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def services_edit(id):
    s = Service.query.get_or_404(id)
    if request.method == 'POST':
        s.title = request.form['title']; s.description = request.form['description']; s.category = request.form['category']
        s.price = int(float(request.form['price']) * 100); s.duration = int(request.form['duration']); s.image = request.form['image']
        s.is_featured = 'is_featured' in request.form
        db.session.commit()
        return redirect(url_for('services_list'))
    return render_template_string(TPL_SERVICE_FORM, service=s)

@app.route('/admin/services/<int:id>/delete', methods=['POST'])
@login_required
def services_delete(id): db.session.delete(Service.query.get_or_404(id)); db.session.commit(); return redirect(url_for('services_list'))

# Stylists CRUD
@app.route('/admin/stylists')
@login_required
def stylists_list(): return render_template_string(TPL_STYLISTS, stylists=Stylist.query.all())

@app.route('/admin/stylists/new', methods=['GET', 'POST'])
@login_required
def stylists_create():
    if request.method == 'POST':
        s = Stylist(name=request.form['name'], role=request.form['role'], bio=request.form['bio'], 
                    image=request.form['image'], specialties=request.form['specialties'])
        db.session.add(s); db.session.commit()
        return redirect(url_for('stylists_list'))
    return render_template_string(TPL_STYLIST_FORM, stylist=None)

@app.route('/admin/stylists/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def stylists_edit(id):
    s = Stylist.query.get_or_404(id)
    if request.method == 'POST':
        s.name = request.form['name']; s.role = request.form['role']; s.bio = request.form['bio']
        s.image = request.form['image']; s.specialties = request.form['specialties']
        db.session.commit()
        return redirect(url_for('stylists_list'))
    return render_template_string(TPL_STYLIST_FORM, stylist=s)

@app.route('/admin/stylists/<int:id>/delete', methods=['POST'])
@login_required
def stylists_delete(id): db.session.delete(Stylist.query.get_or_404(id)); db.session.commit(); return redirect(url_for('stylists_list'))

# Listings
@app.route('/admin/bookings')
@login_required
def bookings_list(): return render_template_string(TPL_BOOKINGS, bookings=Booking.query.order_by(Booking.created_at.desc()).all())

@app.route('/admin/messages')
@login_required
def messages_list(): return render_template_string(TPL_MESSAGES, messages=Message.query.order_by(Message.created_at.desc()).all())

# ==========================================
# ROUTES: PUBLIC API
# ==========================================
@app.route('/api/services', methods=['GET'])
def api_services(): return jsonify([{
    'id':s.id, 'title':s.title, 'description':s.description, 'category':s.category, 
    'price':s.price, 'duration':s.duration, 'image':s.image, 'isFeatured':s.is_featured
} for s in Service.query.all()])

@app.route('/api/services/<int:id>', methods=['GET'])
def api_service(id):
    s = Service.query.get_or_404(id)
    return jsonify({'id':s.id, 'title':s.title, 'description':s.description, 'category':s.category, 'price':s.price, 'image':s.image})

@app.route('/api/stylists', methods=['GET'])
def api_stylists(): return jsonify([{
    'id':s.id, 'name':s.name, 'role':s.role, 'bio':s.bio, 'image':s.image, 'specialties':s.get_specialties_list()
} for s in Stylist.query.all()])

@app.route('/api/bookings', methods=['POST'])
def api_create_booking():
    data = request.json
    try:
        b = Booking(name=data['name'], email=data['email'], phone=data['phone'], service_id=data['serviceId'],
                    stylist_id=data.get('stylistId'), date=data['date'], time=data['time'], message=data.get('message'))
        db.session.add(b); db.session.commit()
        return jsonify({'id': b.id, 'status': 'confirmed'}), 201
    except Exception as e: return jsonify({'message': str(e)}), 400

@app.route('/api/messages', methods=['POST'])
def api_create_message():
    data = request.json
    try:
        m = Message(name=data['name'], email=data['email'], subject=data['subject'], message=data['message'])
        db.session.add(m); db.session.commit()
        return jsonify({'id': m.id, 'status': 'sent'}), 201
    except Exception as e: return jsonify({'message': str(e)}), 400

# ==========================================
# TEMPLATE HELPERS
# ==========================================
# Helper to resolve "extends" blocks via DictLoader
app.jinja_loader = DictLoader({
    'base.html': TPL_BASE,
    'login.html': TPL_LOGIN,
    'dashboard.html': TPL_DASHBOARD,
    'services_list.html': TPL_SERVICES,
    'services_form.html': TPL_SERVICE_FORM,
    'stylists_list.html': TPL_STYLISTS,
    'stylists_form.html': TPL_STYLIST_FORM,
    'bookings_list.html': TPL_BOOKINGS,
    'messages_list.html': TPL_MESSAGES
})

# ==========================================
# SEED DATA
# ==========================================
def seed_data():
    if not Service.query.first():
        services = [
            Service(title="Classic Haircut", description="Expert cut and style tailored to you.", category="Hair", price=4500, duration=45, image="https://images.unsplash.com/photo-1560066984-138dadb4c035?auto=format&fit=crop&w=500&q=60", is_featured=True),
            Service(title="Rejuvenating Facial", description="Deep cleanse and hydration.", category="Skin", price=7500, duration=60, image="https://images.unsplash.com/photo-1570172619644-dfd03ed5d881?auto=format&fit=crop&w=500&q=60", is_featured=True),
            Service(title="Gel Manicure", description="Long-lasting polish and care.", category="Nails", price=3500, duration=40, image="https://images.unsplash.com/photo-1604654894610-df63bc536371?auto=format&fit=crop&w=500&q=60", is_featured=False)
        ]
        db.session.add_all(services)
        print("Seeded Services")

    if not Stylist.query.first():
        stylists = [
            Stylist(name="Elena Ross", role="Senior Stylist", bio="Expert in modern cuts.", image="https://images.unsplash.com/photo-1580618672591-eb180b1a973f?auto=format&fit=crop&w=500&q=60", specialties="Hair,Color"),
            Stylist(name="Marco Diaz", role="Color Specialist", bio="Vibrant colors expert.", image="https://images.unsplash.com/photo-1542596594-649edbc13630?auto=format&fit=crop&w=500&q=60", specialties="Color,Highlights")
        ]
        db.session.add_all(stylists)
        print("Seeded Stylists")
    
    db.session.commit()

def init_db():
    with app.app_context():
        db.create_all()
        if not User.query.filter_by(username='admin').first():
            db.session.add(User(username='admin', password_hash=generate_password_hash('admin123')))
            db.session.commit()
            print("Admin user created.")
        seed_data() # Add demo data

if __name__ == '__main__':
    init_db()
    app.run(debug=True, port=5001, host='0.0.0.0')
