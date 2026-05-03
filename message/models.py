from django.db import models

class Message(models.Model):
    sender_id = models.BigIntegerField()
    receiver_id = models.BigIntegerField()
    job_id = models.BigIntegerField()

    content = models.TextField()

    is_read = models.BooleanField(default=False)
    is_deleted = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "messages"
        ordering = ["created_at"]
        indexes = [
            models.Index(fields=["job_id"]),
            models.Index(fields=["receiver_id", "is_read"]),
            models.Index(fields=["sender_id", "receiver_id"]),
        ]

    def __str__(self):
        return f"Message {self.id} | Job {self.job_id}"
