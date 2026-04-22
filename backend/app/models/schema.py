from sqlalchemy import Column, String, Boolean, Integer, ForeignKey, DateTime
from sqlalchemy.orm import declarative_base
from datetime import datetime
import uuid

Base = declarative_base()

# Helper untuk generate UUID sebagai String
def generate_uuid():
    return str(uuid.uuid4())

class User(Base):
    __tablename__ = "users"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    email = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=True) # Nullable karena bisa login via OAuth
    phone_hash = Column(String, index=True, nullable=True) # Penting untuk sinkronisasi kontak
    linkedin_id = Column(String, unique=True, nullable=True)
    is_admin = Column(Boolean, default=False)
    is_open_to_refer = Column(Boolean, default=True) # Sesuai fitur kontrol privasi
    referral_quota = Column(Integer, default=5)
    created_at = Column(DateTime, default=datetime.utcnow)

class Company(Base):
    __tablename__ = "companies"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    name = Column(String, unique=True, nullable=False) # Nanti akan diindeks dengan pg_trgm
    industry = Column(String, nullable=True)
    verified = Column(Boolean, default=False)

class ReferralRequest(Base):
    __tablename__ = "referral_requests"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    requester_id = Column(String, ForeignKey("users.id"), nullable=False)
    referee_id = Column(String, ForeignKey("users.id"), nullable=False)
    company_id = Column(String, ForeignKey("companies.id"), nullable=False)
    status = Column(String, default="pending") # pending/sent/viewed/accepted/declined
    message_channel = Column(String, default="whatsapp") # whatsapp / email
    sent_at = Column(DateTime, default=datetime.utcnow)
    responded_at = Column(DateTime, nullable=True)