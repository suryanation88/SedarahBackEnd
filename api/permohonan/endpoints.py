"""Routes for module permohonan"""
from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required
from helper.db_helper import get_connection, close_connection
from helper.jwt_helper import get_user_id_from_jwt

permohonan_endpoints = Blueprint('permohonan', __name__)


@permohonan_endpoints.route('/all', methods=['GET'])
@jwt_required()
def get_all_permohonan():
    """Get all permohonan for donor page (tidak filter user_id)"""
    connection = None
    try:
        connection = get_connection()
        cursor = connection.cursor(dictionary=True)
        
        # Get all permohonan yang belum selesai
        query = "SELECT permohonan_id, user_id, nama_pasien, kabupaten, rumah_sakit, golongan_darah, rhesus, jml_pendonor, nama_pemohon, no_telp, status, tanggal_kebutuhan, created_at FROM permohonan WHERE status = 'Belum Selesai' ORDER BY created_at DESC"
        cursor.execute(query)
        permohonan_list = cursor.fetchall()
        cursor.close()
        
        return jsonify({"data": permohonan_list, "message": "Success"}), 200
    except Exception as e:
        return jsonify({"message": f"Error: {str(e)}"}), 500
    finally:
        if connection:
            close_connection(connection)


@permohonan_endpoints.route('/', methods=['GET'], strict_slashes=False)
@jwt_required()
def get_permohonan():
    """Get all permohonan"""
    user_id = get_user_id_from_jwt()
    if not user_id:
        return jsonify({"message": "Unauthorized"}), 401
    user_id = int(user_id)
    
    connection = None
    try:
        connection = get_connection()
        cursor = connection.cursor(dictionary=True)
        
        # Get permohonan by user_id
        query = "SELECT * FROM permohonan WHERE user_id = %s ORDER BY created_at DESC"
        cursor.execute(query, (user_id,))
        permohonan_list = cursor.fetchall()
        cursor.close()
        
        return jsonify({"data": permohonan_list, "message": "Success"}), 200
    except Exception as e:
        return jsonify({"message": f"Error: {str(e)}"}), 500
    finally:
        if connection:
            close_connection(connection)


@permohonan_endpoints.route('/<int:permohonan_id>', methods=['GET'])
@jwt_required()
def get_permohonan_by_id(permohonan_id):
    """Get permohonan by ID"""
    user_id = get_user_id_from_jwt()
    if not user_id:
        return jsonify({"message": "Unauthorized"}), 401
    user_id = int(user_id)
    
    connection = None
    try:
        connection = get_connection()
        cursor = connection.cursor(dictionary=True)
        
        # Check if permohonan exists and belongs to user
        query = "SELECT * FROM permohonan WHERE permohonan_id = %s AND user_id = %s"
        cursor.execute(query, (permohonan_id, user_id))
        permohonan = cursor.fetchone()
        cursor.close()
        
        if not permohonan:
            return jsonify({"message": "Permohonan tidak ditemukan"}), 404
        
        return jsonify({"data": permohonan, "message": "Success"}), 200
    except Exception as e:
        return jsonify({"message": f"Error: {str(e)}"}), 500
    finally:
        if connection:
            close_connection(connection)


