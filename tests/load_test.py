"""Load tests using Locust."""

from locust import HttpUser, task, between


class WebFormUser(HttpUser):
    """Simulate web form submissions."""

    weight = 3
    wait_time = between(1, 3)

    @task(3)
    def submit_form(self):
        """Submit a support form."""
        self.client.post("/support/submit", json={
            "name": "Load Test User",
            "email": f"loadtest-{__import__('uuid').uuid4().hex[:8]}@example.com",
            "subject": "Load test support request",
            "category": "feature_question",
            "priority": "medium",
            "message": "This is a load test message to verify system performance under load.",
        })

    @task(1)
    def check_ticket(self):
        """Check a ticket status."""
        self.client.get("/support/ticket/TKT-20260223-LOAD01")


class HealthCheckUser(HttpUser):
    """Simulate health check monitoring."""

    weight = 1
    wait_time = between(2, 5)

    @task
    def health_check(self):
        """Hit the health endpoint."""
        self.client.get("/health")


class MetricsUser(HttpUser):
    """Simulate metrics dashboard."""

    weight = 1
    wait_time = between(5, 10)

    @task
    def get_metrics(self):
        """Fetch channel metrics."""
        self.client.get("/metrics/channels")

    @task
    def get_metrics_filtered(self):
        """Fetch email-specific metrics."""
        self.client.get("/metrics/channels?channel=email")
