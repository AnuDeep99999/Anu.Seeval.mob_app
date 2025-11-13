from django.contrib import admin
from .models import Topic, Subtopic
# Register your models here.



class SubtopicInline(admin.TabularInline):
    model = Subtopic
    extra = 1

@admin.register(Topic)
class TopicAdmin(admin.ModelAdmin):
    list_display = ['name']
    inlines = [SubtopicInline]

@admin.register(Subtopic)
class SubtopicAdmin(admin.ModelAdmin):
    list_display = ['name', 'topic']