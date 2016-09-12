# -*- coding: utf-8 -*-
from django.conf.urls import url

from . import views
from . import events

urlpatterns = [
    # url(r'^$', views.index, name='index'),
    url(r'^dashboard/$', views.dashboard, name='dashboard'),
    url(r'^estudiante/(?P<pk>(\d)+)$', views.get_student, name='get_student'),
    url(r'^estudiante/crear/$', views.create_student, name='create_student'),
    url(r'^estudiante/buscar/$', views.search_student, name='search_student'),
    url(r'^estudiante/eliminar/$', views.delete_student, name='delete_student'),
    url(r'^estudiante/editar/(?P<pk>(\d)+)$', views.edit_student, name='edit_student'),
    url(r'^profesor/(?P<pk>(\d)+)$', views.get_professor, name='get_professor'),
    url(r'^profesor/crear/$', views.create_professor, name='create_professor'),
    url(r'^profesor/buscar/$', views.search_professor, name='search_professor'),
    url(r'^profesor/eliminar/$', views.delete_professor, name='delete_professor'),
    url(r'^profesor/editar/(?P<pk>(\d)+)$', views.edit_professor, name='edit_professor'),

    # TODO change views
    url(r'^via/(?P<pk>(\d)+)$', views.get_way, name='get_way'),
    url(r'^via/crear/$', views.create_way, name='create_way'),
    url(r'^via/listar/$', views.list_ways, name='list_ways'),
    url(r'^via/buscar/$', views.search_way, name='search_way'),
    url(r'^via/eliminar/$', views.delete_way, name='delete_way'),
    url(r'^via/editar/(?P<pk>(\d)+)$', views.edit_way, name='edit_way'),

    url(r'^evento/crear/$', events.create_event, name='create_event'),
    url(r'^evento/buscar/$', views.search_professor, name='search_event'),  # TODO
    url(r'^evento/listar/$', events.list_events, name='list_events'),
    url(r'^evento/eliminar/$', views.delete_professor, name='delete_event'),  # TODO
    url(r'^evento/editar/(?P<pk>(\d)+)$', views.edit_professor, name='edit_event'),  # TODO
    url(r'^evento/(?P<pk>(\d)+)$', events.get_event, name='get_event'),

    url(r'^graduation/start_process/$', views.start_graduation_process, name='start_graduation_process'),
    url(r'^graduation/list_process/$', views.list_graduation_process, name='list_graduation_process'),
    url(r'^graduation/search_process/$', views.search_graduation_process, name='search_graduation_process'),
    url(r'^graduation/(?P<pk>(\d)+)$', views.get_graduation_process, name='get_graduation_process'),

    url(r'^calendario/eventos/$', events.list_waycalendar, name='list_waycalendar'),
    url(r'^calendario/eventos/(?P<pk>(\d)+)$', events.get_waycalendar, name='get_waycalendar'),
    url(r'^calendario/eventos/crear/(?P<pk>(\d)+)$', events.create_waycalendar, name='create_waycalendar'),
    url(r'^calendario/eventos/editar/(?P<pk>(\d)+)$', events.edit_waycalendar, name='edit_waycalendar'),

    url(r'^reporte/crear/$', events.create_report, name='create_report'),
]
