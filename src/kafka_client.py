"""Kafka client module for the FTE event bus.

Provides Kafka producer/consumer wrappers using aiokafka, plus an
InMemoryEventBus fallback for local development when Kafka is unavailable.
A factory function ``get_event_bus()`` selects the appropriate backend
based on application configuration.
"""

from __future__ import annotations

import asyncio
import json
import uuid
from typing import Any, Callable, Coroutine, Dict, List, Optional

import structlog
from aiokafka import AIOKafkaConsumer, AIOKafkaProducer

from src.config import settings

logger = structlog.get_logger()

# ---------------------------------------------------------------------------
# Topic definitions
# ---------------------------------------------------------------------------

TOPICS: Dict[str, str] = {
    "tickets_incoming": "fte.tickets.incoming",
    "email_inbound": "fte.channels.email.inbound",
    "whatsapp_inbound": "fte.channels.whatsapp.inbound",
    "webform_inbound": "fte.channels.webform.inbound",
    "escalations": "fte.escalations",
    "metrics": "fte.metrics",
    "dlq": "fte.dlq",
}

# Type alias for the async callback expected by consumers.
MessageCallback = Callable[[str, Any], Coroutine[Any, Any, None]]

# ---------------------------------------------------------------------------
# FTEKafkaProducer
# ---------------------------------------------------------------------------


class FTEKafkaProducer:
    """Async Kafka producer that serialises messages as JSON."""

    def __init__(self, bootstrap_servers: str | None = None) -> None:
        self._bootstrap_servers = bootstrap_servers or settings.KAFKA_BOOTSTRAP_SERVERS
        self._producer: Optional[AIOKafkaProducer] = None

    async def start(self) -> None:
        """Create and start the underlying AIOKafkaProducer."""
        self._producer = AIOKafkaProducer(
            bootstrap_servers=self._bootstrap_servers,
            value_serializer=lambda v: json.dumps(v).encode("utf-8"),
            key_serializer=lambda k: k.encode("utf-8") if k else None,
        )
        await self._producer.start()
        logger.info(
            "kafka_producer.started",
            bootstrap_servers=self._bootstrap_servers,
        )

    async def stop(self) -> None:
        """Flush pending messages and close the producer."""
        if self._producer:
            await self._producer.stop()
            self._producer = None
            logger.info("kafka_producer.stopped")

    async def publish(
        self, topic: str, message: Any, key: Optional[str] = None
    ) -> None:
        """Serialise *message* as JSON and send it to *topic*.

        Parameters
        ----------
        topic:
            Kafka topic name (use a value from ``TOPICS``).
        message:
            Any JSON-serialisable payload.
        key:
            Optional partition key.
        """
        if self._producer is None:
            raise RuntimeError("Producer is not started. Call start() first.")
        try:
            await self._producer.send_and_wait(topic, value=message, key=key)
            logger.debug(
                "kafka_producer.published",
                topic=topic,
                key=key,
            )
        except Exception:
            logger.exception("kafka_producer.publish_failed", topic=topic, key=key)
            raise


# ---------------------------------------------------------------------------
# FTEKafkaConsumer
# ---------------------------------------------------------------------------


class FTEKafkaConsumer:
    """Async Kafka consumer that deserialises JSON messages."""

    def __init__(
        self,
        topics: List[str],
        group_id: str,
        bootstrap_servers: str | None = None,
    ) -> None:
        self._topics = topics
        self._group_id = group_id
        self._bootstrap_servers = bootstrap_servers or settings.KAFKA_BOOTSTRAP_SERVERS
        self._consumer: Optional[AIOKafkaConsumer] = None

    async def start(self) -> None:
        """Create and start the underlying AIOKafkaConsumer."""
        self._consumer = AIOKafkaConsumer(
            *self._topics,
            bootstrap_servers=self._bootstrap_servers,
            group_id=self._group_id,
            value_deserializer=lambda v: json.loads(v.decode("utf-8")),
            auto_offset_reset="earliest",
            enable_auto_commit=True,
        )
        await self._consumer.start()
        logger.info(
            "kafka_consumer.started",
            topics=self._topics,
            group_id=self._group_id,
        )

    async def stop(self) -> None:
        """Stop the consumer and release resources."""
        if self._consumer:
            await self._consumer.stop()
            self._consumer = None
            logger.info("kafka_consumer.stopped", group_id=self._group_id)

    async def consume(self, callback: MessageCallback) -> None:
        """Continuously consume messages and invoke *callback* for each.

        Parameters
        ----------
        callback:
            An async callable ``(topic: str, message: Any) -> None`` invoked
            for every message received.
        """
        if self._consumer is None:
            raise RuntimeError("Consumer is not started. Call start() first.")
        try:
            async for msg in self._consumer:
                try:
                    await callback(msg.topic, msg.value)
                except Exception:
                    logger.exception(
                        "kafka_consumer.callback_error",
                        topic=msg.topic,
                        offset=msg.offset,
                    )
        except Exception:
            logger.exception("kafka_consumer.consume_failed")
            raise


