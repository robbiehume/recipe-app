import mysql.connector

def get_db_connection():
    """Legacy direct database connection for password verification"""
    return mysql.connector.connect(
        host='database-1.cp8im2sk8sm3.us-east-2.rds.amazonaws.com',
        user='admin',
        password='adminpassword',
        database='recipe_app'
    ) 