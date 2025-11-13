from django.db import models

# Create your models here.
class QuestionBank(models.Model):
    id = models.AutoField(primary_key=True)
    Course = models.CharField(max_length=50, default="Python")
    Course_Level = models.CharField(max_length=50, default="Basic")
    Level = models.CharField(max_length=50)
    Topic = models.CharField(max_length=100)
    Sub_Topic = models.CharField(max_length=100)
    Question = models.TextField()
    Options = models.TextField(max_length=255)
    OptionA = models.CharField(max_length=255)
    OptionB = models.CharField(max_length=255)
    OptionC = models.CharField(max_length=255)
    OptionD = models.CharField(max_length=255)
    Answer_option = models.CharField(max_length=255)
    Correct_answer = models.CharField(max_length=255)
    def __str__(self):
        return self.Question
    