from django import forms
from moodico.upload.models import Upload

class UploadForm(forms.ModelForm):
    class Meta:
        model = Upload
        fields = ['image_path']