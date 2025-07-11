"""Routes for module pendonor"""
from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from helper.db_helper import get_connection, close_connection

pendonor_endpoints = Blueprint('pendonor', __name__)


@pendonor_endpoints.route('/', methods=['GET'])
@jwt_required()
def get_pendonor():
    """Get all pendonor"""
    # Get user_id from JWT token
    identity = get_jwt_identity()
    user_id = eval(identity).get('user_id')
    
    connection = None
    try:
        connection = get_connection()
        cursor = connection.cursor(dictionary=True)
        
        # Get pendonor by user_id
        query = "SELECT * FROM pendonor WHERE user_id = %s ORDER BY created_at DESC"
        cursor.execute(query, (user_id,))
        pendonor_list = cursor.fetchall()
        cursor.close()
        
        return jsonify({"data": pendonor_list, "message": "Success"}), 200
    except Exception as e:
        return jsonify({"message": f"Error: {str(e)}"}), 500
    finally:
        if connection:
            close_connection(connection)


@pendonor_endpoints.route('/<int:pendonor_id>', methods=['GET'])
@jwt_required()
def get_pendonor_by_id(pendonor_id):
    """Get pendonor by ID"""
    # Get user_id from JWT token
    identity = get_jwt_identity()
    user_id = eval(identity).get('user_id')
    
    connection = None
    try:
        connection = get_connection()
        cursor = connection.cursor(dictionary=True)
        
        # Check if pendonor exists and belongs to user
        query = "SELECT * FROM pendonor WHERE pendonor_id = %s AND user_id = %s"
        cursor.execute(query, (pendonor_id, user_id))
        pendonor = cursor.fetchone()
        cursor.close()
        
        if not pendonor:
            return jsonify({"message": "Pendonor tidak ditemukan"}), 404
        
        return jsonify({"data": pendonor, "message": "Success"}), 200
    except Exception as e:
        return jsonify({"message": f"Error: {str(e)}"}), 500
    finally:
        if connection:
            close_connection(connection)


@pendonor_endpoints.route('/create', methods=['POST'])
@jwt_required()
def create_pendonor():
    """Create new pendonor"""
    nama = request.form.get('nama')
    alamat = request.form.get('alamat')
    golongan_darah = request.form.get('golongan_darah')
    
    if not nama or not alamat or not golongan_darah:
        return jsonify({"message": "Nama, alamat, dan golongan darah harus diisi"}), 400
    
    # Validate golongan darah
    valid_golongan = ['A-', 'A+', 'B-', 'B+', 'AB-', 'AB+', 'O-', 'O+']
    if golongan_darah not in valid_golongan:
        return jsonify({"message": "Golongan darah tidak valid"}), 400
    
    # Get user_id from JWT token
    identity = get_jwt_identity()
    user_id = eval(identity).get('user_id')
    
    connection = None
    try:
        connection = get_connection()
        cursor = connection.cursor()
        
        insert_query = "INSERT INTO pendonor (user_id, nama, alamat, golongan_darah) VALUES (%s, %s, %s, %s)"
        request_insert = (user_id, nama, alamat, golongan_darah)
        cursor.execute(insert_query, request_insert)
        connection.commit()
        new_id = cursor.lastrowid
        cursor.close()
        
        if new_id:
            return jsonify({
                "message": "Pendonor berhasil ditambahkan",
                "pendonor_id": new_id,
                "nama": nama,
                "alamat": alamat,
                "golongan_darah": golongan_darah
            }), 201
        
        return jsonify({"message": "Gagal menambahkan pendonor"}), 500
    except Exception as e:
        return jsonify({"message": f"Error: {str(e)}"}), 500
    finally:
        if connection:
            close_connection(connection)


@pendonor_endpoints.route('/update/<int:pendonor_id>', methods=['PUT'])
@jwt_required()
def update_pendonor(pendonor_id):
    """Update pendonor"""
    nama = request.form.get('nama')
    alamat = request.form.get('alamat')
    golongan_darah = request.form.get('golongan_darah')
    
    # Validate golongan darah if provided
    if golongan_darah:
        valid_golongan = ['A-', 'A+', 'B-', 'B+', 'AB-', 'AB+', 'O-', 'O+']
        if golongan_darah not in valid_golongan:
            return jsonify({"message": "Golongan darah tidak valid"}), 400
    
    # Get user_id from JWT token
    identity = get_jwt_identity()
    user_id = eval(identity).get('user_id')
    
    connection = None
    try:
        connection = get_connection()
        cursor = connection.cursor(dictionary=True)
        
        # Check if pendonor exists and belongs to user
        check_query = "SELECT * FROM pendonor WHERE pendonor_id = %s AND user_id = %s"
        cursor.execute(check_query, (pendonor_id, user_id))
        existing_pendonor = cursor.fetchone()
        
        if not existing_pendonor:
            cursor.close()
            return jsonify({"message": "Pendonor tidak ditemukan"}), 404
        
        # Build update query dynamically
        update_fields = []
        update_values = []
        
        if nama:
            update_fields.append("nama = %s")
            update_values.append(nama)
        if alamat:
            update_fields.append("alamat = %s")
            update_values.append(alamat)
        if golongan_darah:
            update_fields.append("golongan_darah = %s")
            update_values.append(golongan_darah)
        
        if not update_fields:
            cursor.close()
            return jsonify({"message": "Tidak ada data yang diupdate"}), 400
        
        update_values.append(pendonor_id)
        update_query = f"UPDATE pendonor SET {', '.join(update_fields)} WHERE pendonor_id = %s"
        
        cursor.execute(update_query, update_values)
        connection.commit()
        cursor.close()
        
        return jsonify({"message": "Pendonor berhasil diupdate"}), 200
    except Exception as e:
        return jsonify({"message": f"Error: {str(e)}"}), 500
    finally:
        if connection:
            close_connection(connection)


@pendonor_endpoints.route('/delete/<int:pendonor_id>', methods=['DELETE'])
@jwt_required()
def delete_pendonor(pendonor_id):
    """Delete pendonor"""
    # Get user_id from JWT token
    identity = get_jwt_identity()
    user_id = eval(identity).get('user_id')
    
    connection = None
    try:
        connection = get_connection()
        cursor = connection.cursor(dictionary=True)
        
        # Check if pendonor exists and belongs to user
        check_query = "SELECT * FROM pendonor WHERE pendonor_id = %s AND user_id = %s"
        cursor.execute(check_query, (pendonor_id, user_id))
        existing_pendonor = cursor.fetchone()
        
        if not existing_pendonor:
            cursor.close()
            return jsonify({"message": "Pendonor tidak ditemukan"}), 404
        
        delete_query = "DELETE FROM pendonor WHERE pendonor_id = %s"
        cursor.execute(delete_query, (pendonor_id,))
        connection.commit()
        cursor.close()
        
        return jsonify({"message": "Pendonor berhasil dihapus"}), 200
    except Exception as e:
        return jsonify({"message": f"Error: {str(e)}"}), 500
    finally:
        if connection:
            close_connection(connection)