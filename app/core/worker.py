import asyncio
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from app.database.session import SessionLocal
from app.todos.models import Todo
from app.users.models import User
from app.core.notifications import send_push_notification
from loguru import logger

async def process_reminders():
    """Background task checking for reminders due in the next minute."""
    while True:
        db: Session = SessionLocal()
        try:
            now = datetime.now(timezone.utc)
            
            # Find uncompleted todos where reminder_time is now or passed, and notification hasn't been sent
            due_todos = db.query(Todo).join(User).filter(
                Todo.reminder_time <= now,
                Todo.notification_sent == False,
                Todo.completed == False,
                User.fcm_token != None
            ).all()

            for todo in due_todos:
                logger.info(f"Sending background reminder for task ID: {todo.id}")
                await send_push_notification(
                    token=todo.owner.fcm_token,
                    title="Task Reminder 🔔",
                    body=f"Don't forget: {todo.title}"
                )
                todo.notification_sent = True
            
            db.commit()
        except Exception as e:
            logger.error(f"Reminder Worker Error: {e}")
        finally:
            db.close()
            
        # Sleep for 60 seconds before checking the database again
        await asyncio.sleep(60)