from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse
from django.urls import reverse_lazy
from django.views.generic import FormView
from requests import RequestException

from coursera_house.core.tasks import SmartHome
from .models import Setting
from .form import ControllerForm


class ControllerView(FormView):
    form_class = ControllerForm
    template_name = 'core/control.html'
    success_url = reverse_lazy('form')

    def get_context_data(self, **kwargs):
        context = super(ControllerView, self).get_context_data()
        context['data'] = SmartHome.data

        return context

    def get_initial(self):

        SmartHome.get_controllers()
        SmartHome.get_values()
        values = SmartHome.current
        return {'bedroom_light': values['bedroom_light'], 'bathroom_light': values['bathroom_light']}

    def form_valid(self, form):

        change_controllers = {}
        hot_water_target = form.cleaned_data['hot_water_target_temperature']
        bedroom_target = form.cleaned_data['bedroom_target_temperature']
        hot_water_db = Setting.objects.get(controller_name='hot_water_target_temperature')
        bedroom_db = Setting.objects.get(controller_name='bedroom_target_temperature')
        if hot_water_target != hot_water_db.value:
            hot_water_db.value = hot_water_target
            hot_water_db.save()
        if bedroom_target != bedroom_db.value:
            bedroom_db.value = bedroom_target
            bedroom_db.save()
        if not SmartHome.current['smoke_detector']:
            change_controllers['bedroom_light'] = form.cleaned_data['bedroom_light']
            change_controllers['bathroom_light'] = form.cleaned_data['bathroom_light']
        else:
            change_controllers['bedroom_light'] = False
            change_controllers['bathroom_light'] = False
        SmartHome.post_controllers(change_controllers)
        return super(ControllerView, self).form_valid(form)

    def get(self, request, *args, **kwargs):
        if SmartHome.response_status != 200:
            return HttpResponse(status=502)
        return super(ControllerView, self).get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        if SmartHome.response_status != 200:
            return HttpResponse('error', status=502)
        return super(ControllerView, self).post(request, *args, **kwargs)



    
            
            