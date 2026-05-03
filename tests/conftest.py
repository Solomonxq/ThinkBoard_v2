from unittest.mock import patch
import pytest


@pytest.fixture(autouse=True)
def disable_celery_delay():
    with patch("app.tasks.email_tasks.send_email_task.delay"):
        yield
