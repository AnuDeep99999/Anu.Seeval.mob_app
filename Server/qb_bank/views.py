from django.shortcuts import render, redirect
from django.http import HttpResponse
from .forms import MCQUploadForm
from .models import QuestionBank
import pandas as pd

def upload_mcq_excel(request):
    if request.method == 'POST':
        form = MCQUploadForm(request.POST, request.FILES)
        if form.is_valid():
            excel_file = request.FILES['file']
            df = pd.read_excel(excel_file)
            for _, row in df.iterrows():
                QuestionBank.objects.create(
                    Course=row.get('Course', 'Python'),
                    Course_Level=row.get('Course_Level', 'Basic'),
                    Level=row.get('Level', ''),
                    Topic=row.get('Topic', ''),
                    Sub_Topic=row.get('Sub_Topic', ''),
                    Question=row.get('Question', ''),
                    Options=row.get('Options', ''),
                    OptionA=row.get('OptionA', ''),
                    OptionB=row.get('OptionB', ''),
                    OptionC=row.get('OptionC', ''),
                    OptionD=row.get('OptionD', ''),
                    Answer_option=row.get('Answer_option', ''),
                    Correct_answer=row.get('Correct_answer', '')
                )
            return redirect('upload-success')
    else:
        form = MCQUploadForm()
    return render(request, 'upload_mcq.html', {'form': form})


def upload_success(request):
    return HttpResponse("<h2>Upload Successful!</h2><p>Your MCQs were saved in the database.</p>")



