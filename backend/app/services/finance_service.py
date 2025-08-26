from uuid import uuid4
from decimal import Decimal

from sqlalchemy.orm import Session

from app.models.finance import Account, FinancialTransaction
from app.models.user import User
from app.models.user_org import UserOrganization
from app.schemas.finance import FinancialTransactionCreate


class FinanceServiceError(Exception):
    pass


def record_transaction(
    db: Session, data: FinancialTransactionCreate, current_user: User
) -> FinancialTransaction:
    account = db.query(Account).filter(Account.id == data.account_id).first()
    if not account:
        raise FinanceServiceError("account_not_found")

    membership = (
        db.query(UserOrganization)
        .filter(
            UserOrganization.user_id == current_user.id,
            UserOrganization.org_id == account.organization_id,
        )
        .first()
    )
    if not membership:
        raise FinanceServiceError("forbidden")

    tx = FinancialTransaction(
        id=uuid4(),
        organization_id=account.organization_id,
        account_id=data.account_id,
        partner_id=data.partner_id,
        order_id=data.order_id,
        direction=data.direction,
        amount=data.amount,
        transaction_date=data.transaction_date,
        description=data.description,
        method=data.method,
    )

    current_balance = account.current_balance or Decimal("0")
    if data.direction == "IN":
        account.current_balance = current_balance + data.amount
    else:
        account.current_balance = current_balance - data.amount

    db.add(tx)
    db.add(account)
    db.commit()
    db.refresh(tx)
    return tx
