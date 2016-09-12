# -*- coding: utf-8 -*-
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User, Group
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from users.forms import EditUserForm, UserForm
from core.forms import WayForm, GraduationProcessForm
from pteitudp.settings import STUDENTS, PROFESSORS
from core.models import Way, GraduationProcess
from django.http import Http404
from datetime import datetime
from django.db.models import Q, Count


@login_required
def dashboard(request):
    if datetime.today().month < 8:
        semester = 1
    else:
        semester = 2
    ways = Way.objects\
        .filter(graduationprocess__semester=semester, graduationprocess__created_at__year=datetime.today().year)\
        .annotate(actual_quantity=Count('graduationprocess'))
    return render(request, 'dashboard.html', {'ways': ways})


@login_required
def start_graduation_process(request):
    if request.method == 'POST':
        form = GraduationProcessForm(request.POST)
        if form.is_valid():
            gp = form.save(commit=False)
            gp.student = User.objects.get(username=form.cleaned_data['student'])
            if request.POST.get('professor', '') != '':
                gp.professor = User.objects.get(username=form.cleaned_data['professor'])
            if request.POST.get('c_professor', '') != '':
                gp.c_professor = User.objects.get(username=form.cleaned_data['c_professor'])
            gp.way = Way.objects.get(pk=form.cleaned_data['way'])
            gp.set_semester()
            gp.save()
            if GraduationProcess.objects.filter(student=gp.student).count() > 1:
                messages.add_message(request, messages.WARNING,
                                     "El estudiante ya posee un proceso de titulación iniciado,"
                                     " un nuevo proceso de titulación para {student} se ha iniciado correctamente"
                                     .format(student=gp.student.first_name + " " + gp.student.last_name))
            else:
                messages.add_message(request, messages.SUCCESS,
                                     "Proceso de titulación para {student} iniciado correctamente"
                                     .format(student=gp.student.first_name + " " + gp.student.last_name))
        else:
            return render(request, 'graduation_process_start.html', {'form': form})
    form = GraduationProcessForm()
    return render(request, 'graduation_process_start.html', {'form': form})


@login_required
def list_graduation_process(request):
    gps = GraduationProcess.objects.filter(created_at__year=datetime.today().year)
    return render(request, 'graduation_process_list.html', {'gps': gps})


@login_required
def search_graduation_process(request):
    if request.method == 'POST':
        semester = request.POST.get('semester', '')
        username = request.POST['rut']
        first_name = request.POST['first_name']
        last_name = request.POST['last_name']
        year = request.POST['year']
        if semester != '':
            gps_filtered = GraduationProcess.objects.filter((Q(student__username__icontains=username,
                                                            student__first_name__icontains=first_name,
                                                            student__last_name__icontains=last_name,) |
                                                            Q(professor__username__icontains=username,
                                                            professor__first_name__icontains=first_name,
                                                            professor__last_name__icontains=last_name) |
                                                            Q(c_professor__username__icontains=username,
                                                            c_professor__first_name__icontains=first_name,
                                                            c_professor__last_name__icontains=last_name)) &
                                                            Q(created_at__year__icontains=year) &
                                                            Q(semester=int(semester))
                                                            )
        else:
            gps_filtered = GraduationProcess.objects.filter((Q(student__username__icontains=username,
                                                            student__first_name__icontains=first_name,
                                                            student__last_name__icontains=last_name,) |
                                                            Q(professor__username__icontains=username,
                                                            professor__first_name__icontains=first_name,
                                                            professor__last_name__icontains=last_name) |
                                                            Q(c_professor__username__icontains=username,
                                                            c_professor__first_name__icontains=first_name,
                                                            c_professor__last_name__icontains=last_name)) &
                                                            Q(created_at__year__icontains=year)
                                                            )
        return render(request, 'graduation_process_list.html', {'gps': gps_filtered})
    else:
        return render(request, 'graduation_process_search.html')


@login_required
def get_graduation_process(request, pk):
    gp = get_object_or_404(GraduationProcess, pk=pk)
    return render(request, 'graduation_process_get.html', {'gp': gp})


