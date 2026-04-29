from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.dependencies import get_db, require_admin, require_superuser
from app.models.user import User
from app.schemas.poll import PollCreate, PollUpdate, PollOut, PollWithOptions
from app.schemas.option import OptionCreate, OptionOut
from app.schemas.user import UserOut, UserRoleUpdate
from app.services.poll_service import PollService
from app.repositories.user_repository import UserRepository

router = APIRouter(prefix="/admin", tags=["Admin"])


# ─────────────────────────────────────────
# Poll boshqaruvi  (admin + superuser)
# ─────────────────────────────────────────

@router.get("/polls", response_model=list[PollWithOptions])
def list_all_polls(
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),
):
    """Admin: barcha polllar (draft + active + closed) + variantlari"""
    return PollService(db).get_all_polls_with_options()


@router.post("/polls", response_model=PollWithOptions, status_code=status.HTTP_201_CREATED)
def create_poll(
    payload: PollCreate,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),
):
    return PollService(db).create_poll(payload, admin.id)


@router.put("/polls/{poll_id}", response_model=PollOut)
def update_poll(
    poll_id: int,
    payload: PollUpdate,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),
):
    return PollService(db).update_poll(poll_id, payload)


@router.delete("/polls/{poll_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_poll(
    poll_id: int,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),
):
    PollService(db).delete_poll(poll_id)


@router.post("/polls/{poll_id}/start", response_model=PollOut)
def start_poll(
    poll_id: int,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),
):
    return PollService(db).start_poll(poll_id)


@router.post("/polls/{poll_id}/stop", response_model=PollOut)
def stop_poll(
    poll_id: int,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),
):
    return PollService(db).stop_poll(poll_id)


@router.post("/polls/{poll_id}/options", response_model=OptionOut, status_code=status.HTTP_201_CREATED)
def add_option(
    poll_id: int,
    payload: OptionCreate,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),
):
    return PollService(db).add_option(poll_id, payload.text)


@router.delete("/polls/{poll_id}/options/{option_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_option(
    poll_id: int,
    option_id: int,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),
):
    PollService(db).delete_option(poll_id, option_id)


@router.get("/users", response_model=list[UserOut])
def list_users(
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),
):
    return UserRepository(db).get_all()


# ─────────────────────────────────────────
# Foydalanuvchi boshqaruvi  (faqat superuser)
# ─────────────────────────────────────────

@router.patch("/users/{user_id}/role", response_model=UserOut)
def change_user_role(
    user_id: int,
    payload: UserRoleUpdate,
    db: Session = Depends(get_db),
    superuser: User = Depends(require_superuser),
):
    """Superuser istalgan foydalanuvchining rolini o'zgartiradi"""
    user = UserRepository(db).get(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Foydalanuvchi topilmadi")
    if user.id == superuser.id:
        raise HTTPException(status_code=400, detail="O'z rolingizni o'zgartira olmaysiz")

    user.role = payload.role.value
    db.commit()
    db.refresh(user)
    return user


@router.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    superuser: User = Depends(require_superuser),
):
    """Superuser admin yoki oddiy foydalanuvchini o'chiradi"""
    user = UserRepository(db).get(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Foydalanuvchi topilmadi")
    if user.id == superuser.id:
        raise HTTPException(status_code=400, detail="O'zingizni o'chira olmaysiz")
    if user.role == "superuser":
        raise HTTPException(status_code=403, detail="Boshqa superuserni o'chirib bo'lmaydi")

    UserRepository(db).delete(user_id)
