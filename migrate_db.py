#!/usr/bin/env python3
"""
Database migration script to add new columns to existing database
"""

import sqlite3
import os
from app import app, db

def migrate_database():
    """Add missing columns to existing database"""
    db_path = os.path.join(app.instance_path, 'passport_ocr.db')
    
    if not os.path.exists(db_path):
        print("Database doesn't exist, creating new one...")
        with app.app_context():
            db.create_all()
        return
    
    print(f"Migrating database: {db_path}")
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Check existing columns
    cursor.execute("PRAGMA table_info(passport_record)")
    existing_columns = [column[1] for column in cursor.fetchall()]
    print(f"Existing columns: {existing_columns}")
    
    # Add missing columns if they don't exist
    columns_to_add = [
        ('emergency_contact', 'VARCHAR(200) DEFAULT ""'),
        ('phone_number', 'VARCHAR(50) DEFAULT ""'),
        ('previous_passport', 'VARCHAR(50) DEFAULT ""')
    ]
    
    for column_name, column_def in columns_to_add:
        if column_name not in existing_columns:
            try:
                cursor.execute(f'ALTER TABLE passport_record ADD COLUMN {column_name} {column_def}')
                print(f"Added column: {column_name}")
            except sqlite3.OperationalError as e:
                print(f"Error adding column {column_name}: {e}")
    
    conn.commit()
    conn.close()
    
    # Now create HR tables using SQLAlchemy
    with app.app_context():
        try:
            db.create_all()
            print("HR tables created successfully")
        except Exception as e:
            print(f"Error creating HR tables: {e}")

if __name__ == '__main__':
    migrate_database()
    print("Database migration completed!")