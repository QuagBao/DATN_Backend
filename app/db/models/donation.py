import uuid
from sqlalchemy import Column, String, TIMESTAMP, ForeignKey, Numeric
from sqlalchemy import String
from sqlalchemy.orm import relationship
from app.db.database import Base


class Donation(Base):
    __tablename__ = "donation"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    account_id = Column(String(36), ForeignKey("account.id_account"))
    project_id = Column(String(36), ForeignKey("project.id_project"))
        
    amount = Column(Numeric, nullable=False)
    paytime = Column(TIMESTAMP, nullable=False)
    transaction_id = Column(String(255), nullable=False)

    account = relationship("Account", back_populates="donations")
    project = relationship("Project", back_populates="donations")

    def __init__(self, account_id, project_id, amount, paytime, transaction_id):
        self.account_id = account_id
        self.project_id = project_id
        self.amount = amount
        self.paytime = paytime
        self.transaction_id = transaction_id

    def __repr__(self):
        return f"<Donation(id='{self.id}', account_id='{self.account_id}', project_id='{self.project_id}', amount='{self.amount}')>"

    # Getters
    def get_amount(self):
        return self.amount

    def get_paytime(self):
        return self.paytime

    def get_transaction_id(self):
        return self.transaction_id

    # Setters
    def set_amount(self, new_amount):
        self.amount = new_amount

    def set_paytime(self, new_paytime):
        self.paytime = new_paytime

    def set_transaction_id(self, new_transaction_id):
        self.transaction_id = new_transaction_id
