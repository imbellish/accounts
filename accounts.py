from sqlalchemy.orm import DeclarativeBase

from typing import List

from sqlalchemy import ForeignKey
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship

ACCOUNT_TYPES = ["ASSET", "LIABILITY", "EQUITY", "REVENUE", "EXPENSE"]
DEBIT = "L"
CREDIT = "R"
NORMAL_BALANCES = [DEBIT, CREDIT]

class Base(DeclarativeBase):
    pass

class Account(Base):
    """
    Implements common elements of all accounts
    """
    __tablename__ = "account"

    id = mapped_column(Integer, primary_key=True)
    name: Mapped[str]
    normal_balance = mapped_column(default=DEBIT)

    # schematic relationships


class Action(Base):
    """
    Implements common elements of all actions
    """
    __tablename__ = "action"

    id = mapped_column(Integer, primary_key=True)
    description: Mapped[str]
    amount: Mapped[float]
    side: Mapped[str]
    order: Mapped[int]

    # schematic relationships
    t_id = mapped_column(ForeignKey("t.id"))

class Debitor(Base):
    """
    Left side of any accounting transaction, itself an action
    """
    __tablename__ = "debitor"

    id = mapped_column(Integer, primary_key=True)
    name: Mapped[str]

    # relationship schemas

class Creditor(Base):
    """
    Right side of any accounting transaction, itself an action
    """
    __tablename__ = "creditor"

    id = mapped_column(Integer, primary_key=True)
    name: Mapped[str]

    # relationship schemas

class T(Base):
    """
    Implements common elements of all T-structs
    """
    __tablename__ = "t"

    id = mapped_column(Integer, primary_key=True)
    debitor_id: Mapped[int] = mapped_column(ForeignKey("debitor.id"))
    creditor_id: Mapped[str] = mapped_column(ForeignKey("creditor.id"))

class Transaction(Base):
    """
    Implements common elements of all transactions
    """
    __tablename__ = "transaction"

    id = mapped_column(Integer, primary_key=True)

    # schematic relationships
    actions: Mapped[List["Action"]] = relationship()



