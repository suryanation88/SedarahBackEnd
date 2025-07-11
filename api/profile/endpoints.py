from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from helper.db_helper import get_connection, close_connection
from helper.jwt_helper import get_user_id_from_jwt, get_role_from_jwt
from werkzeug.utils import secure_filename
import os

profile_endpoints = Blueprint('profile', __name__)
PROFILE_FOLDER = os.path.join(os.getcwd(), 'profile')
if not os.path.exists(PROFILE_FOLDER):
    os.makedirs(PROFILE_FOLDER)

# Ambil profil user yang sedang login
@profile_endpoints.route('/', methods=['GET'], strict_slashes=False)
@jwt_required()
def get_profile():
    user_id = get_user_id_from_jwt()
    if not user_id:
        return jsonify({'message': 'Unauthorized'}), 401
    connection = get_connection()
    cursor = connection.cursor(dictionary=True)
    cursor.execute("SELECT nama, domisili, golongan_darah, photo_path, no_telp, status_pendonor FROM users WHERE user_id=%s", (user_id,))
    data = cursor.fetchone()
    cursor.close()
    close_connection(connection)
    if not data:
        return jsonify({'message': 'User tidak ditemukan'}), 404
    return jsonify({'data': data, 'message': 'Success'}), 200

# Update profil user sendiri
@profile_endpoints.route('/update', methods=['POST', 'PUT'])
@jwt_required()
def update_profile():
    user_id = get_user_id_from_jwt()
    if not user_id:
        return jsonify({'message': 'Unauthorized'}), 401
    nama = request.form.get('nama')
    domisili = request.form.get('domisili')
    golongan_darah = request.form.get('golongan_darah')
    no_telp = request.form.get('no_telp')
    photo_path = None
    if 'photo' in request.files:
        photo = request.files['photo']
        if photo.filename != '':
            filename = secure_filename(photo.filename)
            photo.save(os.path.join(PROFILE_FOLDER, filename))
            photo_path = f'/profile/{filename}'
    else:
        photo_path = request.form.get('photo_path')
    update_fields = []
    update_values = []
    if nama:
        update_fields.append('nama = %s')
        update_values.append(nama)
    if domisili:
        update_fields.append('domisili = %s')
        update_values.append(domisili)
    if golongan_darah:
        update_fields.append('golongan_darah = %s')
        update_values.append(golongan_darah)
    if no_telp:
        update_fields.append('no_telp = %s')
        update_values.append(no_telp)
    if photo_path:
        update_fields.append('photo_path = %s')
        update_values.append(photo_path)
    if not update_fields:
        return jsonify({'message': 'Tidak ada data yang diupdate'}), 400
    update_values.append(user_id)
    connection = get_connection()
    cursor = connection.cursor()
    update_query = f"UPDATE users SET {', '.join(update_fields)} WHERE user_id = %s"
    cursor.execute(update_query, update_values)
    connection.commit()
    cursor.close()
    close_connection(connection)
    return jsonify({'message': 'Profile berhasil diupdate'}), 200

# Admin: update status_pendonor user tertentu
@profile_endpoints.route('/update_status/<int:user_id>', methods=['PUT'])
@jwt_required()
def update_status_pendonor(user_id):
    role = get_role_from_jwt()
    if role != 'admin':
        return jsonify({'message': 'Unauthorized'}), 403
    status_pendonor = request.json.get('status_pendonor')
    if not status_pendonor:
        return jsonify({'message': 'status_pendonor wajib diisi'}), 400
    connection = get_connection()
    cursor = connection.cursor()
    update_query = "UPDATE users SET status_pendonor = %s WHERE user_id = %s"
    cursor.execute(update_query, (status_pendonor, user_id))
    connection.commit()
    cursor.close()
    close_connection(connection)
    return jsonify({'message': 'Status pendonor berhasil diupdate'}), 200

# Admin: get user by id
@profile_endpoints.route('/<int:user_id>', methods=['GET'])
@jwt_required()
def get_user_by_id(user_id):
    role = get_role_from_jwt()
    if role != 'admin':
        return jsonify({'message': 'Unauthorized'}), 403
    connection = get_connection()
    cursor = connection.cursor(dictionary=True)
    cursor.execute("SELECT nama, domisili, golongan_darah, photo_path, no_telp, status_pendonor FROM users WHERE user_id=%s", (user_id,))
    data = cursor.fetchone()
    cursor.close()
    close_connection(connection)
    if not data:
        return jsonify({'message': 'User tidak ditemukan'}), 404
    return jsonify({'data': data, 'message': 'Success'}), 200

# Admin: get semua user
@profile_endpoints.route('/all', methods=['GET'])
@jwt_required()
def get_all_users():
    role = get_role_from_jwt()
    if role != 'admin':
        return jsonify({'message': 'Unauthorized'}), 403
    connection = get_connection()
    cursor = connection.cursor(dictionary=True)
    cursor.execute("SELECT nama, domisili, golongan_darah, photo_path, no_telp, status_pendonor, user_id FROM users")
    data = cursor.fetchall()
    cursor.close()
    close_connection(connection)
    return jsonify({'data': data, 'message': 'Success'}), 200
