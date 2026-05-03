from app.tasks.email_tasks import send_email_task

def delete_account_event(user_email: str):
    send_email_task.delay(
        user_email,
        "Account Deletion",
        "Your account has been successfully deleted."
    )