# ---------------------------------------------------------------------------
# InMemoryEventBus  (fallback for local dev / testing)
# ---------------------------------------------------------------------------


class InMemoryEventBus:
    """In-process event bus with the same interface as the Kafka classes.

    Uses one ``asyncio.Queue`` per topic and spawns ``asyncio.Task`` objects
    for consuming.  Useful when Kafka is not available (local dev, CI tests).
    """

    def __init__(self) -> None:
        self._queues: Dict[str, asyncio.Queue[Any]] = {}
        self._handlers: Dict[str, List[MessageCallback]] = {}
        self._tasks: List[asyncio.Task[None]] = []
        self._running: bool = False

    # -- lifecycle -----------------------------------------------------------

    async def start(self) -> None:
        """Mark the bus as running."""
        self._running = True
        logger.info("inmemory_event_bus.started")

    async def stop(self) -> None:
        """Cancel all consumer tasks and drain queues."""
        self._running = False
        for task in self._tasks:
            task.cancel()
        # Wait for graceful cancellation
        if self._tasks:
            await asyncio.gather(*self._tasks, return_exceptions=True)
        self._tasks.clear()
        self._queues.clear()
        self._handlers.clear()
        logger.info("inmemory_event_bus.stopped")

    # -- producer interface --------------------------------------------------

    async def publish(
        self, topic: str, message: Any, key: Optional[str] = None
    ) -> None:
        """Enqueue *message* for all consumers subscribed to *topic*."""
        if not self._running:
            raise RuntimeError("Event bus is not started. Call start() first.")
        queue = self._queues.setdefault(topic, asyncio.Queue())
        await queue.put(message)
        logger.debug(
            "inmemory_event_bus.published",
            topic=topic,
            key=key,
        )

    # -- consumer interface --------------------------------------------------

    async def consume(self, callback: MessageCallback) -> None:
        """Start background tasks that call *callback* for each subscribed topic.

        This registers the callback for every topic that has an existing queue
        and spawns an ``asyncio.Task`` per topic to drain messages.
        """
        if not self._running:
            raise RuntimeError("Event bus is not started. Call start() first.")

        # Ensure every known topic has a queue.
        for topic in TOPICS.values():
            self._queues.setdefault(topic, asyncio.Queue())

        for topic, queue in self._queues.items():
            self._handlers.setdefault(topic, []).append(callback)
            task = asyncio.create_task(
                self._consume_loop(topic, queue, callback),
                name=f"inmemory-consumer-{topic}-{uuid.uuid4().hex[:8]}",
            )
            self._tasks.append(task)
        logger.info("inmemory_event_bus.consuming", topics=list(self._queues.keys()))

    async def _consume_loop(
        self,
        topic: str,
        queue: asyncio.Queue[Any],
        callback: MessageCallback,
    ) -> None:
        """Drain *queue* and invoke *callback* until cancelled."""
        try:
            while self._running:
                try:
                    message = await asyncio.wait_for(queue.get(), timeout=1.0)
                except asyncio.TimeoutError:
                    continue
                try:
                    await callback(topic, message)
                except Exception:
                    logger.exception(
                        "inmemory_event_bus.callback_error",
                        topic=topic,
                    )
        except asyncio.CancelledError:
            logger.debug("inmemory_event_bus.consumer_cancelled", topic=topic)


# ---------------------------------------------------------------------------
# Factory
# ---------------------------------------------------------------------------


_event_bus_instance: Optional[InMemoryEventBus | FTEKafkaProducer] = None


def get_event_bus() -> InMemoryEventBus | FTEKafkaProducer:
    """Return the singleton event-bus backend.

    When ``settings.KAFKA_BOOTSTRAP_SERVERS`` is set to a non-default,
    reachable broker address **and** the environment is not ``development``,
    the real Kafka producer is returned.  Otherwise the lightweight
    ``InMemoryEventBus`` is used so the application can still run without an
    external broker.
    """
    global _event_bus_instance
    if _event_bus_instance is not None:
        return _event_bus_instance

    use_kafka = (
        settings.KAFKA_BOOTSTRAP_SERVERS
        and settings.KAFKA_BOOTSTRAP_SERVERS != "localhost:9092"
        and settings.ENVIRONMENT != "development"
    )

    if use_kafka:
        logger.info(
            "event_bus.using_kafka",
            bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS,
        )
        _event_bus_instance = FTEKafkaProducer(bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS)
    else:
        logger.info("event_bus.using_inmemory_fallback")
        _event_bus_instance = InMemoryEventBus()

    return _event_bus_instance
