from flask import Blueprint, jsonify, request
from backend.models import db, Service, Stylist, Testimonial, Offer, Booking, Message

api_bp = Blueprint('api', __name__)

# === SERVICES ===
@api_bp.route('/services', methods=['GET'])
def get_services():
    services = Service.query.all()
    result = []
    for s in services:
        result.append({
            'id': s.id,
            'title': s.title,
            'description': s.description,
            'category': s.category,
            'price': s.price,
            'duration': s.duration,
            'image': s.image,
            'isFeatured': s.is_featured,
            'is_featured': s.is_featured # Supporting both casing if needed
        })
    return jsonify(result)

@api_bp.route('/services/<int:id>', methods=['GET'])
def get_service(id):
    s = Service.query.get_or_404(id)
    return jsonify({
        'id': s.id,
        'title': s.title,
        'description': s.description,
        'category': s.category,
        'price': s.price,
        'duration': s.duration,
        'image': s.image,
        'isFeatured': s.is_featured
    })

# === STYLISTS ===
@api_bp.route('/stylists', methods=['GET'])
def get_stylists():
    stylists = Stylist.query.all()
    result = []
    for s in stylists:
        result.append({
            'id': s.id,
            'name': s.name,
            'role': s.role,
            'bio': s.bio,
            'image': s.image,
            'specialties': s.get_specialties_list()
        })
    return jsonify(result)

@api_bp.route('/stylists/<int:id>', methods=['GET'])
def get_stylist(id):
    s = Stylist.query.get_or_404(id)
    return jsonify({
        'id': s.id,
        'name': s.name,
        'role': s.role,
        'bio': s.bio,
        'image': s.image,
        'specialties': s.get_specialties_list()
    })

# === TESTIMONIALS ===
@api_bp.route('/testimonials', methods=['GET'])
def get_testimonials():
    testimonials = Testimonial.query.all()
    result = []
    for t in testimonials:
        result.append({
            'id': t.id,
            'name': t.name,
            'role': t.role,
            'content': t.content,
            'rating': t.rating,
            'avatar': t.avatar
        })
    return jsonify(result)

# === OFFERS ===
@api_bp.route('/offers', methods=['GET'])
def get_offers():
    offers = Offer.query.all()
    result = []
    for o in offers:
        result.append({
            'id': o.id,
            'title': o.title,
            'description': o.description,
            'code': o.code,
            'discount': o.discount,
            'expiry': o.expiry
        })
    return jsonify(result)

# === BOOKINGS ===
@api_bp.route('/bookings', methods=['POST'])
def create_booking():
    data = request.json
    try:
        # Basic validation (could use Marshmallow/Pydantic)
        required_fields = ['name', 'email', 'phone', 'serviceId', 'date', 'time']
        for field in required_fields:
            if field not in data:
                return jsonify({'message': f'Missing field: {field}'}), 400
        
        booking = Booking(
            name=data['name'],
            email=data['email'],
            phone=data['phone'],
            service_id=data['serviceId'],
            stylist_id=data.get('stylistId'),
            date=data['date'],
            time=data['time'],
            message=data.get('message')
        )
        db.session.add(booking)
        db.session.commit()
        
        return jsonify({
            'id': booking.id,
            'name': booking.name,
            'email': booking.email,
            'date': booking.date,
            'status': 'confirmed' # Mock status
        }), 201
    except Exception as e:
        return jsonify({'message': str(e)}), 400

# === MESSAGES ===
@api_bp.route('/messages', methods=['POST'])
def create_message():
    data = request.json
    try:
        required_fields = ['name', 'email', 'subject', 'message']
        for field in required_fields:
            if field not in data:
                return jsonify({'message': f'Missing field: {field}'}), 400

        msg = Message(
            name=data['name'],
            email=data['email'],
            subject=data['subject'],
            message=data['message']
        )
        db.session.add(msg)
        db.session.commit()
        
        return jsonify({'id': msg.id, 'status': 'sent'}), 201
    except Exception as e:
        return jsonify({'message': str(e)}), 400
