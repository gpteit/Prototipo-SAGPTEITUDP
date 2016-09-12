# -*- coding: utf-8 -*-
from django import forms
from django.forms import ModelForm
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.models import User, Group


class LoginForm(forms.Form):
    rut = forms.CharField(label="RUT", max_length=13)
    password = forms.CharField(label="Contraseña", widget=forms.PasswordInput)


class UserForm(ModelForm):
    rut = forms.CharField(label="RUT", max_length=13)
    password = forms.CharField(label="Contraseña", widget=forms.PasswordInput())
    password2 = forms.CharField(label="Confirmar contraseña", widget=forms.PasswordInput())

    def clean(self):
        data = self.cleaned_data
        if 'password' in data and 'password2' in data and data['password'] != data['password2']:
            raise forms.ValidationError("Las contraseñas no concuerdan")

    def clean_rut(self):
        data = self.cleaned_data
        try:
            User.objects.get(username=data['rut'])
        except ObjectDoesNotExist:
            return data['rut']
        raise forms.ValidationError("Ya existe un usuario con ese Rut")

    def clean_email(self):
        if self.cleaned_data['email'].strip() == '':
            raise forms.ValidationError("Este campo es obligatorio")
        return self.cleaned_data['email']

    class Meta:
        model = User
        fields = ['rut', 'first_name', 'last_name', 'password', 'password2', 'email']


class EditUserForm(ModelForm):
    rut = forms.CharField(label="RUT", max_length=13, disabled=True, required=False)
    password = forms.CharField(label="Contraseña", widget=forms.PasswordInput(), required=False)
    password2 = forms.CharField(label="Confirmar contraseña", widget=forms.PasswordInput(), required=False)

    def clean(self):
        data = self.cleaned_data
        if 'password' in data and 'password2' in data:
            if data['password'].strip()=="" and data['password2'].strip()=="":
                return
            elif data['password'] != data['password2']:
                raise forms.ValidationError("Las contraseñas no concuerdan")


    def clean_email(self):
        if self.cleaned_data['email'].strip() == '':
            raise forms.ValidationError("Este campo es obligatorio")
        return self.cleaned_data['email']

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'password', 'password2', 'email']


class GroupForm(ModelForm):
    class Meta:
        model = Group
        fields = ['name', 'permissions']
