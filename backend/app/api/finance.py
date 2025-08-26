from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.deps import get_current_org, get_current_user_in_org, get_db
from app.models.organization import Organization
from app.models.user import User
from app.models.finance import Account
from app.schemas.finance import (
    AccountPublic,
    FinancialTransactionCreate,
    FinancialTransactionPublic,
)
from app.services.finance_service import (
    FinanceServiceError,
    record_transaction,
)

router = APIRouter(prefix="/finance", tags=["finance"])


@router.post(
    "/transactions",
    response_model=FinancialTransactionPublic,
    status_code=status.HTTP_201_CREATED,
)
def create_transaction(
    data: FinancialTransactionCreate,
    db: Session = Depends(get_db),
    org: Organization = Depends(get_current_org),
    user: User = Depends(get_current_user_in_org),
):
    account = (
        db.query(Account)
        .filter(Account.id == data.account_id, Account.organization_id == org.id)
        .first()
    )
    if not account:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="account_not_found")
    try:
        tx = record_transaction(db, data, user)
    except FinanceServiceError as e:
        if str(e) == "forbidden":
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="forbidden")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="account_not_found")
    return tx


@router.get("/accounts", response_model=list[AccountPublic])
def list_accounts(
    db: Session = Depends(get_db),
    org: Organization = Depends(get_current_org),
    user: User = Depends(get_current_user_in_org),
):
    accounts = db.query(Account).filter(Account.organization_id == org.id).all()
    return accounts
