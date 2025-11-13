# SEEVAL_api/views.py
# ---------------- IMPORTS ---------------- #

from rest_framework import generics
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.authentication import JWTAuthentication

from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.http import JsonResponse
from django.shortcuts import get_object_or_404

import json
import re
import threading
import concurrent.futures
import requests
import random
import traceback

from .models import Topic, Subtopic, QuizResult
from .serializers import TopicSerializer, SubtopicSerializer, QuizResultSerializer
from qb_bank.models import QuestionBank
from django.conf import settings
from rest_framework import status


# ---------------- Topic & Subtopic Views ---------------- #

class TopicListCreateView(generics.ListCreateAPIView):
    queryset = Topic.objects.prefetch_related('subtopics').all()
    serializer_class = TopicSerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]


class TopicRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Topic.objects.prefetch_related('subtopics').all()
    serializer_class = TopicSerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]


class SubtopicListCreateView(generics.ListCreateAPIView):
    queryset = Subtopic.objects.select_related('topic').all()
    serializer_class = SubtopicSerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]


class SubtopicRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Subtopic.objects.select_related('topic').all()
    serializer_class = SubtopicSerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]


# ---------------- MCQ Generator ---------------- #

@csrf_exempt
@require_POST
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def generate_mcqs(request):
    """
    Endpoint: POST /api/topic-content/
    Body: {"course": "...", "topic": "...", "subtopic": "..."}
    Tries Mistral/OpenRouter first (robust parsing), falls back to QuestionBank.
    """
    try:
        try:
            data = json.loads(request.body)
        except Exception:
            return JsonResponse({"error": "Invalid JSON in request body"}, status=400)

        course = data.get("course", "").strip()
        topic = data.get("topic", "").strip()
        subtopic = data.get("subtopic", "").strip()

        if not course or not topic or not subtopic:
            return JsonResponse({"error": "Course, topic, and subtopic are required."}, status=400)

        print(f"🔍 Request received for MCQs — Course: '{course}', Topic: '{topic}', Subtopic: '{subtopic}'")

        # NOTE: double braces used to render a JSON-like literal in f-string
        prompt = (
            f"Return exactly 10 multiple choice questions as a valid JSON array for the subtopic '{subtopic}' "
            f"under the topic '{topic}' in the course '{course}'. Each question must be in this format: "
            '{{"question": "...", "options": ["...", "...", "...", "..."], "answer": "..."}}. '
            "Only return a valid JSON array — no explanations, no markdown, no code block markers."
        )

        def call_mistral_and_parse():
            """Call OpenRouter / Mistral and return validated list of MCQs or None on failure."""
            try:
                print("📡 Calling Mistral / OpenRouter API...")
                headers = {
                    "Authorization": f"Bearer {settings.OPENROUTER_API_KEY}",
                    "Content-Type": "application/json",
                }
                body = {
                    "model": "mistralai/mistral-small-3.1-24b-instruct:free",
                    "messages": [{"role": "user", "content": prompt}]
                }

                response = requests.post(
                    "https://openrouter.ai/api/v1/chat/completions",
                    headers=headers,
                    json=body,
                    timeout=30
                )

                # Try to parse JSON; fallback to raw text
                raw_json = None
                raw_text = ""
                try:
                    raw_json = response.json()
                    raw_text = json.dumps(raw_json)[:20000]
                except Exception:
                    raw_json = None
                    raw_text = response.text[:20000]

                print(f"📥 Mistral status={response.status_code} body={raw_text}")

                if not response.ok:
                    print("⚠️ Mistral returned non-OK status:", response.status_code)
                    return None

                # Collect candidate text outputs from several common shapes
                candidates = []

                # 1) OpenAI-style: choices -> [ { message: { content: "..." } } ] or choices[].text
                if isinstance(raw_json, dict):
                    choices = raw_json.get("choices")
                    if isinstance(choices, list) and choices:
                        for ch in choices:
                            if isinstance(ch, dict):
                                msg = ch.get("message") or {}
                                if isinstance(msg, dict):
                                    text = msg.get("content")
                                    if text:
                                        candidates.append(text)
                                # older shape
                                text2 = ch.get("text")
                                if text2:
                                    candidates.append(text2)

                # 2) other shapes: results/outputs/generations/data
                for key in ("results", "outputs", "generations", "data"):
                    if isinstance(raw_json, dict) and key in raw_json:
                        arr = raw_json.get(key) or []
                        if isinstance(arr, list):
                            for item in arr:
                                if isinstance(item, dict):
                                    for candidate_field in ("content", "output", "text"):
                                        t = item.get(candidate_field)
                                        if t:
                                            candidates.append(t)
                                elif isinstance(item, str):
                                    candidates.append(item)

                # 3) regex-fallback: look for JSON array inside response.text
                if not candidates:
                    text_body = response.text
                    match = re.search(r"(\[\s*\{.*?\}\s*\])", text_body, re.DOTALL)
                    if match:
                        candidates.append(match.group(1))
                    else:
                        candidates.append(text_body)

                # Parse candidates into structured mcqs
                parsed_mcqs = []
                for cand in candidates:
                    if not isinstance(cand, str):
                        continue
                    try:
                        cand = cand.strip()
                        if cand.startswith("["):
                            arr = json.loads(cand)
                            if isinstance(arr, list):
                                for q in arr:
                                    if (isinstance(q, dict)
                                            and "question" in q and "options" in q and "answer" in q):
                                        opts = q.get("options") or []
                                        if isinstance(opts, list) and len(opts) == 4:
                                            parsed_mcqs.append({
                                                "question": str(q["question"]).strip(),
                                                "options": [str(o).strip() for o in opts],
                                                "answer": str(q["answer"]).strip()
                                            })
                                if parsed_mcqs:
                                    break
                    except Exception:
                        # not JSON -> continue to text parsing
                        pass

                    # naive text parsing fallback
                    lines = [ln.strip() for ln in cand.splitlines() if ln.strip()]
                    cur_q = None
                    cur_opts = []
                    for line in lines:
                        if re.match(r"^\d+[\).\s]", line):
                            if cur_q and len(cur_opts) == 4:
                                parsed_mcqs.append({"question": cur_q, "options": cur_opts, "answer": ""})
                            cur_q = re.sub(r"^\d+[\).\s]+", "", line).strip()
                            cur_opts = []
                            continue
                        m = re.match(r"^[a-dA-D][\)\.\-]\s*(.*)", line)
                        if m:
                            cur_opts.append(m.group(1).strip())
                            continue
                        if line.startswith("- "):
                            cur_opts.append(line[2:].strip())
                    if cur_q and len(cur_opts) == 4:
                        parsed_mcqs.append({"question": cur_q, "options": cur_opts, "answer": ""})

                # Validate and normalize parsed_mcqs
                validated = []
                for item in parsed_mcqs:
                    if not item.get("question") or not isinstance(item.get("options"), list):
                        continue
                    opts = item["options"]
                    if len(opts) != 4:
                        continue
                    ans = item.get("answer", "") or ""
                    if ans and ans not in opts:
                        if isinstance(ans, str) and re.match(r"^[a-dA-D]$", ans.strip()):
                            idx = ord(ans.strip().lower()) - ord("a")
                            if 0 <= idx < len(opts):
                                ans = opts[idx]
                            else:
                                ans = ""
                        else:
                            ans = ""
                    validated.append({"question": item["question"], "options": opts, "answer": ans})

                if len(validated) < 5:
                    print(f"⚠️ Parsed only {len(validated)} validated MCQs from Mistral")
                    return None

                random.shuffle(validated)
                return validated[:10]

            except requests.exceptions.Timeout:
                print("❌ Mistral request timed out")
                return None
            except requests.exceptions.RequestException as rexc:
                print("❌ Mistral request exception:", rexc)
                return None
            except Exception as exc:
                print("❌ Unexpected parsing error from Mistral:", exc)
                return None

        # Run Mistral call with a thread-level timeout
        with concurrent.futures.ThreadPoolExecutor() as executor:
            future = executor.submit(call_mistral_and_parse)
            try:
                mcqs_from_mistral = future.result(timeout=20)
            except concurrent.futures.TimeoutError:
                print("⏳ Mistral call timed out (thread level)")
                mcqs_from_mistral = None

        if mcqs_from_mistral:
            # Persist unique MCQs in background
            def save_to_db_async(mcqs_list):
                try:
                    print("💾 Saving unique MCQs to local DB...")
                    new_mcqs = 0
                    for q in mcqs_list:
                        question_text = q["question"].strip()
                        exists = QuestionBank.objects.filter(
                            Course=course,
                            Topic=topic,
                            Sub_Topic=subtopic,
                            Question__iexact=question_text
                        ).exists()
                        if not exists:
                            QuestionBank.objects.create(
                                Course=course,
                                Course_Level="Basic",
                                Level="AI",
                                Topic=topic,
                                Sub_Topic=subtopic,
                                Question=question_text,
                                Options=json.dumps(q["options"]),
                                OptionA=q["options"][0],
                                OptionB=q["options"][1],
                                OptionC=q["options"][2],
                                OptionD=q["options"][3],
                                Answer_option=q["answer"] or "",
                                Correct_answer=q["answer"] or ""
                            )
                            new_mcqs += 1
                    print(f"✅ {new_mcqs} new MCQs saved to DB (duplicates skipped).")
                except Exception:
                    print("⚠️ Error saving MCQs to DB:")
                    traceback.print_exc()

            threading.Thread(target=save_to_db_async, args=(mcqs_from_mistral,)).start()
            print("🎯 Returning fresh MCQs from Mistral")
            return JsonResponse({"content": mcqs_from_mistral, "source": "mistral"}, status=200)

        # DB fallback
        fallback_qs = QuestionBank.objects.filter(Course=course, Topic=topic, Sub_Topic=subtopic).order_by('?')[:10]
        if fallback_qs.exists():
            print("📁 Using fallback — MCQs from local DB")
            payload = [
                {
                    "question": q.Question,
                    "options": [q.OptionA, q.OptionB, q.OptionC, q.OptionD],
                    "answer": q.Correct_answer
                } for q in fallback_qs
            ]
            return JsonResponse({"content": payload, "source": "local"}, status=200)

        # Nothing available
        print("❌ No MCQs found in Mistral or local DB")
        return JsonResponse({"error": "No MCQs available for the requested topic."}, status=404)

    except Exception:
        traceback.print_exc()
        print("🚨 Server error in generate_mcqs")
        return JsonResponse({"error": "Server error while generating MCQs"}, status=502)


