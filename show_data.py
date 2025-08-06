#!/usr/bin/env python3
"""
Script to show actual database data
"""
import sys
import os
sys.path.append('/app')

from sqlalchemy import text
from app.config.database import SessionLocal

def show_data():
    db = SessionLocal()
    try:
        # Show actual tenants
        result = db.execute(text("SELECT * FROM tenants"))
        tenants = result.fetchall()
        print("=== TENANTS ===")
        for tenant in tenants:
            print(f"Tenant: {tenant}")
        
        # Show actual users
        result = db.execute(text("SELECT id, username, email, role, tenant_id FROM users"))
        users = result.fetchall()
        print("\n=== USERS ===")
        for user in users:
            print(f"ID: {user[0]}, Username: {user[1]}, Email: {user[2]}, Role: {user[3]}, Tenant: {user[4]}")
            
    except Exception as e:
        print(f"Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    show_data()