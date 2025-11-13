from django.urls import path
from SEEVAL_api.views import (
    TopicListCreateView, TopicRetrieveUpdateDestroyView,
    SubtopicListCreateView, SubtopicRetrieveUpdateDestroyView,
    generate_mcqs, topics_with_subtopics, subtopic_details, save_quiz_result, quiz_results
)

urlpatterns = [
    path('api/topics/', TopicListCreateView.as_view(), name='topic-list-create'),
    path('api/topics/<int:pk>/', TopicRetrieveUpdateDestroyView.as_view(), name='topic-detail'),
    path('api/subtopics/', SubtopicListCreateView.as_view(), name='subtopic-list-create'),
    path('api/subtopics/<int:pk>/', SubtopicRetrieveUpdateDestroyView.as_view(), name='subtopic-detail'),
    path('api/topics-with-subtopics/', topics_with_subtopics, name='topics-with-subtopics'),
    path('api/subtopic-details/', subtopic_details, name='subtopic-details'),
    path('api/topic-content/', generate_mcqs, name='get-topic-content'),
    path('api/save-quiz-result/', save_quiz_result, name='save_quiz_result'),
    path('api/quiz-results/', quiz_results),

]
