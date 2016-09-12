# -*- coding: utf-8 -*-
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User, Group
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from users.forms import EditUserForm, UserForm
from core.forms import WayForm, EventForm, SelectWayForm, WayCalendarForm, SelectWayCalendarForm, ReportForm
from core.models import Event, WayCalendar
from pteitudp.settings import STUDENTS, PROFESSORS
from core.models import Way, GraduationProcess, StudentEvents
from django.http import Http404
from datetime import datetime, timedelta
from django.db.models import Q


@login_required
def create_event(request):
    if request.method == 'POST':
        form = EventForm(request.POST)
        if form.is_valid():
            form.save()
            # TODO agregar logica de keywords para responsable y destinatarios de eventos
            messages.add_message(request, messages.SUCCESS,
                                 "Evento {name} ha sido registrado exitosamente"
                                 .format(name=request.POST['abbr']))
            return redirect('create_event')
        return render(request, 'event_create.html', {'form': form})
    else:
        form = EventForm()
        return render(request, 'event_create.html', {'form': form})


@login_required
def edit_event(request):
    pass


@login_required
def delete_event(request):
    pass


@login_required
def get_event(request, pk):
    event = get_object_or_404(Event, pk=pk)
    return render(request, 'event_get.html', {'event': event})


@login_required
def list_events(request):
    if request.method == 'POST':
        form = SelectWayForm(request.POST)
        events = Event.objects.filter(way=request.POST['way'])
        return render(request, 'events_list.html', {'events': events, 'form': form})
    form = SelectWayForm()
    return render(request, 'events_list_select.html', {'form': form})


@login_required
def search_event(request):
    pass


# Way Calendar
@login_required
def list_waycalendar(request):
    if request.method == 'POST':
        form = SelectWayCalendarForm(request.POST)
        # TODO revisar si .exclude() funciona de forma correcta
        # TODO Solo se debe mostrar los eventos a los que se debe asignar fecha
        if request.POST['year'].strip() == "":
            year = datetime.now().year
        else:
            year = request.POST['year']
        events = Event.objects.filter(way=request.POST['way'])
        waycalendars_1 = WayCalendar.objects.filter(event__way=request.POST['way'], semester=1, year=year)
        waycalendars_2 = WayCalendar.objects.filter(event__way=request.POST['way'], semester=2, year=year)
        return render(request, 'waycalendar_list.html', {'events': events,
                                                         'waycalendars_1': waycalendars_1,
                                                         'waycalendars_2': waycalendars_2,
                                                         'form': form,
                                                         'year': year})
    form = SelectWayCalendarForm()
    return render(request, 'waycalendar_select.html', {'form': form})


@login_required
def get_waycalendar(request, pk):
    waycalendar = get_object_or_404(WayCalendar, pk=pk)
    return render(request, 'waycalendar_get.html', {'waycalendar': waycalendar})


def check_events(request, events_to_check, lala, semester, date_ini):
    for event in events_to_check:
        foo = WayCalendar.objects.create(event=event,
                                         year=lala,
                                         semester=semester,
                                         date_ini=(date_ini + timedelta(days=event.reference_days))
                                         )
        check_events(request, Event.objects.filter(involved_event=foo.event), lala, semester, date_ini)
        messages.add_message(request, messages.SUCCESS,
                             "Debido a que depende de la fecha recien asignada"
                             " se ha asignado fecha al evento \"{name}\""
                             .format(name=event))


@login_required
def create_waycalendar(request, pk):
    if request.method == 'POST':
        event = get_object_or_404(Event, pk=pk)
        form = WayCalendarForm(request.POST)
        if form.is_valid():
            year = form.cleaned_data['year']
            semester = form.cleaned_data['semester']
            date_ini = form.cleaned_data['date_ini']

            form.save()
            messages.add_message(request, messages.SUCCESS,
                                 "Se ha asignado fecha al evento \"{name}\""
                                 .format(name=event))

            events_to_check = Event.objects.filter(involved_event=event)
            check_events(request, events_to_check, year, semester, date_ini)

            return redirect('list_waycalendar')
        return render(request, 'waycalendar_create.html', {'event': event, 'form': form})
    else:
        event = get_object_or_404(Event, pk=pk)
        form = WayCalendarForm()
        return render(request, 'waycalendar_create.html', {'event': event, 'form': form})


def check_edit_events(request, events_to_check, lala, semester, date_ini):
    for event in events_to_check:
        wc = WayCalendar.objects.filter(event=event, year=lala, semester=semester, ).last()
        wc.date_ini = (date_ini + timedelta(days=event.reference_days))
        foo = wc
        wc.save()
        check_edit_events(request, Event.objects.filter(involved_event=foo.event), lala, semester, date_ini)
        messages.add_message(request, messages.SUCCESS,
                             "Debido a que depende de la fecha recien editada"
                             " se ha editado la fecha al evento \"{name}\""
                             .format(name=fooevent))

