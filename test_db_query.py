#!/usr/bin/env python3
"""
Script to check database contents
"""
import sys
import os
sys.path.append('/app')

from sqlalchemy import text
from app.config.database import SessionLocal

def check_database():
    db = SessionLocal()
    try:
        # Check tenants
        result = db.execute(text("SELECT id, name, display_name, domain FROM tenants"))
        tenants = result.fetchall()
        print("=== TENANTS ===")
        for tenant in tenants:
            print(f"ID: {tenant[0]}, Name: {tenant[1]}, Display: {tenant[2]}, Domain: {tenant[3]}")
        
        # Check users
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
    check_database()