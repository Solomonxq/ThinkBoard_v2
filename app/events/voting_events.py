from sqlalchemy import select
from app.db.session import SessionLocal
from app.models.board import Board
from app.tasks.email_tasks import send_email_task


async def notify_voting_finished(
    board_id: str,
    board_name: str,
    idea_id: str,
    result: dict,
):
    async with SessionLocal() as db:
        board = (await db.execute(
            select(Board).where(Board.id == board_id)
        )).scalar_one_or_none()

        if not board:
            return

        for member in board.members:
            send_email_task.delay(
                member.email,
                f"Voting finished in board '{board_name}'",
                f"""
Voting finished!

Board: {board_name}
Idea ID: {idea_id}

Result: {"ACCEPTED" if result["accepted"] else "REJECTED"}

👍 Approve: {result["approve"]}
👎 Reject: {result["reject"]}
                """
            )