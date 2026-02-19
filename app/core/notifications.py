import firebase_admin
from firebase_admin import credentials, messaging
from loguru import logger

# Initialize Firebase
try:
    if not firebase_admin._apps:
        cred = credentials.Certificate("serviceAccountKey.json")
        firebase_admin.initialize_app(cred)
except Exception as e:
    logger.warning(f"Firebase initialization failed (Check credentials): {e}")

async def send_push_notification(token: str, title: str, body: str):
    """Sends a push notification payload to a specific device via FCM."""
    if not token:
        return
        
    message = messaging.Message(
        notification=messaging.Notification(
            title=title,
            body=body,
        ),
        token=token,
    )
    
    try:
        response = messaging.send(message)
        logger.info(f"FCM Notification sent successfully: {response}")
    except Exception as e:
        logger.error(f"Error sending FCM notification: {e}")