# TODO se debe crear una funcion recursiva para revisar los eventos a editar, similar a lo que se hace e create_waycalendar (verificar funcion creada)
@login_required
def edit_waycalendar(request, pk):
    requested_waycalendar = get_object_or_404(WayCalendar, pk=pk)
    if request.method == 'POST':
        form = WayCalendarForm(request.POST, instance=requested_waycalendar)
        related_event = get_object_or_404(Event, pk=requested_waycalendar.event.pk)
        if form.is_valid():
            year = form.cleaned_data['year']
            semester = form.cleaned_data['semester']
            date_ini = form.cleaned_data['date_ini']
            form.save()
            messages.add_message(request, messages.SUCCESS,
                                 "Fecha/s e información relacionada al evento {event} ha sido editada exitosamente"
                                 .format(event=related_event))

            events_to_check = Event.objects.filter(involved_event=requested_waycalendar.event)
            check_edit_events(request, events_to_check, year, semester, date_ini)
            return redirect('get_waycalendar', pk=pk)
        else:
            form = WayCalendarForm(request.POST, instance=requested_waycalendar)
            context = {'form': form, 'waycalendar': requested_waycalendar}
            return render(request, 'waycalendar_edit.html', context)
    else:
        form = WayCalendarForm(instance=requested_waycalendar)
        context = {'form': form, 'waycalendar': requested_waycalendar}
    return render(request, 'waycalendar_edit.html', context)


@login_required
def delete_waycalendar(request):
    pass


def is_student(request):
    if request.user in User.objects.filter(groups__name=STUDENTS):
        return True
    return False


def get_students_choices(request):
    gps = GraduationProcess.objects.filter(Q(student=request.user) |
                                           Q(professor=request.user) |
                                           Q(c_professor=request.user))
    choices = list()
    for gp in gps:
        # TODO should get the relvants gp, maybe this year gps? or this semester gp?
        choices.append(
            (gp.student.pk, (gp.student.first_name + " " + gp.student.last_name + " " + gp.student.username))
        )
    return choices

