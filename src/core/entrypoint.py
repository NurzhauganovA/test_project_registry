import asyncio
import contextlib
import signal
import threading
import typing
from types import FrameType
from typing import Any

from mis_eventer_lib.eventer_consumer import EventerConsumerService

from src.apps.users.infrastructure.kafka.kafka_consumer import UsersKafkaConsumerImpl
from src.core.core_container import CoreContainer
from src.core.logger import logger
from src.core.settings import Settings
from src.core.utils import asyncify, unwire_subcontainers, wire_subcontainers

HANDLED_SIGNALS = (
    signal.SIGINT,  # Unix signal 2. Sent by Ctrl+C.
    signal.SIGTERM,  # Unix signal 15. Sent by `kill <pid>`.
)


class Entrypoint:
    def __init__(
        self,
        *,
        settings: Settings | None = None,
        container: CoreContainer | None = None,
    ):
        self._config = settings or Settings()
        self._container = container or CoreContainer()
        self._container.config.from_dict(self._config.model_dump())
        self._signal_event = asyncio.Event()

        self._users_kafka_consumer: UsersKafkaConsumerImpl | None = None
        self._eventer_consumer_service: EventerConsumerService | None = None
        self._uvicorn_server: Any = None

        # Kafka consumer & Uvicorn tasks
        self._users_kafka_consumer_task: asyncio.Task | None = None
        self._eventer_consumer_task: asyncio.Task | None = None
        self._asgi_server_task: asyncio.Task | None = None

    async def serve(self) -> None:
        with self.capture_signals():
            try:
                await self.startup()
                await self._signal_event.wait()
            finally:
                await self.shutdown()

    def run(self) -> None:
        asyncio.run(self.serve())

    async def startup(self) -> None:
        await asyncify(self._container.init_resources())
        wire_subcontainers(self._container)

        # Get resource-objects
        self._users_kafka_consumer = (
            await self._container.users_container().users_kafka_consumer()
        )
        self._eventer_consumer_service = self._container.eventer_consumer_service()
        self._uvicorn_server = self._container.api_server()

        if self._users_kafka_consumer is None:
            raise RuntimeError(
                "[DEPRECATED] Kafka consumer for users is not initialized!"
            )

        if self._eventer_consumer_service is None:
            RuntimeError("[NEW] Kafka consumer for events is not initialized!")

        # Start Kafka consumers & Uvicorn tasks
        self._users_kafka_consumer_task = asyncio.create_task(
            self._users_kafka_consumer.start()
        )

        self._eventer_consumer_task = asyncio.create_task(
            self._eventer_consumer_service.start()
        )
        logger.info(
            f"Started Eventer Consumer task on topics: {', '.join(self._eventer_consumer_service.topics)}"
        )

        self._asgi_server_task = asyncio.create_task(self._uvicorn_server.serve())

    async def shutdown(self) -> None:
        # Stop Kafka consumer
        if self._users_kafka_consumer is not None:
            await self._users_kafka_consumer.stop()

        if self._eventer_consumer_task is not None:
            self._eventer_consumer_task.cancel()
            with contextlib.suppress(asyncio.CancelledError):
                await self._eventer_consumer_task

        # Stop ASGI-server (Uvicorn) task
        if self._asgi_server_task:
            self._asgi_server_task.cancel()
            with contextlib.suppress(asyncio.CancelledError):
                await self._asgi_server_task

        # Stop Kafka consumer task
        if self._users_kafka_consumer_task:
            self._users_kafka_consumer_task.cancel()
            with contextlib.suppress(asyncio.CancelledError):
                await self._users_kafka_consumer_task

        await asyncify(self._container.shutdown_resources())
        unwire_subcontainers(self._container)

    @contextlib.contextmanager
    def capture_signals(self) -> typing.Generator[None, None, None]:
        # Copyright © 2017-present,
        # Signals can only be listened to from the main thread.
        if threading.current_thread() is not threading.main_thread():
            yield  # pragma: no cover
            return  # pragma: no cover
        # always use signal.signal, even if loop.add_signal_handler is available
        # this allows to restore previous signal handlers later on
        original_handlers = {
            sig: signal.signal(sig, self.handle_exit) for sig in HANDLED_SIGNALS
        }
        try:
            yield
        finally:
            for sig, handler in original_handlers.items():
                signal.signal(sig, handler)

    def handle_exit(self, sig: int, frame: FrameType | None = None) -> None:
        loop = asyncio.get_running_loop()
        if not self._signal_event.is_set():
            loop.call_soon_threadsafe(self._signal_event.set)


if __name__ == "__main__":
    Entrypoint().run()
