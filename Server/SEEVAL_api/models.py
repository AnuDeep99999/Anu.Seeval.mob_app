from django.db import models
from django.conf import settings

class Topic(models.Model):
    name = models.CharField(max_length=100, unique=True)  # Prevent duplicate topic names

    def __str__(self):
        return self.name


class Subtopic(models.Model):
    topic = models.ForeignKey(Topic, related_name='subtopics', on_delete=models.CASCADE)
    name = models.CharField(max_length=100, unique=True)  # Ensure subtopic names are unique
    description = models.TextField(blank=True, null=True)  # Store detailed descriptions

    def __str__(self):
        return f"{self.topic.name} - {self.name}"
    
    
    
class QuizResult(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='quiz_results')
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE)
    subtopic = models.ForeignKey(Subtopic, on_delete=models.CASCADE)
    score = models.PositiveIntegerField()
    total = models.PositiveIntegerField()
    date_taken = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user} - {self.topic.name}/{self.subtopic.name} - Score: {self.score}/{self.total}"
    