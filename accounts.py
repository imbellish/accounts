from time import time
from sqlalchemy.orm import DeclarativeBase

from typing import List

from sqlalchemy import ForeignKey
from sqlalchemy import Integer
from sqlalchemy import Float
from sqlalchemy import String
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

ASSET, LIABILITY, EQUITY, REVENUE, EXPENSE = ["ASSET", "LIABILITY", "EQUITY", "REVENUE", "EXPENSE"]
ACCOUNT_TYPES = [ASSET, LIABILITY, EQUITY, REVENUE, EXPENSE]
DEBIT = "Dr"
CREDIT = "Cr"
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
    normal_balance: Mapped[str] = mapped_column(default=DEBIT)
    type: Mapped[str]

    # schematic relationships
    actions: Mapped["Action"] = relationship()

    # dunders
    def __repr__(self) -> str:
        return "<Account(id={}, name={}, normal_balance={}".format(
            self.id, self.name, self.normal_balance
        )


class Action(Base):
    """
    Implements common elements of all actions
    """
    __tablename__ = "action"

    id = mapped_column(Integer, primary_key=True)
    description: Mapped[str] = mapped_column(String, nullable=True)
    amount: Mapped[float]
    side: Mapped[str]
    order: Mapped[int]

    # schematic relationships
    transaction_id = mapped_column(ForeignKey("transaction.id"))
    transaction: Mapped["Transaction"] = relationship(back_populates="actions")

    account_id = mapped_column(ForeignKey("account.id"))
    account: Mapped["Account"] = relationship(back_populates="actions")

    # dunders
    def __repr__(self):
        return "<Action: (id={}, amount={}, order={}, transaction_id={}, account_id={})".format(
            self.id, self.amount, self.order, self.transaction_id, self.account_id
        )

    def __str__(self):
        return "{} {} {}".format(self.order, self.side, self.amount)


class Transaction(Base):
    """
    Implements common elements of all transactions
    """
    __tablename__ = "transaction"

    id = mapped_column(Integer, primary_key=True)
    time = mapped_column(Float, default=time)

    # schematic relationships
    actions: Mapped[List["Action"]] = relationship()

    def balance(self):
        return (sum((action.amount for action in self.actions if action.side == DEBIT)),
               sum((action.amount for action in self.actions if action.side == CREDIT)))

    # dunders
    def __str__(self):
        retValue = "-----------------------\n"
        for action in self.actions:
            if action.side == DEBIT:
                retValue += str(action) + " | \n"
            elif action.side == CREDIT:
                retValue += "           | " + str(action) + "\n"
        return retValue


if __name__ == "__main__":
    engine = create_engine("sqlite://", echo=True)
    Base.metadata.create_all(engine)
    session = Session(engine)

    transaction = Transaction()

    # initialize some basic accounts
    debitor = Account(name="My Company Accounts Receivable", type=ASSET)
    creditor = Account(name="Your Company Accounts Payable", type=ASSET) #TODO clarify account types
    session.add_all([debitor, creditor, transaction])
    session.commit()

    # create basic line items
    action1 = Action(transaction_id=transaction.id, side=DEBIT, order=1, amount=100.00, account_id=debitor.id)
    action2 = Action(transaction_id=transaction.id, side=CREDIT, order=2, amount=100.00, account_id=creditor.id)
    transaction.actions = [action1, action2]

    print(transaction)
    print(transaction.actions)
    session.add_all([transaction, action1, action2])
    session.commit()

    # print a general ledger and transaction
    print(session.query(Action).filter(Action.side == CREDIT).all())
    print(session.query(Action).filter(Action.side == DEBIT).all())
    print(session.query(Transaction).first())

    # generate standard chart of accounts
    assets, liabilities, revenues, equities = [], [], [], []
    for account in ("Cash", "Accounts Receivable", "Supplies", "Land", "Equipment"):
        assets += [Account(name=account, type=ASSET)]
    for account in ("Notes Payable", "Accounts Payable", "Salaries and Wages Payable",
                    "Interest Payable", "Taxes Payable"):
        liabilities += [Account(name=account, type=LIABILITY, normal_balance=CREDIT)]
    for account in ("Service Revenue", "Sales Revenue",):
        revenues += [Account(name=account, type=REVENUE, normal_balance=CREDIT)]
    for account in ("Common Stock", "Retained Earnings"):
        equities += [Account(name=account, type=EQUITY, normal_balance=CREDIT)]
    session.add_all(assets + liabilities + equities)
    session.commit()
    print(session.query(Account).all())
    print("Complete")
