#!/bin/bash

# Create versions directory for Alembic
mkdir -p app/alembic/versions

# Create initial migration
#cd /home/ubuntu/kindergarten_kitchen_system
alembic -c app/alembic/alembic.ini revision --autogenerate -m "Initial migration"

# Apply migration
alembic -c app/alembic/alembic.ini upgrade head

# Create initial admin user
python3 -c "
from app.db.session import SessionLocal
from app.models.models import User, UserRole
from app.core.security import get_password_hash

db = SessionLocal()
admin = User(
    username='admin',
    email='admin@example.com',
    hashed_password=get_password_hash('admin'),
    full_name='Administrator',
    role=UserRole.admin,
    is_active=True
)
db.add(admin)
db.commit()
db.close()
print('Admin user created successfully')
"

# Start the application
#cd /home/ubuntu/kindergarten_kitchen_system
uvicorn app.main:app --host 127.0.0.1 --port 8000
