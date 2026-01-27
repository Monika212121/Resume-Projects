from typing import Optional, Dict, Any

from src.common.logging import logger
from src.common.alerts_and_notifications.alert_types import AlertType
from src.common.alerts_and_notifications.notification_types import NotificationType


class AlertNotifier:
    def __init__(self):
        pass


    def raise_alert(self, alert_type: AlertType, message: str, metadata: Optional[Dict[Any, Any]]):
        logger.warning(f"[ALERT] {alert_type.value} | {message} | meta = {metadata}")


    def raise_notification(self, notification_type: NotificationType, message: str, metadata: Optional[Dict[Any, Any]]):
        logger.warning(f"[NOTIFICATION] {notification_type.value} | {message} | meta = {metadata}")
