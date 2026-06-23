from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from src.db.dependencies import get_current_user, get_db
from src.models.budget import Budget
from src.models.category import Category
from src.models.user import User
from src.schemas.budget import BudgetCreate, BudgetRead


router = APIRouter(prefix="/budgets", tags=["budgets"])


@router.post(
    "/",
    response_model=BudgetRead,
    status_code=status.HTTP_201_CREATED,
)
def create_budget(
    data: BudgetCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    category = (
        db.query(Category)
        .filter(
            Category.id == data.category_id,
            Category.user_id == current_user.id,
        )
        .first()
    )

    if category is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found",
        )

    new_budget = Budget(
        user_id=current_user.id,
        **data.model_dump(),
    )

    db.add(new_budget)

    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A budget already exists for this category and period",
        ) from exc

    db.refresh(new_budget)
    return new_budget