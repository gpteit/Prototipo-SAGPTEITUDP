# -*- coding: utf-8 -*-
from django import forms
from django.forms import ModelForm
from .models import Way, Event, GraduationProcess, WayCalendar, StudentEvents
from django.contrib.auth.models import User
from pteitudp.settings import KEYWORDS, STUDENTS, PROFESSORS
from django.db.models import Q

class DateInput(forms.DateInput):
    input_type = 'date'


class TimeInput(forms.DateInput):
    input_type = 'time'


class WayForm(ModelForm):

    class Meta:
        model = Way
        fields = ['name', 'abbr', 'ini_date', 'end_date']
        widgets = {
            'ini_date': DateInput(),
            'end_date': DateInput(),
        }


class EventForm(ModelForm):
    to_users = forms.CharField(max_length=100, required=False)
    owner_user = forms.CharField(max_length=100, required=False)

    def clean(self):
        if self.cleaned_data['involved_event'] and\
                        self.cleaned_data['involved_event'].way.pk != self.cleaned_data['way'].pk:
            raise forms.ValidationError("El evento relacionado debe pertenercer a la "
                                        "misma vía del evento que se esta creando")

    def clean_to_users(self):
        if self.cleaned_data['to_users'] == "" or self.cleaned_data['to_users'] in KEYWORDS:
            return self.cleaned_data['to_users']
        if User.objects.filter(username=self.cleaned_data['to_users'].strip()).count() > 0:
            return self.cleaned_data['to_users']
        raise forms.ValidationError("El usuario ingresado no existe")

    def clean_owner_user(self):
        if self.cleaned_data['owner_user'] in KEYWORDS:
            return self.cleaned_data['owner_user']
        if self.cleaned_data['owner_user'] == "" or User.objects.filter(username=self.cleaned_data['owner_user'].strip()).count() > 0:
            return self.cleaned_data['owner_user']
        raise forms.ValidationError("El usuario ingresado no existe")

    class Meta:
        model = Event
        exclude = ['owner_user', 'to_users']
        #fields = '__all__'


class ReportForm(ModelForm):
    class Meta:
        model = StudentEvents
        exclude = ['to_users']


class SelectWayForm(forms.Form):
    choices = list()
    for way in Way.objects.all():
        choices.append((way.pk, way.name))
    way = forms.ChoiceField(label="Seleccione una vía", choices=choices, widget=forms.Select)


class GraduationProcessForm(ModelForm):
    student = forms.CharField(max_length=100)
    professor = forms.CharField(max_length=100, required=False)
    c_professor = forms.CharField(max_length=100, required=False)
    choices = list()
    for way in Way.objects.all():
        choices.append((way.pk, way.name))
    way = forms.ChoiceField(choices=choices)

    def clean_student(self):
        student = User.objects.filter(username=self.cleaned_data['student'].strip())
        if student.count() == 1:
            if student[0] in User.objects.filter(groups__name=STUDENTS):
                return self.cleaned_data['student']
            else:
                raise forms.ValidationError("El usuario ingresado no es estudiante")
        else:
            if student.count() == 0:
                raise forms.ValidationError("No existe usuario con ese rut")
            else:
                raise forms.ValidationError("Existe más de un usuario con ese rut")

    def clean_professor(self):
        if self.cleaned_data['professor'].strip() != "":
            professor = User.objects.filter(username=self.cleaned_data['professor'].strip())
            if professor.count() == 1:
                if professor[0] in User.objects.filter(groups__name=PROFESSORS):
                    return self.cleaned_data['professor']
                else:
                    raise forms.ValidationError("El usuario ingresado no es profesor")
            else:
                raise forms.ValidationError("Existe más de un usuario con ese rut")

    def clean_c_professor(self):
        if self.cleaned_data['c_professor'].strip() != "":
            professor = User.objects.filter(username=self.cleaned_data['professor'].strip())
            if professor.count() == 1:
                if professor[0] in User.objects.filter(groups__name=PROFESSORS):
                    return self.cleaned_data['professor']
                else:
                    raise forms.ValidationError("El profesor ingresado no es profesor")
            else:
                raise forms.ValidationError("Existe más de un usuario con ese rut")

    class Meta:
        model = GraduationProcess
        exclude = ['status', 'student', 'professor', 'c_professor', 'semester', 'way']


class WayCalendarForm(ModelForm):

    class Meta:
        model = WayCalendar
        widgets = {
            'date_ini': DateInput(),
            'date_end': DateInput(),
            'time_ini': TimeInput(),
        }
        fields = '__all__'


class SelectWayCalendarForm(forms.Form):
    choices = list()
    for way in Way.objects.all():
        choices.append((way.pk, way.name))
    way = forms.ChoiceField(label="Seleccione una vía", choices=choices, widget=forms.Select)
    year = forms.IntegerField(label="Año")
