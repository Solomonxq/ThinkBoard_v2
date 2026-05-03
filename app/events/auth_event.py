from app.tasks.email_tasks import send_email_task

def login_event(user_email: str):
    send_email_task.delay(
        user_email,
        "Login Notification",
        "You have successfully logged in."
    )

def registration_event(user_email: str):
    send_email_task.delay(
        user_email,
        "Welcome to the ThinkBoard!",
        "Thank you for registering! We're excited to have you on board."
    )

def password_reset_event(user_email: str):
    send_email_task.delay(
        user_email,
        "Password Reset",
        "Your password has been successfully reset."
    )
