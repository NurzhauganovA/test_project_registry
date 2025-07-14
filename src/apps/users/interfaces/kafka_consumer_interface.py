from abc import ABC, abstractmethod
from typing import Any, Dict


class KafkaConsumerInterface(ABC):
    @abstractmethod
    async def start(self):
        """Starts the Kafka consumer."""
        pass

    @abstractmethod
    async def stop(self):
        """Stops the Kafka consumer."""
        pass

    @abstractmethod
    async def consume(self):
        """
        Consumes messages from the Kafka topic.

        :raises KafkaEventHandlingError: If an error occurs during message consumption.
        """
        pass

    @abstractmethod
    async def handle_event(self, event: Dict[str, Any]):
        """
        Handles an incoming event from the Kafka topic.
        """
        pass