@permohonan_endpoints.route('/create', methods=['POST'])
@jwt_required()
def create_permohonan():
    nama_pasien = request.form.get('nama_pasien')
    kabupaten = request.form.get('kabupaten')
    rumah_sakit = request.form.get('rumah_sakit')
    golongan_darah = request.form.get('golongan_darah')
    rhesus = request.form.get('rhesus')
    jml_pendonor = request.form.get('jml_pendonor')
    nama_pemohon = request.form.get('nama_pemohon')
    no_telp = request.form.get('no_telp')
    status = request.form.get('status', 'Belum Selesai')
    tanggal_kebutuhan = request.form.get('tanggal_kebutuhan')

    # Validasi wajib isi
    if not all([nama_pasien, kabupaten, rumah_sakit, golongan_darah, rhesus, jml_pendonor, nama_pemohon, no_telp, tanggal_kebutuhan]):
        return jsonify({"message": "Semua field wajib diisi"}), 400

    # Validasi enum
    valid_golongan = ['A', 'B', 'AB', 'O']
    valid_rhesus = ['+', '-']
    valid_status = ['Selesai', 'Belum Selesai']
    valid_kabupaten = ['Gianyar','Tabanan','Bangli','Buleleng','Denpasar','Badung','Klungkung','Karangasem','Jembrana']

    if golongan_darah not in valid_golongan:
        return jsonify({"message": "Golongan darah tidak valid"}), 400
    if rhesus not in valid_rhesus:
        return jsonify({"message": "Rhesus tidak valid"}), 400
    if status not in valid_status:
        return jsonify({"message": "Status tidak valid"}), 400
    if kabupaten not in valid_kabupaten:
        return jsonify({"message": "Kabupaten tidak valid"}), 400

    # Get user_id dari JWT
    user_id = get_user_id_from_jwt()
    if not user_id:
        return jsonify({"message": "Unauthorized"}), 401
    user_id = int(user_id)

    connection = None
    try:
        connection = get_connection()
        cursor = connection.cursor()
        insert_query = """
            INSERT INTO permohonan
            (user_id, nama_pasien, kabupaten, rumah_sakit, golongan_darah, rhesus, jml_pendonor, nama_pemohon, no_telp, status, tanggal_kebutuhan)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        request_insert = (user_id, nama_pasien, kabupaten, rumah_sakit, golongan_darah, rhesus, jml_pendonor, nama_pemohon, no_telp, status, tanggal_kebutuhan)
        cursor.execute(insert_query, request_insert)
        connection.commit()
        new_id = cursor.lastrowid
        cursor.close()
        if new_id:
            return jsonify({
                "message": "Permohonan berhasil ditambahkan",
                "permohonan_id": new_id
            }), 201
        return jsonify({"message": "Gagal menambahkan permohonan"}), 500
    except Exception as e:
        return jsonify({"message": f"Error: {str(e)}"}), 500
    finally:
        if connection:
            close_connection(connection)


@permohonan_endpoints.route('/update/<int:permohonan_id>', methods=['PUT'])
@jwt_required()
def update_permohonan(permohonan_id):
    # Ambil semua field yang mungkin diupdate
    fields = ['nama_pasien', 'kabupaten', 'rumah_sakit', 'golongan_darah', 'rhesus', 'jml_pendonor', 'nama_pemohon', 'no_telp', 'status', 'tanggal_kebutuhan']
    update_fields = []
    update_values = []
    for field in fields:
        value = request.form.get(field)
        if value is not None:
            update_fields.append(f"{field} = %s")
            update_values.append(value)
    if not update_fields:
        return jsonify({"message": "Tidak ada data yang diupdate"}), 400
    update_values.append(permohonan_id)
    connection = None
    try:
        connection = get_connection()
        cursor = connection.cursor()
        update_query = f"UPDATE permohonan SET {', '.join(update_fields)} WHERE permohonan_id = %s"
        cursor.execute(update_query, update_values)
        connection.commit()
        cursor.close()
        return jsonify({"message": "Permohonan berhasil diupdate"}), 200
    except Exception as e:
        return jsonify({"message": f"Error: {str(e)}"}), 500
    finally:
        if connection:
            close_connection(connection)


@permohonan_endpoints.route('/delete/<int:permohonan_id>', methods=['DELETE'])
@jwt_required()
def delete_permohonan(permohonan_id):
    """Delete permohonan"""
    user_id = get_user_id_from_jwt()
    if not user_id:
        return jsonify({"message": "Unauthorized"}), 401
    user_id = int(user_id)
    
    connection = None
    try:
        connection = get_connection()
        cursor = connection.cursor(dictionary=True)
        
        # Check if permohonan exists and belongs to user
        check_query = "SELECT * FROM permohonan WHERE permohonan_id = %s AND user_id = %s"
        cursor.execute(check_query, (permohonan_id, user_id))
        existing_permohonan = cursor.fetchone()
        
        if not existing_permohonan:
            cursor.close()
            return jsonify({"message": "Permohonan tidak ditemukan"}), 404
        
        delete_query = "DELETE FROM permohonan WHERE permohonan_id = %s"
        cursor.execute(delete_query, (permohonan_id,))
        connection.commit()
        cursor.close()
        
        return jsonify({"message": "Permohonan berhasil dihapus"}), 200
    except Exception as e:
        return jsonify({"message": f"Error: {str(e)}"}), 500
    finally:
        if connection:
            close_connection(connection)


@permohonan_endpoints.route('/user/<int:user_id>', methods=['GET'])
@jwt_required()
def get_permohonan_by_user_admin(user_id):
    from helper.jwt_helper import get_role_from_jwt
    role = get_role_from_jwt()
    if role != 'admin':
        return jsonify({'message': 'Unauthorized'}), 403
    connection = get_connection()
    cursor = connection.cursor(dictionary=True)
    query = "SELECT * FROM permohonan WHERE user_id = %s ORDER BY created_at DESC"
    cursor.execute(query, (user_id,))
    data = cursor.fetchall()
    cursor.close()
    close_connection(connection)
    return jsonify({'data': data, 'message': 'Success'}), 200


@permohonan_endpoints.route('/all_admin', methods=['GET'])
@jwt_required()
def get_all_permohonan_admin():
    from helper.jwt_helper import get_role_from_jwt
    role = get_role_from_jwt()
    if role != 'admin':
        return jsonify({'message': 'Unauthorized'}), 403
    connection = None
    try:
        connection = get_connection()
        cursor = connection.cursor(dictionary=True)
        query = "SELECT permohonan_id, user_id, nama_pasien, kabupaten, rumah_sakit, golongan_darah, rhesus, jml_pendonor, nama_pemohon, no_telp, status, tanggal_kebutuhan, created_at FROM permohonan ORDER BY created_at DESC"
        cursor.execute(query)
        permohonan_list = cursor.fetchall()
        cursor.close()
        return jsonify({"data": permohonan_list, "message": "Success"}), 200
    except Exception as e:
        return jsonify({"message": f"Error: {str(e)}"}), 500
    finally:
        if connection:
            close_connection(connection)
