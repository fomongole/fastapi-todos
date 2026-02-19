import asyncio
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from app.database.session import SessionLocal 
from app.todos.models import Todo
from app.users.models import User
from app.core.notifications import send_push_notification
from loguru import logger

async def process_reminders():
    """
    Background task checking for reminders due in the next minute.
    STRICTLY uses UTC for cross-timezone reliability.
    """
    while True:
        db: Session = SessionLocal()
        try:
            # Always get the current time in UTC
            now = datetime.now(timezone.utc)
            
            # Find uncompleted todos where reminder_time is now or passed
            due_todos = db.query(Todo).join(User).filter(
                Todo.reminder_time <= now,
                Todo.notification_sent == False,
                Todo.completed == False,
                User.fcm_token != None
            ).all()

            for todo in due_todos:
                logger.info(f"Processing reminder for task: {todo.id}")
                await send_push_notification(
                    token=todo.owner.fcm_token,
                    title="Task Reminder 🔔",
                    body=f"Don't forget: {todo.title}"
                )
                # Mark as sent to prevent duplicate notifications
                todo.notification_sent = True
            
            db.commit()
        except Exception as e:
            logger.error(f"Reminder Worker Error: {e}")
        finally:
            db.close()
            
        # Standard 1-minute interval for reminder checks
        await asyncio.sleep(60)