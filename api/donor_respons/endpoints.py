from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from helper.db_helper import get_connection, close_connection
from helper.jwt_helper import get_user_id_from_jwt, get_role_from_jwt
from datetime import date
import ast

donor_respons_endpoints = Blueprint('donor_respons', __name__)

@donor_respons_endpoints.route('/', methods=['GET'], strict_slashes=False)
@jwt_required()
def get_all_donor_respons():
    user_id = get_user_id_from_jwt()
    if not user_id:
        return jsonify({'message': 'Unauthorized'}), 401
    
    connection = get_connection()
    cursor = connection.cursor(dictionary=True)
    
    # Join dengan tabel permohonan untuk mendapatkan data lengkap
    query = """
        SELECT 
            dr.*,
            p.nama_pasien,
            p.kabupaten,
            p.rumah_sakit,
            p.golongan_darah,
            p.rhesus,
            p.jml_pendonor,
            p.nama_pemohon,
            p.no_telp,
            p.tanggal_kebutuhan,
            p.status as permohonan_status
        FROM donor_respons dr
        LEFT JOIN permohonan p ON dr.permohonan_id = p.permohonan_id
        WHERE dr.user_id = %s 
        ORDER BY dr.created_at DESC
    """
    
    cursor.execute(query, (user_id,))
    data = cursor.fetchall()
    cursor.close()
    close_connection(connection)
    
    # Format data untuk frontend
    formatted_data = []
    for item in data:
        formatted_item = {
            'donor_id': item['donor_id'],
            'user_id': item['user_id'],
            'permohonan_id': item['permohonan_id'],
            'status': item['status'],
            'tanggal_donor': item.get('tanggal_donor'),
            'created_at': item.get('created_at'),
            'updated_at': item.get('updated_at'),
            'permohonan': {
                'nama_pasien': item.get('nama_pasien'),
                'kabupaten': item.get('kabupaten'),
                'rumah_sakit': item.get('rumah_sakit'),
                'golongan_darah': item.get('golongan_darah'),
                'rhesus': item.get('rhesus'),
                'jml_pendonor': item.get('jml_pendonor'),
                'nama_pemohon': item.get('nama_pemohon'),
                'no_telp': item.get('no_telp'),
                'tanggal_kebutuhan': item.get('tanggal_kebutuhan'),
                'status': item.get('permohonan_status')
            }
        }
        formatted_data.append(formatted_item)
    
    return jsonify({'data': formatted_data, 'message': 'Success'}), 200

@donor_respons_endpoints.route('/<int:donor_id>', methods=['GET'])
@jwt_required()
def get_donor_respons_by_id(donor_id):
    user_id = get_user_id_from_jwt()
    if not user_id:
        return jsonify({'message': 'Unauthorized'}), 401
    connection = get_connection()
    cursor = connection.cursor(dictionary=True)
    cursor.execute("SELECT * FROM donor_respons WHERE donor_id=%s AND user_id=%s", (donor_id, user_id))
    data = cursor.fetchone()
    cursor.close()
    close_connection(connection)
    if not data:
        return jsonify({'message': 'Donor respons tidak ditemukan'}), 404
    return jsonify({'data': data, 'message': 'Success'}), 200

@donor_respons_endpoints.route('/create', methods=['POST'])
@jwt_required()
def create_donor_respons():
    user_id = get_user_id_from_jwt()
    if not user_id:
        return jsonify({'message': 'Unauthorized'}), 401
    permohonan_id = request.form.get('permohonan_id')
    if not permohonan_id:
        return jsonify({'message': 'permohonan_id wajib diisi'}), 400

    connection = get_connection()
    cursor = connection.cursor(dictionary=True)

    # Cek apakah sudah ada donor respons untuk permohonan ini
    cursor.execute("SELECT * FROM donor_respons WHERE user_id=%s AND permohonan_id=%s", (user_id, permohonan_id))
    existing_donor = cursor.fetchone()

    if existing_donor:
        cursor.close()
        close_connection(connection)
        return jsonify({'message': 'Anda sudah mendaftar sebagai donor untuk permohonan ini'}), 400

    # Cek apakah permohonan masih valid (belum selesai) dan ambil user_id pembuat permohonan
    cursor.execute("SELECT user_id FROM permohonan WHERE permohonan_id=%s AND status='Belum Selesai'", (permohonan_id,))
    permohonan = cursor.fetchone()

    if not permohonan:
        cursor.close()
        close_connection(connection)
        return jsonify({'message': 'Permohonan tidak ditemukan atau sudah selesai'}), 404

    # Tambahkan pengecekan: user tidak boleh donor di permohonan sendiri
    if str(permohonan['user_id']) == str(user_id):
        cursor.close()
        close_connection(connection)
        return jsonify({'message': 'Anda tidak bisa donor di permohonan yang Anda buat sendiri!'}), 400

    cursor.close()
    cursor = connection.cursor()
    cursor.execute(
        "INSERT INTO donor_respons (user_id, permohonan_id) VALUES (%s, %s)",
        (user_id, permohonan_id)
    )
    connection.commit()
    cursor.close()
    close_connection(connection)
    return jsonify({'message': 'Donor respons berhasil dibuat'}), 201

