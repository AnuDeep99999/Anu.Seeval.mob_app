from django import forms

class MCQUploadForm(forms.Form):
    file = forms.FileField(label="Upload Excel File")

