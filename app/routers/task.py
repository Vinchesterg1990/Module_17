from fastapi import APIRouter
from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session
from app.backend.db_depends import get_db
from typing import Annotated
from app.models.task import Task
from app.models.user import User
from app.schemas import CreateTask, UpdateTask
from sqlalchemy import insert, select, update, delete
from slugify import slugify


router = APIRouter(prefix='/task', tags=['task'])


@router.get('/')
async def all_tasks(db: Annotated[Session, Depends(get_db)]):
    res = db.execute(select(Task))
    tasks = res.scalars().all()
    return tasks


@router.get('/task_id')
async def task_by_id(db: Annotated[Session, Depends(get_db)],
                     task_id: int):
    query = select(Task).where(Task.id == task_id)
    task = db.scalar(query)
    if task is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Not found"
        )
    else:
        return task


@router.post('/create')
async def create_task(db: Annotated[Session, Depends(get_db)],
                      task: CreateTask, user_id: int):
    query = select(User).where(User.id == user_id)
    user = db.scalar(query)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User was not found"
        )

    stmt = insert(Task).values(
        title=task.title,
        content=task.content,
        priority=task.priority,
        user_id=user_id,
        slug=slugify(task.title)
    )
    db.execute(stmt)
    db.commit()
    return {
        'status_code': status.HTTP_201_CREATED,
        'transaction': 'Successful'
    }


@router.put('/update')
async def update_task(db: Annotated[Session, Depends(get_db)],
                      up_task: UpdateTask, task_id: int):
    query = select(User).where(Task.id == task_id)
    task = db.scalar(query)
    if task is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Not found"
        )

    stmt = update(Task).where(Task.id == task_id).values(
        title=up_task.title,
        content=up_task.content,
        priority=up_task.priority,
        slug=slugify(up_task.title)
    )
    db.execute(stmt)
    db.commit()
    return {
        'status_code': status.HTTP_200_OK,
        'transaction': 'Task update is successful!'
    }


@router.delete('/delete')
async def delete_task(db: Annotated[Session, Depends(get_db)],
                      task_id: int):
    query = select(Task).where(Task.id == task_id)
    task = db.scalar(query)
    if task is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Not found"
        )
    stmt = delete(Task).where(Task.id == task_id)
    db.execute(stmt)
    db.commit()
    return {
        'status_code': status.HTTP_200_OK,
        'transaction': 'Task deleted!'
    }