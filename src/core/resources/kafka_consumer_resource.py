from typing import List

from mis_eventer_lib.eventer_consumer import EventerConsumerService, EventerListener


def EventerConsumerResource(
    *topics: str,
    bootstrap_servers: str | List[str],
    listeners: List[EventerListener],
    group_id: str | None = None,
    start_thread: bool = True,
) -> EventerConsumerService:

    consumer = EventerConsumerService(
        *topics,
        bootstrap_servers=bootstrap_servers,
        listeners=listeners,
        group_id=group_id,
    )

    # An attribute for easy access to topics
    consumer.topics = list(topics)

    if start_thread:
        consumer.run_in_thread()

    return consumer
