from django.db import models

class ContactMessage(models.Model):
    SERVICE_CHOICES = [
        ("web_dev", "Web Development"),
        ("mobile_dev", "Mobile App Development"),
        ("online_courses", "Online Courses"),
    ]

    full_name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    services = models.JSONField(default=list)  # list of selected services
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.full_name} - {self.email}"