@login_required
def create_student(request):
    if request.method == 'POST':
        data = request.POST.copy()
        form = UserForm(data)
        context = {'user_form': form}
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.username = form.cleaned_data['rut']
            user.save()
            # Si el grupo no existe, lo crea con el nombre designado en settings.py
            try:
                group = Group.objects.get(name=STUDENTS)
            except Group.DoesNotExist:
                Group.objects.create(name=STUDENTS)
                group = Group.objects.get(name=STUDENTS)
            group.user_set.add(user)
            context = {'user_form': UserForm()}
            messages.add_message(request, messages.SUCCESS,
                                 "Estudiante {first_name} {last_name} ha sido creado exitosamente"
                                 .format(first_name=form.cleaned_data['first_name'],
                                         last_name=form.cleaned_data['last_name']))
        return render(request, 'student_create.html', context)
    context = {'user_form': UserForm()}
    return render(request, 'student_create.html', context)


@login_required
def get_student(request, pk):
    user = get_object_or_404(User, pk=pk)
    if user not in User.objects.filter(groups__name=STUDENTS):
        raise Http404
    context = {'user': user}
    return render(request, 'student_get.html', context)


@login_required
def delete_student(request):
    if request.method == "POST":
        user = get_object_or_404(User, pk=request.POST['pk'])
        user_fullname = user.first_name + " " + user.last_name
        user.delete()
        messages.add_message(request,
                             messages.SUCCESS,
                             "Estudiante {fullname} ha sido eliminado exitosamente".format(fullname=user_fullname))
        return redirect('search_student')


@login_required
def edit_student(request, pk):
    requested_user = get_object_or_404(User, pk=pk)
    if requested_user not in User.objects.filter(groups__name=STUDENTS):
        raise Http404
    if request.method == 'POST':
        data = request.POST.copy()
        form = EditUserForm(data, instance=requested_user)
        if form.is_valid():
            user = form.save(commit=False)
            if form.cleaned_data['password'].strip() != "":
                user.set_password(form.cleaned_data['password'])
                user.save()
            else:
                form.save()
            messages.add_message(request, messages.SUCCESS,
                                 "Estudiante {first_name} {last_name} ha sido editado exitosamente"
                                 .format(first_name=user.first_name,
                                         last_name=user.last_name))
            return redirect('get_student', pk=pk)
        else:
            form = EditUserForm(data, initial={'rut': requested_user.username}, instance=requested_user)
            context = {'user_form': form, 'user_pk': pk}
            return render(request, 'student_edit.html', context)

    else:
        form = EditUserForm(initial={'rut': requested_user.username}, instance=requested_user)
        context = {'user_form': form, 'user_pk': pk}
    return render(request, 'student_edit.html', context)


@login_required
def search_student(request):
    if request.method == 'POST':
        # obtiene usuarios que pertenecen al grupo de estudiantes
        users_filtered = User.objects.filter(groups__name=STUDENTS,
                                             username__icontains=request.POST['rut'],
                                             first_name__icontains=request.POST['first_name'],
                                             last_name__icontains=request.POST['last_name'],)
        su_form = {'rut': request.POST['rut'], 'first_name': request.POST['first_name'],
                   'last_name': request.POST['last_name']}
        context = {'users': users_filtered, 'su_form': su_form}
        return render(request, 'students_list.html', context)
    return render(request, 'student_search.html')


@login_required
def create_professor(request):
    if request.method == 'POST':
        data = request.POST.copy()
        form = UserForm(data)
        context = {'user_form': form}
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.username = form.cleaned_data['rut']
            user.save()
            # Si el grupo no existe, lo crea con el nombre designado en settings.py
            try:
                group = Group.objects.get(name=PROFESSORS)
            except Group.DoesNotExist:
                Group.objects.create(name=PROFESSORS)
                group = Group.objects.get(name=PROFESSORS)
            group.user_set.add(user)
            context = {'user_form': UserForm()}
            messages.add_message(request, messages.SUCCESS,
                                 "Profesor {first_name} {last_name} ha sido creado exitosamente"
                                 .format(first_name=form.cleaned_data['first_name'],
                                         last_name=form.cleaned_data['last_name']))
        return render(request, 'professor_create.html', context)
    context = {'user_form': UserForm()}
    return render(request, 'professor_create.html', context)


@login_required
def get_professor(request, pk):
    user = get_object_or_404(User, pk=pk)
    if user not in User.objects.filter(groups__name=PROFESSORS):
        raise Http404
    context = {'user': user}
    return render(request, 'professor_get.html', context)


