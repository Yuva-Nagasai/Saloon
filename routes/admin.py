from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import check_password_hash
from backend.models import db, User, Service, Stylist, Testimonial, Offer, Booking, Message

admin_bp = Blueprint('admin', __name__, template_folder='../templates/admin')

@admin_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('admin.dashboard'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()
        
        if user and check_password_hash(user.password_hash, password):
            login_user(user)
            return redirect(url_for('admin.dashboard'))
        else:
            flash('Invalid username or password')
            
    return render_template('login.html')

@admin_bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('admin.login'))

@admin_bp.route('/')
@admin_bp.route('/dashboard')
@login_required
def dashboard():
    stats = {
        'services': Service.query.count(),
        'stylists': Stylist.query.count(),
        'bookings': Booking.query.count(),
        'messages': Message.query.count()
    }
    return render_template('dashboard.html', stats=stats)

# === SERVICES MANAGEMENT ===
@admin_bp.route('/services')
@login_required
def services_list():
    services = Service.query.all()
    return render_template('services_list.html', services=services)

@admin_bp.route('/services/new', methods=['GET', 'POST'])
@login_required
def services_create():
    if request.method == 'POST':
        # Add simpler handling for demo purposes; real app would validate input and handle file uploads
        service = Service(
            title=request.form['title'],
            description=request.form['description'],
            category=request.form['category'],
            price=int(request.form['price']),
            duration=int(request.form['duration']),
            image=request.form['image'], # Expecting URL string for now
            is_featured=True if 'is_featured' in request.form else False
        )
        db.session.add(service)
        db.session.commit()
        flash('Service create successfully')
        return redirect(url_for('admin.services_list'))
    return render_template('services_form.html', service=None)

@admin_bp.route('/services/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def services_edit(id):
    service = Service.query.get_or_404(id)
    if request.method == 'POST':
        service.title = request.form['title']
        service.description = request.form['description']
        service.category = request.form['category']
        service.price = int(request.form['price'])
        service.duration = int(request.form['duration'])
        service.image = request.form['image']
        service.is_featured = True if 'is_featured' in request.form else False
        
        db.session.commit()
        flash('Service updated successfully')
        return redirect(url_for('admin.services_list'))
    return render_template('services_form.html', service=service)

@admin_bp.route('/services/<int:id>/delete', methods=['POST'])
@login_required
def services_delete(id):
    service = Service.query.get_or_404(id)
    db.session.delete(service)
    db.session.commit()
    flash('Service deleted')
    return redirect(url_for('admin.services_list'))

# === BOOKINGS VIEW ===
@admin_bp.route('/bookings')
@login_required
def bookings_list():
    bookings = Booking.query.order_by(Booking.created_at.desc()).all()
    return render_template('bookings_list.html', bookings=bookings)

# === MESSAGES VIEW ===
@admin_bp.route('/messages')
@login_required
def messages_list():
    messages = Message.query.order_by(Message.created_at.desc()).all()
    return render_template('messages_list.html', messages=messages)

# === STYLISTS MANAGEMENT ===
@admin_bp.route('/stylists')
@login_required
def stylists_list():
    stylists = Stylist.query.all()
    return render_template('stylists_list.html', stylists=stylists)

@admin_bp.route('/stylists/new', methods=['GET', 'POST'])
@login_required
def stylists_create():
    if request.method == 'POST':
        stylist = Stylist(
            name=request.form['name'],
            role=request.form['role'],
            bio=request.form['bio'],
            image=request.form['image'],
            specialties=request.form['specialties']
        )
        db.session.add(stylist)
        db.session.commit()
        flash('Stylist added successfully')
        return redirect(url_for('admin.stylists_list'))
    return render_template('stylists_form.html', stylist=None)

@admin_bp.route('/stylists/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def stylists_edit(id):
    stylist = Stylist.query.get_or_404(id)
    if request.method == 'POST':
        stylist.name = request.form['name']
        stylist.role = request.form['role']
        stylist.bio = request.form['bio']
        stylist.image = request.form['image']
        stylist.specialties = request.form['specialties']
        
        db.session.commit()
        flash('Stylist updated successfully')
        return redirect(url_for('admin.stylists_list'))
    return render_template('stylists_form.html', stylist=stylist)

@admin_bp.route('/stylists/<int:id>/delete', methods=['POST'])
@login_required
def stylists_delete(id):
    stylist = Stylist.query.get_or_404(id)
    db.session.delete(stylist)
    db.session.commit()
    flash('Stylist deleted')
    return redirect(url_for('admin.stylists_list'))
