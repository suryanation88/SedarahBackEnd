#!/usr/bin/env python3
"""Generate bcrypt password hash"""

from flask_bcrypt import Bcrypt

bcrypt = Bcrypt()

def generate_password_hash(password):
    """Generate bcrypt hash for password"""
    hashed = bcrypt.generate_password_hash(password).decode('utf-8')
    print(f"Password: {password}")
    print(f"Hash: {hashed}")
    return hashed

if __name__ == "__main__":
    print("=== Generate Password Hash ===")
    
    # Generate hash for admin password
    admin_password = "admin123"
    admin_hash = generate_password_hash(admin_password)
    
    print("\n=== SQL Query ===")
    print(f"UPDATE users SET password = '{admin_hash}' WHERE username = 'admin';")
    
    print("\n=== Or Insert New Admin ===")
    print(f"""INSERT INTO users (
    username, 
    email, 
    password, 
    nama, 
    domisili, 
    golongan_darah, 
    no_telp, 
    role
) VALUES (
    'admin',
    'admin@sedarah.com',
    '{admin_hash}',
    'Administrator',
    'Denpasar',
    'O+',
    123456789,
    'admin'
);""") 