@login_required
def delete_professor(request):
    if request.method == "POST":
        user = get_object_or_404(User, pk=request.POST['pk'])
        user_fullname = user.first_name + " " + user.last_name
        user.delete()
        messages.add_message(request,
                             messages.SUCCESS,
                             "Profesor {fullname} ha sido eliminado exitosamente".format(fullname=user_fullname))
        return redirect('search_professor')


@login_required
def edit_professor(request, pk):
    requested_user = get_object_or_404(User, pk=pk)
    if requested_user not in User.objects.filter(groups__name=PROFESSORS):
        raise Http404
    if request.method == 'POST':
        data = request.POST.copy()
        form = EditUserForm(data, instance=requested_user)
        if form.is_valid():
            user = form.save(commit=False)
            if form.cleaned_data['password'].strip() != "":
                user.set_password(form.cleaned_data['password'])
                user.save()
            else:
                form.save()
            messages.add_message(request, messages.SUCCESS,
                                 "Profesor {first_name} {last_name} ha sido editado exitosamente"
                                 .format(first_name=user.first_name,
                                         last_name=user.last_name))
            return redirect('get_professor', pk=pk)
        else:
            form = EditUserForm(data, initial={'rut': requested_user.username}, instance=requested_user)
            context = {'user_form': form, 'user_pk': pk}
            return render(request, 'professor_edit.html', context)

    else:
        form = EditUserForm(initial={'rut': requested_user.username}, instance=requested_user)
        context = {'user_form': form, 'user_pk': pk}
    return render(request, 'professor_edit.html', context)


@login_required
def search_professor(request):
    if request.method == 'POST':
        # obtiene usuarios que pertenecen al grupo de profesores
        users_filtered = User.objects.filter(groups__name=PROFESSORS,
                                             username__icontains=request.POST['rut'],
                                             first_name__icontains=request.POST['first_name'],
                                             last_name__icontains=request.POST['last_name'])
        su_form = {'rut': request.POST['rut'], 'first_name': request.POST['first_name'],
                   'last_name': request.POST['last_name']}
        context = {'users': users_filtered, 'su_form': su_form}
        return render(request, 'professors_list.html', context)
    return render(request, 'professor_search.html')


@login_required()
def create_way(request):
    if request.method == 'POST':
        form = WayForm(request.POST)
        if form.is_valid():
            way = form.save(commit=False)
            way.update_date = datetime.now().date()
            way.save()
            messages.add_message(request, messages.SUCCESS,
                                 "Vía {name} ha sido creada exitosamente"
                                 .format(name=way.name))
            return redirect('list_ways')
    else:
        form = WayForm()
    return render(request, 'way_create.html', {'form': form})


@login_required()
def list_ways(request):
    ways = Way.objects.all()
    today = datetime.now().date()
    return render(request, 'ways_list.html', {'ways': ways, 'today': today})


@login_required()
def get_way(request, pk):
    way = get_object_or_404(Way, pk=pk)
    return render(request, 'way_get.html', {'way': way})


@login_required()
def search_way(request):
    if request.method == 'POST':
        query = request.POST['query']
        ways = Way.objects.filter(Q(name__icontains=query) | Q(abbr__icontains=query))
        today = datetime.now().date()
        return render(request, 'ways_list.html', {'ways': ways, 'today': today})
    else:
        return render(request, 'way_search.html')


@login_required()
def delete_way(request):
    if request.method == 'POST':
        way = get_object_or_404(Way, pk=request.POST['pk'])
        name = way.name
        way.delete()
        messages.add_message(request, messages.SUCCESS,
                             "Vía {name} ha sido eliminada exitosamente"
                             .format(name=name))
    return redirect('list_ways')


@login_required()
def edit_way(request, pk):
    requested_way = get_object_or_404(Way, pk=pk)
    if request.method == 'POST':
        form = WayForm(request.POST, instance=requested_way)
        if form.is_valid():
            form.save()
            messages.add_message(request, messages.SUCCESS,
                                 "Vía {name} ha sido editado exitosamente"
                                 .format(name=requested_way.name))
            return redirect('get_way', pk=pk)
        else:
            return render(request, 'way_edit.html', {'form': form, 'way_pk': pk})
    else:
        way = get_object_or_404(Way, pk=pk)
        form = WayForm(instance=way)
        return render(request, 'way_edit.html', {'form': form, 'way_pk': pk})
