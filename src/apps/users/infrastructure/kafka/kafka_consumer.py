import json
from typing import Any, Dict, List, Optional
from uuid import UUID

from aiokafka import AIOKafkaConsumer

from src.apps.users.domain.enums import ActionsOnUserEnum
from src.apps.users.infrastructure.schemas.user_schemas import UserSchema
from src.apps.users.interfaces.kafka_consumer_interface import KafkaConsumerInterface
from src.apps.users.services.user_service import UserService
from src.core.logger import LoggerService


class UsersKafkaConsumerImpl(KafkaConsumerInterface):
    def __init__(
        self,
        user_service: UserService,
        bootstrap_servers: List[str],
        topic: str,
        logger: LoggerService,
        group_id: Optional[str] = "registry-service-users-group",
    ):
        self.user_service = user_service
        self.bootstrap_servers = bootstrap_servers
        self.topic = topic
        self.group_id = group_id
        self._logger = logger
        self.consumer = None
        self._running = False

    async def start(self):
        self._logger.info("Starting Kafka consumer...")
        self.consumer = AIOKafkaConsumer(
            self.topic,
            bootstrap_servers=self.bootstrap_servers,
            value_deserializer=lambda message: json.loads(message.decode("utf-8")),
            group_id=self.group_id,
            enable_auto_commit=True,
        )
        await self.consumer.start()
        self._running = True
        try:
            await self.consume()
        finally:
            await self.consumer.stop()

    async def stop(self):
        self._running = False
        if self.consumer:
            await self.consumer.stop()
            self._logger.info("Kafka consumer stopped.")

    async def consume(self):
        self._logger.info(f"Consuming topic '{self.topic}'")
        async for msg in self.consumer:
            if not self._running:
                break
            try:
                await self.handle_event(msg.value)
            except Exception as err:
                error_message = f"Error while handling a message: {err}"
                self._logger.error(error_message)
                continue

    async def handle_event(self, event: Dict[str, Any]):
        action_type = event.get("action_type")
        user_id = event.get("sub")
        payload = event.get("payload", {})

        try:
            action_enum = ActionsOnUserEnum(action_type)
        except ValueError:
            self._logger.critical(
                f" - KAFKA: Unknown action type received "
                f"from the Auth Service: '{action_type}'."
            )
            self._logger.info("Skipping this event. Unknown action type was received.")
            return

        # For creation and update, we form a user schema, for delete - only ID
        if action_enum in (ActionsOnUserEnum.CREATE, ActionsOnUserEnum.UPDATE):
            user_data = UserSchema(
                id=UUID(user_id),
                first_name=payload["first_name"],
                last_name=payload["last_name"],
                middle_name=payload.get("middle_name"),
                iin=payload["iin"],
                date_of_birth=payload["date_of_birth"],
                client_roles=payload["client_roles"],
                enabled=payload["enabled"],
                specializations=payload["specializations"],
                served_patient_types=payload["served_patient_types"],
                served_referral_types=payload["served_referral_types"],
                served_referral_origins=payload["served_referral_origins"],
                served_payment_types=payload["served_payment_types"],
            )
        elif action_enum == ActionsOnUserEnum.DELETE:
            user_data = UUID(user_id)
        else:
            self._logger.info("Skipping this event. Unknown action type was received.")
            return

        await self.user_service.handle_event(action=action_enum, user_data=user_data)

        self._logger.debug(f"Handled user action '{action_type}'. ID: '{user_id}'.")
