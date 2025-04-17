# 任务API
from fastapi import APIRouter, Depends
from app.core.security import get_current_user

router = APIRouter()

@router.post("/tasks")
async def create_task(
    task_data: dict,
    current_user: TokenData = Depends(get_current_user)
):
    """需要认证的API端点"""
    return {
        "user_id": current_user.user_id,
        "task": task_data
    }