from accounts import Base, Account, Transaction, Action, DEBIT, CREDIT, ASSET, EQUITY
from sqlalchemy.orm import create_session, Session
from sqlalchemy import create_engine

def fetch_session(engine):
    return create_session(engine)

def raise_cash_from_equity(session, cashaccount, capitalstock, amt):
    transaction = Transaction()
    session.add(transaction)
    session.commit()
    cash = Action(transaction_id=transaction.id, side=DEBIT, order=1, amount=amt, account_id=cashaccount.id)
    equity = Action(transaction_id=transaction.id, side=CREDIT, order=2, amount=amt, account_id=capitalstock.id)
    transaction.actions = [cash, equity]
    session.add_all([cash, equity, transaction])
    session.commit()
    # placeholder return for further design consideration
    return (True, cash, equity, str(transaction))


if __name__ == '__main__':
    engine = create_engine("sqlite://", echo=True)
    Base.metadata.create_all(engine)

    session = fetch_session(engine)
    assert session

    cashaccount = Account(name="Cash", type=ASSET)
    capitalstock = Account(name="Common Stock", type=EQUITY)
    session.add_all([cashaccount, capitalstock])
    session.commit()

    print(raise_cash_from_equity(session, cashaccount, capitalstock, 25000.0, 1.00))
    # print(transaction.balance())
