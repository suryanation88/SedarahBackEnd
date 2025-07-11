#!/usr/bin/env python3
"""Test database connection"""

from helper.db_helper import get_connection, close_connection

def test_db_connection():
    print("=== Testing Database Connection ===")
    
    try:
        # Test connection
        connection = get_connection()
        print("✅ Database connection successful")
        
        # Test query
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT COUNT(*) as count FROM users")
        result = cursor.fetchone()
        print(f"✅ Users table exists, count: {result['count']}")
        
        # Test select users
        cursor.execute("SELECT username, role FROM users LIMIT 5")
        users = cursor.fetchall()
        print(f"✅ Found {len(users)} users:")
        for user in users:
            print(f"   - {user['username']} (role: {user['role']})")
        
        cursor.close()
        close_connection(connection)
        print("✅ Database test completed successfully")
        
    except Exception as e:
        print(f"❌ Database error: {str(e)}")
        print(f"Error type: {type(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_db_connection() 