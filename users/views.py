# -*- coding: utf-8 -*-
from django.contrib import messages
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from users.forms import UserForm, LoginForm, GroupForm, EditUserForm
from django.contrib.auth.models import Group, User

#TODO add group to user in web (in create_user? or submenu with add_group)


def index(request):
    return render(request, 'index.html', {'form': LoginForm()})


@login_required
def get_group(request, pk):
    group = get_object_or_404(Group, pk=pk)
    return render(request, 'group_get.html', {'group': group})


@login_required
def search_group(request):
    if request.method == 'POST':
        groups = Group.objects.filter(name__contains=request.POST['name'])
        form = {'name': request.POST['name']}
        context = {'groups': groups, 'form': form}
        return render(request, 'groups_list.html', context)
    else:
        return render(request, 'group_search.html')


@login_required
def edit_group(request, pk):
    requested_group = get_object_or_404(Group, pk=pk)
    if request.method == 'POST':
        form = GroupForm(request.POST, instance=requested_group)
        if form.is_valid():
            form.save()
            messages.add_message(request, messages.SUCCESS,
                                 "Rol {name} ha sido editado exitosamente"
                                 .format(name=requested_group.name))
            return redirect('get_group', pk=pk)
        else:
            return render(request, 'group_edit.html', {'group_form': form, 'group_pk': pk})
    else:
        group = get_object_or_404(Group, pk=pk)
        form = GroupForm(instance=group)
        return render(request, 'group_edit.html', {'group_form': form, 'group_pk': pk})


@login_required
def list_groups(request):
    groups = Group.objects.all().order_by('-pk')
    return render(request, 'groups_list.html', {'groups': groups})


@login_required
def create_group(request):
    if request.method == 'POST':
        form = GroupForm(request.POST)
        if form.is_valid():
            form.save()
            messages.add_message(request,
                                 messages.SUCCESS,
                                 "Grupo {name} ha sido creado exitosamente".format(name=request.POST['name']))
            return redirect('list_groups')
        else:
            return render(request, 'group_create.html', {'group_form': form})
    else:
        form = GroupForm()
        return render(request, 'group_create.html', {'group_form': form})


@login_required
def delete_group(request):
    if request.method == 'POST':
        group = get_object_or_404(Group, pk=request.POST['pk'])
        group_name = group.name
        group.delete()
        messages.add_message(request,
                             messages.SUCCESS,
                             "Grupo {name} ha sido eliminado exitosamente".format(name=group_name))
    return redirect('list_groups')


@login_required
def create_user(request):
    if request.method == 'POST':
        data = request.POST.copy()
        form = UserForm(data)
        context = {'user_form': form}
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.username=form.cleaned_data['rut']
            user.save()
            context = {'user_form': UserForm()}
            messages.add_message(request, messages.SUCCESS,
                                 "Usuario {first_name} {last_name} ha sido creado exitosamente"
                                 .format(first_name=form.cleaned_data['first_name'],
                                         last_name=form.cleaned_data['last_name']))
        return render(request, 'user_create.html', context)
    context = {'user_form': UserForm()}
    return render(request, 'user_create.html', context)


@login_required
def edit_user(request, pk):
    requested_user = get_object_or_404(User, pk=pk)
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
                                 "Usuario {first_name} {last_name} ha sido editado exitosamente"
                                 .format(first_name=user.first_name,
                                         last_name=user.last_name))
            return redirect('get_user', pk=pk)
        else:
            form = EditUserForm(data, initial={'rut': requested_user.username}, instance=requested_user)
            context = {'user_form': form, 'user_pk': pk}
            return render(request, 'user_edit.html', context)

    else:
        form = EditUserForm(initial={'rut': requested_user.username}, instance=requested_user)
        context = {'user_form': form, 'user_pk': pk}
    return render(request, 'user_edit.html', context)


@login_required
def search_user(request):
    if request.method == 'POST':
        users = User.objects.filter(username__contains=request.POST['rut'],
                                    first_name__contains=request.POST['first_name'],
                                    last_name__contains=request.POST['last_name'])
        form = {'rut': request.POST['rut'], 'first_name': request.POST['first_name'],
                   'last_name': request.POST['last_name']}
        context = {'users': users, 'form': form}
        return render(request, 'users_list.html', context)
    return render(request, 'user_search.html')


@login_required
def get_user(request, pk):
    user = get_object_or_404(User, pk=pk)
    context = {'user': user}
    return render(request, 'user_get.html', context)


@login_required
def delete_user(request):
    if request.method == 'POST':
        user = get_object_or_404(User, pk=request.POST['pk'])
        messages.add_message(request, messages.SUCCESS,
                             "Usuario {first_name} {last_name} ha sido eliminado exitosamente"
                             .format(first_name=user.first_name,
                                     last_name=user.last_name))
        user.delete()
        return redirect('search_user')
    else:
        return redirect('search_user')


def login(request):
    if request.method == 'POST':
        user = authenticate(username=request.POST['rut'], password=request.POST['password'])
        if user is not None:
            if user.is_active:
                auth_login(request, user)
            else:
                messages.add_message(request, messages.ERROR, "Cuenta desactivada")
                return redirect('index')
        else:
            messages.add_message(request, messages.ERROR, "Usuario o contraseña incorrecto/s")
            return redirect('index')
    # TODO redirect to 'next' (get['next'] contain the url to redirect the user)
    return redirect('dashboard')


@login_required
def logout(request):
    auth_logout(request)
    return redirect('index')
