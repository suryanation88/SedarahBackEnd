from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from helper.db_helper import get_connection, close_connection
from helper.jwt_helper import get_user_id_from_jwt, get_role_from_jwt

komentar_endpoints = Blueprint('komentar', __name__)

@komentar_endpoints.route('/', methods=['GET'], strict_slashes=False)
def get_all_komentar():
    connection = get_connection()
    cursor = connection.cursor(dictionary=True)
    # JOIN ke tabel user
    cursor.execute("""
        SELECT k.*, u.photo_path, u.domisili, u.golongan_darah
        FROM komentar k
        JOIN users u ON k.user_id = u.user_id
        ORDER BY k.komentar_id DESC
    """)
    data = cursor.fetchall()
    cursor.close()
    close_connection(connection)
    return jsonify({'data': data, 'message': 'Success'}), 200

@komentar_endpoints.route('/<int:komentar_id>', methods=['GET'])
def get_komentar_by_id(komentar_id):
    connection = get_connection()
    cursor = connection.cursor(dictionary=True)
    cursor.execute("SELECT * FROM komentar WHERE komentar_id=%s", (komentar_id,))
    data = cursor.fetchone()
    cursor.close()
    close_connection(connection)
    if not data:
        return jsonify({'message': 'Komentar tidak ditemukan'}), 404
    return jsonify({'data': data, 'message': 'Success'}), 200

@komentar_endpoints.route('/create', methods=['POST'])
@jwt_required()
def create_komentar():
    nama = request.form.get('nama')
    deskripsi = request.form.get('deskripsi')
    user_id = get_user_id_from_jwt()
    if not user_id:
        return jsonify({'message': 'Unauthorized'}), 401
    if not nama or not deskripsi:
        return jsonify({'message': 'Nama dan deskripsi wajib diisi'}), 400
    connection = get_connection()
    cursor = connection.cursor()
    cursor.execute("INSERT INTO komentar (user_id, nama, deskripsi) VALUES (%s, %s, %s)", (user_id, nama, deskripsi))
    connection.commit()
    komentar_id = cursor.lastrowid
    cursor.close()
    close_connection(connection)
    return jsonify({'message': 'Komentar berhasil ditambahkan', 'komentar_id': komentar_id}), 201

@komentar_endpoints.route('/delete/<int:komentar_id>', methods=['DELETE'])
@jwt_required()
def delete_komentar(komentar_id):
    user_id = get_user_id_from_jwt()
    role = get_role_from_jwt()
    if not user_id:
        return jsonify({'message': 'Unauthorized'}), 401
    if role != 'admin':
        return jsonify({'message': 'Unauthorized, hanya admin yang bisa hapus komentar'}), 403
    connection = get_connection()
    cursor = connection.cursor(dictionary=True)
    cursor.execute("SELECT * FROM komentar WHERE komentar_id=%s", (komentar_id,))
    data = cursor.fetchone()
    if not data:
        cursor.close()
        close_connection(connection)
        return jsonify({'message': 'Komentar tidak ditemukan'}), 404
    cursor.execute("DELETE FROM komentar WHERE komentar_id=%s", (komentar_id,))
    connection.commit()
    cursor.close()
    close_connection(connection)
    return jsonify({'message': 'Komentar berhasil dihapus'}), 200
