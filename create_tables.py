#!/usr/bin/env python3
"""
Script to create database tables directly.
Use this if you don't want to use Alembic migrations.
"""
from database import engine, Base
from models import User, Project, Deployment, RefreshToken

if __name__ == "__main__":
    print("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    print("Tables created successfully!")
