from rest_framework import serializers
from .models import Topic, Subtopic, QuizResult

class SubtopicSerializer(serializers.ModelSerializer):
    topic_name = serializers.ReadOnlyField(source='topic.name')  # Show topic name instead of ID

    class Meta:
        model = Subtopic
        fields = ['id', 'topic_name', 'name', 'description']  # Added description field

class TopicSerializer(serializers.ModelSerializer):
    subtopics = SubtopicSerializer(many=True, read_only=True)  # Show related subtopics

    class Meta:
        model = Topic
        fields = ['id', 'name', 'subtopics']
        
        
        
class QuizResultSerializer(serializers.ModelSerializer):
    topic = serializers.SlugRelatedField(
        slug_field='name',
        queryset=Topic.objects.all()
    )
    subtopic = serializers.SlugRelatedField(
        slug_field='name',
        queryset=Subtopic.objects.all()
    )

    class Meta:
        model = QuizResult
        fields = ['topic', 'subtopic', 'score', 'total']