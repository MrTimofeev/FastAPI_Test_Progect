from sqlalchemy import Column, Integer, String, Date
from database import Base

class ParserData(Base):
    __tablename__ = 'parsed_data'
    
    id = Column(Integer, primary_key=True)
    exchange_product_id = Column(String, nullable=True)
    exchange_product_name = Column(String, nullable=True)
    oil_id = Column(String, nullable=True)
    delivery_basis_id = Column(String, nullable=True)
    delivery_basis_name = Column(String, nullable=True)
    delivery_type_id = Column(String, nullable=True)
    volume = Column(Integer, nullable=True)
    total = Column(Integer, nullable=True)
    count = Column(Integer, nullable=True)
    date = Column(Date, nullable=True)
    created_on = Column(Date, nullable=True)
    updated_on = Column(Date, nullable=True)