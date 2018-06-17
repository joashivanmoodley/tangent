from django.conf.urls import url

from employee.views import summary, details, birthday
from employee.views import review, employee_dashboard, employee_stats

urlpatterns = [
    url(r'^summary/$', summary, name='employee_summary'),
    url(r'^details/(?P<id>(\d|-)+)/$', details, name='details'),
    url(r'^details/$', details, name='details'),
    url(r'^dashboard/$', employee_dashboard, name='employee_dashboard'),
    url(r'^birthday/$', birthday, name='birthday'),
    url(r'^review/$', review, name='review'),
    url(r'^stats/$', employee_stats, name='employee_stats'),
]
