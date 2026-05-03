from app.tasks.email_tasks import send_email_task


def notify_idea_created(users, idea_title: str, board_id: str):
    for user in users:
        send_email_task.delay(
            user.email,
            "Idea Created",
            f"Idea '{idea_title}' created in board {board_id}"
        )