from sqlalchemy import Column, Integer, String, Date
from api_service.database import Base

class ParsedData(Base):
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
    
    def to_dict(self):
        return {
            "id": self.id,
            "exchange_product_id": self.exchange_product_id,
            "exchange_product_name": self.exchange_product_name,
            "oil_id": self.oil_id,
            "delivery_basis_id": self.delivery_basis_id,
            "delivery_basis_name": self.delivery_basis_name,
            "delivery_type_id": self.delivery_type_id,
            "volume": self.volume,
            "total": self.total,
            "count": self.count,
            "date": self.date.isoformat() if self.date else None,
            "created_on": self.created_on.isoformat() if self.created_on else None,
            "updated_on": self.updated_on.isoformat() if self.updated_on else None,
        }