# -*- coding: utf-8 -*-
from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^usuario/(?P<pk>(\d)+)$', views.get_user, name='get_user'),
    url(r'^usuario/crear$', views.create_user, name='create_user'),
    url(r'^usuario/editar$', views.search_user),
    url(r'^usuario/buscar$', views.search_user, name='search_user'),
    url(r'^usuario/editar/(?P<pk>(\d)+)$', views.edit_user, name='edit_user'),
    url(r'^usuario/eliminar/$', views.delete_user, name='delete_user'),
    url(r'^roles/$', views.list_groups, name='list_groups'),
    url(r'^roles/(?P<pk>(\d)+)$', views.get_group, name='get_group'),
    url(r'^roles/editar$', views.search_group),
    url(r'^roles/editar/(?P<pk>(\d)+)$', views.edit_group, name='edit_group'),
    url(r'^roles/crear$', views.create_group, name='create_group'),
    url(r'^roles/buscar$', views.search_group, name='search_group'),
    url(r'^roles/eliminar$', views.delete_group, name='delete_group'),
    url(r'^login/$', views.login, name='login'),
    url(r'^logout/$', views.logout, name='logout'),
]
