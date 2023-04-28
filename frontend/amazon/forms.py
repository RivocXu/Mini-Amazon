# from django import forms
# from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
# from .models import Users

# class RegisterForm(UserCreationForm):
#     email = forms.EmailField(required=True)

#     class Meta:
#         model = Users
#         fields = ('username', 'email', 'password1', 'password2')

# class LoginForm(AuthenticationForm):
#     class Meta:
#         model = Users
#         fields = ('username', 'password')

# from django import forms
# from django.contrib.auth import get_user_model

# User = get_user_model()

# class UserRegistrationForm(forms.ModelForm):
#     password = forms.CharField(label='Password', widget=forms.PasswordInput)
#     password_confirm = forms.CharField(label='Password confirm', widget=forms.PasswordInput)

#     class Meta:
#         model = User
#         fields = ('name', 'email', 'location_x', 'location_y', 'ups_name')

#     def clean_password_confirm(self):
#         password = self.cleaned_data.get('password')
#         password_confirm = self.cleaned_data.get('password_confirm')
#         if password and password_confirm and password != password_confirm:
#             raise forms.ValidationError('Passwords do not match')
#         return password_confirm

#     def save(self, commit=True):
#         user = super().save(commit=False)
#         user.set_password(self.cleaned_data['password'])
#         if commit:
#             user.save()
#         return user

# class UserLoginForm(forms.Form):
#     name = forms.CharField(max_length=64)
#     password = forms.CharField(widget=forms.PasswordInput)

from django import forms
from .models import placeOrder
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm

# class RegistrationForm(forms.ModelForm):
#     password = forms.CharField(widget=forms.PasswordInput)

#     class Meta:
#         model = Users
#         fields = ['name', 'email', 'password', 'location_x', 'location_y', 'ups_name']

class RegistrationForm(UserCreationForm):
    email = forms.EmailField()
    # password = forms.CharField(widget=forms.PasswordInput)
    location_x = forms.IntegerField()
    location_y = forms.IntegerField()

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2', 'location_x', 'location_y']

        
class placeOrderForm(forms.ModelForm):
    class Meta:
        model = placeOrder
        fields = ['user_name', 'location_x', 'location_y']

class LoginForm(forms.ModelForm):
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)