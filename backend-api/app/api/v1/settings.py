from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.security import require_admin
from app.db.session import get_db
from app.models.setting import SystemSetting
from app.schemas import SettingRead, SettingUpdate

router = APIRouter(dependencies=[Depends(require_admin)])


@router.get("", response_model=list[SettingRead])
def list_settings(db: Session = Depends(get_db)) -> list[SystemSetting]:
    return db.query(SystemSetting).order_by(SystemSetting.key.asc()).all()


@router.patch("/{key}", response_model=SettingRead)
def update_setting(key: str, payload: SettingUpdate, db: Session = Depends(get_db)) -> SystemSetting:
    setting = db.query(SystemSetting).filter(SystemSetting.key == key).first()
    if setting is None:
        raise HTTPException(status_code=404, detail="setting_not_found")
    setting.value = payload.value
    db.commit()
    db.refresh(setting)
    return setting
