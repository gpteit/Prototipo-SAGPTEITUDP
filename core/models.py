# -*- coding: utf-8 -*-
from django.db import models
from users.models import User
import time
from datetime import datetime


class BaseModel(models.Model):
    created_at = models.DateTimeField("registrado el", auto_now_add=True)
    updated_at = models.DateTimeField("actualizado el", auto_now=True)

    class Meta:
        abstract = True


class Way(BaseModel):
    name = models.CharField("nombre", max_length=200)
    abbr = models.CharField("abreviatura", max_length=15)
    ini_date = models.DateField("fecha de inicio de vigencia", null=True, blank=True)
    end_date = models.DateField("fecha de término de vigencia", null=True, blank=True)
    update_date = models.DateField("fecha de la última actualización", null=True, blank=True)

    def __unicode__(self):
        return u"%s" % self.name


class Event(BaseModel):
    event_types = (
        ('recepcion', 'Recepción por parte del actor'),
        ('entrega', 'Entrega por parte del actor'),
        ('aprobacion', 'Aprobación por parte del actor'),
        ('presentacion', 'Presentación por parte del actor'),
        ('com_recepcion', 'Generación de comunicación de confirmación de recepción'),
        ('com_proximidad', 'Generación de comunicación por proximidad'),
        ('com_retraso', 'Generación de comunicación de retraso'),
        ('com_escalamiento', 'Generación de comunicación escalamiento'),
        ('com_evaluacion', 'Generación de comunicación de evaluación'),
        ('com_via', 'Generación de comunicación cancelación de vía'),
        ('com_termino', 'Generación de comunicación por término de proceso'),
    )
    triggers = (
        ('fecha_fija', 'Por fecha fija de calendario del semestre'),
        ('cantidad_dias', 'Por cantidad de días antes o después (signo) de un evento de referencia')
    )
    way = models.ForeignKey(Way,
                            on_delete=models.CASCADE,
                            verbose_name="vía")
    correlative = models.IntegerField("correlativo", help_text="Número de secuencia en que deben ocurrir los eventos")
    type = models.CharField("tipo de evento", max_length=30, choices=event_types)
    abbr = models.CharField("abreviatura", max_length=50)
    description = models.TextField("descripción")
    trigger_type = models.CharField("trigger", max_length=30, choices=triggers)
    involved_event = models.ForeignKey('self', null=True, blank=True,
                                       on_delete=models.CASCADE,
                                       verbose_name="evento relacionado")
    reference_days = models.IntegerField("días de referencia",
                                         blank=True,
                                         null=True,
                                         help_text="Días antes o despues (signo) de un evento de referencia")
    involved_document = models.CharField("tipo de documento involucrado",
                                          max_length=255,
                                          blank=True,
                                          null=True,)
    to_users = models.TextField(blank=True, help_text="puede utilizar nombres 							claves como profesor o alumno")
    owner_user = models.ForeignKey(User, null=True, blank=True, related_name='owner_user')

    def __unicode__(self):
        return u"%s" % self.abbr


class GraduationProcess(BaseModel):
    student = models.ForeignKey(User,
                                verbose_name="estudiante",
                                related_name="students"
                                )
    professor = models.ForeignKey(User,
                                  verbose_name="profesor",
                                  related_name="professors",
                                  null=True,
                                  blank=True
                                  )
    c_professor = models.ForeignKey(User,
                                    verbose_name="profesor de comisión",
                                    related_name="c_professors",
                                    null=True,
                                    blank=True)
    description = models.TextField("descripción", null=True, blank=True)
    semester = models.CharField("semestre", max_length=1)
    status = models.CharField("estado", max_length=255, default="Inscrito")
    way = models.ForeignKey(Way, verbose_name="vía")

    def set_semester(self):
        if datetime.today().month < 8:
            self.semester = 1
        else:
            self.semester = 2


class WayCalendar(BaseModel):
    event = models.ForeignKey(Event)
    year = models.IntegerField("año")
    semester = models.CharField("semestre", max_length=1)
    description = models.TextField("descripción", null=True, blank=True)
    date_ini = models.DateField("fecha de inicio", null=True, blank=True)
    time_ini = models.TimeField("hora de inicio", null=True, blank=True)
    date_end = models.DateField("fecha de término", null=True, blank=True,
                                help_text="Fecha de termino si es que corresponde")
    place = models.CharField("lugar", max_length=255, null=True, blank=True)


##########################################################################################
def path_to_documents(instance, filename_user):
    if int(time.strftime('%m')) > 6:
        semester = "2"
    else:
        semester = "1"
    filename = str(instance.user.pk) + " " + instance.user.username + filename_user
    return '{year}/{sem}/{filename}'.format(
        year=time.strftime("%Y"),
        sem=semester,
        filename=filename,
    )


class Document(BaseModel):
    student = models.ForeignKey(User)
    description = models.TextField("Descripción")
    file = models.FileField("Documento", upload_to=path_to_documents)
##########################################################################################


class StudentEvents(BaseModel):
    event_types = (
        ('recepcion', 'Recepción por parte del actor'),
        ('entrega', 'Entrega por parte del actor'),
        ('aprobacion', 'Aprobación por parte del actor'),
        ('presentacion', 'Presentación por parte del actor'),
        ('com_recepcion', 'Generación de comunicación de confirmación de recepción'),
        ('com_proximidad', 'Generación de comunicación por proximidad'),
        ('com_retraso', 'Generación de comunicación de retraso'),
        ('com_escalamiento', 'Generación de comunicación escalamiento'),
        ('com_evaluacion', 'Generación de comunicación de evaluación'),
        ('com_via', 'Generación de comunicación cancelación de vía'),
        ('com_termino', 'Generación de comunicación por término de proceso'),
    )
    student = models.ForeignKey(User, related_name="student", verbose_name="Estudiante")
    way = models.ForeignKey(Way)
    semester = models.CharField("semestre", max_length=1)
    type = models.CharField("tipo de evento", max_length=30, choices=event_types)
    description = models.TextField("descripción", blank=True, null=True)
    involved_document = models.CharField("tipo de documento involucrado",
                                         max_length=255,
                                         blank=True,
                                         null=True, )
    to_users = models.ManyToManyField(User,
                                      blank=True,
                                      related_name='tousers',
                                      help_text="puede utilizar nombres claves como profesor o alumno")
    owner_user = models.ForeignKey(User, null=True, blank=True, related_name='owneruser')
