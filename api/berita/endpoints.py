"""Routes for module berita"""
from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required
from helper.db_helper import get_connection, close_connection
from helper.jwt_helper import get_user_id_from_jwt, get_role_from_jwt
from werkzeug.utils import secure_filename
import os

UPLOAD_FOLDER = os.path.join(os.getcwd(), 'uploads')
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

berita_endpoints = Blueprint('berita', __name__)

@berita_endpoints.route('/', methods=['GET'], strict_slashes=False)
def get_berita():
    """Get all berita (tidak filter user, tampilkan semua)"""
    connection = None
    try:
        connection = get_connection()
        cursor = connection.cursor(dictionary=True)
        query = "SELECT * FROM berita ORDER BY berita_id DESC"
        cursor.execute(query)
        berita_list = cursor.fetchall()
        cursor.close()
        return jsonify({"data": berita_list, "message": "Success"}), 200
    except Exception as e:
        return jsonify({"message": f"Error: {str(e)}"}), 500
    finally:
        if connection:
            close_connection(connection)

@berita_endpoints.route('/<int:berita_id>', methods=['GET'])
@jwt_required()
def get_berita_by_id(berita_id):
    connection = None
    try:
        connection = get_connection()
        cursor = connection.cursor(dictionary=True)
        query = "SELECT * FROM berita WHERE berita_id = %s"
        cursor.execute(query, (berita_id,))
        berita = cursor.fetchone()
        cursor.close()
        if not berita:
            return jsonify({"message": "Berita tidak ditemukan"}), 404
        return jsonify({"data": berita, "message": "Success"}), 200
    except Exception as e:
        return jsonify({"message": f"Error: {str(e)}"}), 500
    finally:
        if connection:
            close_connection(connection)

@berita_endpoints.route('/create', methods=['POST'])
@jwt_required()
def create_berita():
    user_id = get_user_id_from_jwt()
    role = get_role_from_jwt()
    if not user_id:
        return jsonify({"message": "Unauthorized"}), 401
    if role != 'admin':
        return jsonify({"message": "Unauthorized, hanya admin yang bisa menambah berita"}), 403
    judul_berita = request.form.get('judul_berita')
    deskripsi_berita = request.form.get('deskripsi_berita')
    url_berita = request.form.get('url_berita')
    # Logika baru: jika url_image diisi, pakai itu, jika tidak cek file upload
    url_image = request.form.get('url_image')
    if not judul_berita or not deskripsi_berita:
        return jsonify({"message": "Judul berita dan deskripsi berita harus diisi"}), 400
    connection = None
    try:
        connection = get_connection()
        cursor = connection.cursor()
        insert_query = "INSERT INTO berita (user_id, judul_berita, deskripsi_berita, url_image, url_berita) VALUES (%s, %s, %s, %s, %s)"
        request_insert = (user_id, judul_berita, deskripsi_berita, url_image, url_berita)
        cursor.execute(insert_query, request_insert)
        connection.commit()
        new_id = cursor.lastrowid
        cursor.close()
        if new_id:
            return jsonify({
                "message": "Berita berhasil ditambahkan",
                "berita_id": new_id,
                "judul_berita": judul_berita,
                "deskripsi_berita": deskripsi_berita,
                "url_image": url_image,
                "url_berita": url_berita
            }), 201
        return jsonify({"message": "Gagal menambahkan berita"}), 500
    except Exception as e:
        return jsonify({"message": f"Error: {str(e)}"}), 500
    finally:
        if connection:
            close_connection(connection)

@berita_endpoints.route('/update/<int:berita_id>', methods=['PUT'])
@jwt_required()
def update_berita(berita_id):
    user_id = get_user_id_from_jwt()
    role = get_role_from_jwt()
    if not user_id:
        return jsonify({"message": "Unauthorized"}), 401
    if role != 'admin':
        return jsonify({"message": "Unauthorized, hanya admin yang bisa update berita"}), 403
    judul_berita = request.form.get('judul_berita')
    deskripsi_berita = request.form.get('deskripsi_berita')
    url_berita = request.form.get('url_berita')
    # Logika baru: jika url_image diisi, pakai itu, jika tidak cek file upload
    url_image = request.form.get('url_image')
    connection = None
    try:
        connection = get_connection()
        cursor = connection.cursor(dictionary=True)
        check_query = "SELECT * FROM berita WHERE berita_id = %s"
        cursor.execute(check_query, (berita_id,))
        existing_berita = cursor.fetchone()
        if not existing_berita:
            cursor.close()
            return jsonify({"message": "Berita tidak ditemukan"}), 404
        # Jika url_image tidak diisi, cek file upload
        if not url_image:
            if 'image' in request.files:
                image = request.files['image']
                if image.filename != '':
                    old_url = existing_berita.get('url_image')
                    if old_url and old_url.startswith('/uploads/'):
                        filename = os.path.basename(old_url)
                        old_path = os.path.join(UPLOAD_FOLDER, filename)
                        if os.path.exists(old_path):
                            os.remove(old_path)
                    filename = secure_filename(image.filename)
                    image.save(os.path.join(UPLOAD_FOLDER, filename))
                    url_image = f'/uploads/{filename}'
        update_fields = []
        update_values = []
        if judul_berita:
            update_fields.append("judul_berita = %s")
            update_values.append(judul_berita)
        if deskripsi_berita:
            update_fields.append("deskripsi_berita = %s")
            update_values.append(deskripsi_berita)
        if url_image:
            update_fields.append("url_image = %s")
            update_values.append(url_image)
        if url_berita:
            update_fields.append("url_berita = %s")
            update_values.append(url_berita)
        if not update_fields:
            cursor.close()
            return jsonify({"message": "Tidak ada data yang diupdate"}), 400
        update_values.append(berita_id)
        update_query = f"UPDATE berita SET {', '.join(update_fields)} WHERE berita_id = %s"
        cursor.execute(update_query, update_values)
        connection.commit()
        cursor.close()
        return jsonify({"message": "Berita berhasil diupdate", "url_berita": url_berita, "url_image": url_image}), 200
    except Exception as e:
        return jsonify({"message": f"Error: {str(e)}"}), 500
    finally:
        if connection:
            close_connection(connection)

@berita_endpoints.route('/delete/<int:berita_id>', methods=['DELETE'])
@jwt_required()
def delete_berita(berita_id):
    user_id = get_user_id_from_jwt()
    role = get_role_from_jwt()
    if not user_id:
        return jsonify({"message": "Unauthorized"}), 401
    if role != 'admin':
        return jsonify({"message": "Unauthorized, hanya admin yang bisa hapus berita"}), 403
    connection = None
    try:
        connection = get_connection()
        cursor = connection.cursor(dictionary=True)
        check_query = "SELECT * FROM berita WHERE berita_id = %s"
        cursor.execute(check_query, (berita_id,))
        existing_berita = cursor.fetchone()
        if not existing_berita:
            cursor.close()
            return jsonify({"message": "Berita tidak ditemukan"}), 404
        old_url = existing_berita.get('url_image')
        if old_url and old_url.startswith('/uploads/'):
            old_path = os.path.join(UPLOAD_FOLDER, old_url.split('/')[-1])
            if os.path.exists(old_path):
                os.remove(old_path)
        delete_query = "DELETE FROM berita WHERE berita_id = %s"
        cursor.execute(delete_query, (berita_id,))
        connection.commit()
        cursor.close()
        return jsonify({"message": "Berita berhasil dihapus"}), 200
    except Exception as e:
        return jsonify({"message": f"Error: {str(e)}"}), 500
    finally:
        if connection:
            close_connection(connection)