# ---------------- Utility Views ---------------- #

@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def get_topics(request):
    return Response(TopicSerializer(Topic.objects.all(), many=True).data)


@api_view(['GET'])
@permission_classes([AllowAny])
def topics_with_subtopics(request):
    print("Authorization header:", request.headers.get('Authorization'))
    print("🔍 Request user:", request.user)
    print("🔐 Is authenticated:", request.user.is_authenticated)
    topics = Topic.objects.prefetch_related('subtopics').all()
    data = {
        topic.name: [{"name": sub.name, "description": sub.description} for sub in topic.subtopics.all()]
        for topic in topics
    }
    return Response(data)


@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def subtopic_details(request):
    name = request.GET.get("name", "").strip()
    if not name:
        return Response({"error": "Subtopic name is required"}, status=400)
    sub = get_object_or_404(Subtopic, name=name)
    data = SubtopicSerializer(sub).data
    data["description"] = data.get("description", "").strip('"')
    return Response(data)


@api_view(['POST'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def save_quiz_result(request):
    serializer = QuizResultSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save(user=request.user)
        return Response({'message': 'Quiz result saved successfully'}, status=status.HTTP_201_CREATED)
    else:
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def quiz_results(request):
    try:
        user = request.user
        results = QuizResult.objects.filter(user=user).order_by('-date_taken')

        data = [
            {
                'topic': result.topic.name if result.topic else "N/A",
                'subtopic': result.subtopic.name if result.subtopic else "N/A",
                'score': result.score,
                'total': result.total,
                'date_taken': result.date_taken,
            }
            for result in results
        ]
        return Response(data)

    except Exception:
        traceback.print_exc()
        print("🔥 Error in quiz_results view")
        return Response({"error": "Internal server error"}, status=500)