@donor_respons_endpoints.route('/update/<int:donor_id>', methods=['PUT'])
@jwt_required()
def update_donor_respons(donor_id):
    from datetime import date
    user_id = get_user_id_from_jwt()
    if not user_id:
        return jsonify({'message': 'Unauthorized'}), 401
    role = get_role_from_jwt()
    status = request.form.get('status')
    if not status:
        return jsonify({'message': 'Status wajib diisi'}), 400
    # Logika pembatasan status
    if role == 'admin':
        allowed_status = ['DIKONFIRMASI', 'DIBATALKAN', 'SELESAI']
    else:
        allowed_status = ['DIKONFIRMASI', 'DIBATALKAN']
    if status.upper() not in allowed_status:
        return jsonify({'message': f'Status {status} tidak diizinkan untuk role ini'}), 403
    connection = get_connection()
    cursor = connection.cursor()
    if status.strip().upper() == 'SELESAI' and role == 'admin':
        tanggal_donor = date.today()
        cursor.execute(
            "UPDATE donor_respons SET status=%s, tanggal_donor=%s WHERE donor_id=%s",
            (status, tanggal_donor, donor_id)
        )
    else:
        cursor.execute(
            "UPDATE donor_respons SET status=%s WHERE donor_id=%s",
            (status, donor_id)
        )
    connection.commit()
    cursor.close()
    close_connection(connection)
    return jsonify({'message': 'Status donor respons berhasil diupdate'}), 200

@donor_respons_endpoints.route('/delete/<int:donor_id>', methods=['DELETE'])
@jwt_required()
def delete_donor_respons(donor_id):
    user_id = get_user_id_from_jwt()
    if not user_id:
        return jsonify({'message': 'Unauthorized'}), 401
    role = get_role_from_jwt()
    if role != 'admin':
        return jsonify({'message': 'Unauthorized, hanya admin yang bisa hapus donor respons'}), 403
    connection = get_connection()
    cursor = connection.cursor()
    cursor.execute("DELETE FROM donor_respons WHERE donor_id=%s", (donor_id,))
    connection.commit()
    cursor.close()
    close_connection(connection)
    return jsonify({'message': 'Donor respons berhasil dihapus'}), 200

@donor_respons_endpoints.route('/user/<int:user_id>', methods=['GET'])
@jwt_required()
def get_donor_respons_by_user(user_id):
    role = get_role_from_jwt()
    if role != 'admin':
        return jsonify({'message': 'Unauthorized'}), 403
    connection = get_connection()
    cursor = connection.cursor(dictionary=True)
    query = """
        SELECT 
            dr.*,
            p.nama_pasien,
            p.kabupaten,
            p.rumah_sakit,
            p.golongan_darah,
            p.rhesus,
            p.jml_pendonor,
            p.nama_pemohon,
            p.no_telp,
            p.tanggal_kebutuhan,
            p.status as permohonan_status
        FROM donor_respons dr
        LEFT JOIN permohonan p ON dr.permohonan_id = p.permohonan_id
        WHERE dr.user_id = %s
        ORDER BY dr.created_at DESC
    """
    cursor.execute(query, (user_id,))
    data = cursor.fetchall()
    cursor.close()
    close_connection(connection)
    return jsonify({'data': data, 'message': 'Success'}), 200