@login_required
def create_report(request):
    # TODO crear 2 versiones. crear form diferentes si es estudiante o profesor (form.student)
    # TODO detect way (ultimo proceso iniciado para ese estudiante?)
    # TODO detect semester from date
    # TODO select event type from menu (differents forms)
    # TODO documents?
    # TODO Owner user => user logged in
    # graduation process related to user
    gp = GraduationProcess.objects.filter(Q(student=request.user) |
                                          Q(professor=request.user) |
                                          Q(c_professor=request.user))

    if is_student(request):
        if request.method == 'POST':
            form = ReportForm(request.POST)
            if gp.count() < 1:
                messages.add_message(request, messages.ERROR, "El estudiante no tiene un proceso de titulación activo")
                return render(request, 'report_create.html', {'form': form, 'is_student': is_student(request)})

            # TODO check whats the next step to the student
            # semester
            if datetime.now().month < 8:
                semester = 1
            else:
                semester = 2
            student = User.objects.get(pk=request.user.pk)
            way = GraduationProcess.objects.filter(student=student).last().way
            print("way")
            print(way)
            waycalendars = WayCalendar.objects.filter(event__way=way,
                                                      semester=semester,
                                                      year=datetime.now().year, )
            student_record = StudentEvents.objects.filter(student=student)
            next_task = ""
            for index, waycalendar in enumerate(waycalendars):
                if waycalendar.date_ini < datetime.today().date():
                    if student_record.count() > 0:
                        if student_record[index].type == waycalendar.event.type:
                            print("task done")
                        else:
                            print("task NOT done")
                    else:
                        print("0 task done")
                        next_task = waycalendar
                        break
                else:
                    next_task = waycalendar
                    break
            # student
            student = request.user.pk
            # owner_user
            owner_user = request.user.pk
            # way
            way = gp.last().way.pk
            # event_type
            ftype = next_task.event.type

            data = {'semester': semester,
                    'type': ftype,
                    'way': way,
                    'owner_user': owner_user,
                    'student': student,
                    'description': request.POST['description'],
                    'involved_document': request.POST['involved_document']
                    }
            final_form = ReportForm(data=data)
            print(final_form.errors)
            print("HHHHHHHHHHHHHHHHH")
            if final_form.is_valid():
                print("*************************")
                final_form.save()
                messages.add_message(request, messages.SUCCESS,
                                     "Reporte del tipo {event_type} ha sido registrado exitosamente"
                                     .format(event_type=ftype))
                print("ZZZZZZZZZZZZZZZZZZZZZZZZZZ")
                return redirect('create_report')
            print("OOOOOOOOOOOOOOOOOOOOOOOOOOOOO")
            #return render(request, 'report_create.html', {'form': form, 'is_student': is_student(request)})
            return redirect('create_report')
        else:
            if gp.count() < 1:
                messages.add_message(request, messages.ERROR, "El estudiante no tiene un proceso de titulación activo")
                return render(request, 'report_create.html', {'form': form, 'is_student': is_student(request)})

            #TODO check whats the next step to the student
            if datetime.now().month < 8:
                semester = 1
            else:
                semester = 2
            student = User.objects.get(pk=request.user.pk)
            way = GraduationProcess.objects.filter(student=student).last().way
            waycalendars = WayCalendar.objects.filter(event__way=way,
                                                      semester=semester,
                                                      year=datetime.now().year,)
            student_record = StudentEvents.objects.filter(student=student)
            next_task = "No existen tareas por realizar"
            print("******")
            print(next_task)
            print(":D:D:D:D:D:D:D:D:")
            print(str(len(waycalendars)))
            for index, waycalendar in enumerate(waycalendars):
                if waycalendar.date_ini < datetime.today().date():
                    if student_record.count() > 0:
                        if len(student_record) > index:
                            if student_record[index].type == waycalendar.event.type:
                                print("task done")
                            else:
                                print("task NOT done")
                                next_task = waycalendar
                                break
                        else:
                            print("task not done")
                    else:
                        print("0 task done")
                        next_task = waycalendar
                        break
                else:
                    print("antes de la fecha del primer")
                    next_task = waycalendar
                    break
            print("******")
            print(next_task)
            print("siguiente tarea a realizar es " + next_task)
            #TODO hardcoded estudiantes NEED TEST
            show_form = True
            if next_task.event.to_users == "estudiantes":
                messages.add_message(request, messages.SUCCESS, "El siguiente reporte debe realizarlo otro usuario")
                show_form = False
            form = ReportForm()
            return render(request, 'report_create.html',
                          {'form': form,
                           'is_student': is_student(request),
                           'next_task': next_task,
                           'show_form': show_form
                           })
    else:
        if request.method == 'POST':
            form = ReportForm(request.POST)
            if gp.count() < 1:
                messages.add_message(request, messages.ERROR,
                                     "El usuario no esta involucrado en un proceso de titulación activo")
                return render(request, 'report_create.html',
                              {'form': form,
                               'is_student': is_student(request),
                               'choices': get_students_choices(request)
                               })

            # student
            if request.POST['student'].strip() == "":
                messages.add_message(request, messages.ERROR, "Debe seleccionar un estudiante")
                return render(request, 'report_create.html',
                              {'form': form,
                               'is_student': is_student(request),
                               'choices': get_students_choices(request)
                               })
            # way
            way = gp.last().way.pk
            # semester
            if datetime.now().month < 8:
                semester = 1
            else:
                semester = 2
            # event_type
            if event_type == '1':
                type = 'recepcion'
            if event_type == '2':
                type = 'entrega'
            if event_type == '3':
                type = 'aprobacion'
            if event_type == '4':
                type = 'presentacion'
            # owner
            owner_user = User.objects.get(pk=request.user.pk)
            data = {'semester': semester,
                    'type': type,
                    'way': way,
                    'owner_user': owner_user.pk,
                    'student': request.POST['student'],
                    'description': request.POST['description'],
                    'involved_document': request.POST['involved_document']
                    }
            final_form = ReportForm(data=data)
            if final_form.is_valid():
                messages.add_message(request, messages.SUCCESS,
                                     "Reporte del tipo {event_type} ha sido registrado exitosamente"
                                     .format(event_type=type))
                final_form.save()
                return redirect('create_report', event_type=event_type)
            return render(request, 'report_create.html',
                          {'form': form,
                           'is_student': is_student(request),
                           'choices': get_students_choices(request)
                           })
        else:
            form = ReportForm()
            return render(request, 'report_create.html',
                          {'form': form,
                           'is_student': is_student(request),
                           'choices': get_students_choices(request)
                           })


@login_required
def edit_report(request):
    pass


@login_required
def delete_report(request):
    pass


@login_required
def get_report(request, pk):
    event = get_object_or_404(Event, pk=pk)
    return render(request, 'event_get.html', {'event': event})


@login_required
def list_reports(request):
    if request.method == 'POST':
        form = SelectWayForm(request.POST)
        events = Event.objects.filter(way=request.POST['way'])
        return render(request, 'events_list.html', {'events': events, 'form': form})
    form = SelectWayForm()
    return render(request, 'events_list_select.html', {'form': form})
