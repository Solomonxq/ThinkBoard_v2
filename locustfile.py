import random
import string
from datetime import datetime, timezone, timedelta

from locust import HttpUser, between, task


def random_string(length=8):
    return "".join(random.choices(string.ascii_lowercase, k=length))


class ThinkBoardUser(HttpUser):
    wait_time = between(1, 3)
    token = None
    board_id = None

    def on_start(self):
        email = f"{random_string()}@test.com"
        password = "TestPass123!"
        username = random_string(10)

        reg = self.client.post("/auth/register", json={
            "email": email,
            "username": username,
            "password": password,
        })

        if reg.status_code != 200:
            self.headers = {}
            return

        response = self.client.post("/auth/login", json={
            "email": email,
            "password": password,
        })

        if response.status_code == 200:
            self.token = response.json().get("access_token")
            self.headers = {"Authorization": f"Bearer {self.token}"}
        else:
            self.headers = {}
            return

        response = self.client.post("/boards/create", json={
            "board_name": random_string(6),
            "access": True,
            "description": "Test board for load testing",
        }, headers=self.headers)

        if response.status_code == 200:
            self.board_id = response.json().get("id")
        else:
            self.board_id = None

    @task(3)
    def get_profile(self):
        self.client.get("/profile/me", headers=self.headers)

    @task(3)
    def get_auth_me(self):
        self.client.get("/auth/me", headers=self.headers)

    @task(2)
    def create_board(self):
        self.client.post("/boards/create", json={
            "board_name": random_string(6),
            "access": True,
            "description": "Load test board",
        }, headers=self.headers)

    @task(2)
    def create_idea(self):
        if not self.board_id:
            return
        self.client.post(
            f"/boards/{self.board_id}/ideas/create",
            json={
                "title": random_string(10),
                "description": "Load test idea",
                "voting_ends_at": (datetime.now(timezone.utc) + timedelta(minutes=10)).isoformat(),
            },
            headers=self.headers,
        )

    @task(1)
    def get_public_profile(self):
        self.client.get("/profile/me", headers=self.headers)