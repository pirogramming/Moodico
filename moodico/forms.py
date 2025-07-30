from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import *

class CustomSignupForm(UserCreationForm):
    username = forms.CharField(
        label='',
        help_text='',
        widget=forms.TextInput(attrs={
            'placeholder': '사용자 이름',
            'class': 'form-input'
        })
    )
    password1 = forms.CharField(
        label='',
        help_text='',
        widget=forms.PasswordInput(attrs={
            'placeholder': '비밀번호',
            'class': 'form-input'
        })
    )
    password2 = forms.CharField(
        label='',
        help_text='',
        widget=forms.PasswordInput(attrs={
            'placeholder': '비밀번호 확인',
            'class': 'form-input'
        })
    )

    class Meta:
        model = User
        fields = ('username',)
        help_texts = {
            'username': '',
        }