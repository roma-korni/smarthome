import json

import requests
from django.core.mail import send_mail
from .models import Setting
from coursera_house import settings


class SmartHome:
    data = []
    current = {}
    url = settings.SMART_HOME_API_URL
    auth = {'Authorization': f'Bearer {settings.SMART_HOME_ACCESS_TOKEN}'}
    change_controllers = {}
    response_status = 200

    @classmethod
    def get_controllers(cls):
        response = requests.get(cls.url, headers=cls.auth)
        cls.response_status = response.status_code
        cls.data = json.loads(response.content)['data']

    @classmethod
    def get_values(cls):
        cls.current = {item['name']: item['value'] for item in cls.data}
        cls.change_controllers = {}

    @classmethod
    def is_leak(cls):
        if cls.current['leak_detector']:
            cls.change_controllers['cold_water'] = False
            cls.change_controllers['hot_water'] = False
            cls.change_controllers['boiler'] = False
            send_mail(
                'Leak is detected',
                'Leak is detected. Cold and hot water are closed.',
                settings.EMAIL_HOST_USER,
                settings.EMAIL_RECEPIENT
            )

    @classmethod
    def is_cold_water_close(cls):
        if not cls.current['cold_water']:
            cls.change_controllers['boiler'] = False
            cls.change_controllers['washing_machine'] = 'off'
            cls.change_controllers['washing_machine'] = 'off'

    @classmethod
    def boiler_handler(cls):
        boiler_handler = {}
        if not cls.current['smoke_detector'] and cls.current['cold_water']:
            hot_water_target = Setting.objects.get(controller_name='hot_water_target_temperature').value
            if int(cls.current['boiler_temperature']) < int(hot_water_target) * 0.9:
                cls.change_controllers['boiler'] = True
                boiler_handler['boiler'] = True
            if int(cls.current['boiler_temperature']) > int(hot_water_target) * 1.1:
                cls.change_controllers['boiler'] = False
                boiler_handler['boiler'] = False
        return boiler_handler

    @classmethod
    def is_curtain_slightly(cls):
        if cls.current['curtains'] == 'slightly_open':
            return True
        return False

    @classmethod
    def curtains_handler(cls):
        if not cls.is_curtain_slightly():
            if cls.current['outdoor_light'] < 50 and not cls.current['bedroom_light']:
                cls.change_controllers['curtains'] = 'open'
            if cls.current['outdoor_light'] > 50 or cls.current['bedroom_light']:
                cls.change_controllers['curtains'] = 'close'

    @classmethod
    def is_smoke(cls):
        if cls.current['smoke_detector']:
            cls.change_controllers['boiler'] = False
            cls.change_controllers['air_conditioner'] = False
            cls.change_controllers['bedroom_light'] = False
            cls.change_controllers['bathroom_light'] = False
            cls.change_controllers['washing_machine'] = 'off'

    @classmethod
    def conditioner_handler(cls):
        conditioner_handler = {}
        if not cls.current['smoke_detector']:
            bedroom_target = Setting.objects.get(controller_name='bedroom_target_temperature').value
            if int(cls.current['bedroom_temperature']) > int(bedroom_target) * 1.1:
                cls.change_controllers['air_conditioner'] = True
                conditioner_handler['air_conditioner'] = True
            if int(cls.current['bedroom_temperature']) < int(bedroom_target) * 0.9:
                cls.change_controllers['air_conditioner'] = False
                conditioner_handler['air_conditioner'] = False
        return conditioner_handler   

    @classmethod
    def post_controllers(cls, change_data):
        data_send = []
        change_data_copy = change_data.copy()
        for key in change_data:
            if change_data[key] == cls.current[key]:
                change_data_copy.pop(key)
        for key, value in change_data_copy.items():
            data_send.append({'name': key, 'value': value})
        if data_send:
            post = requests.post(cls.url, headers=cls.auth, data=json.dumps({"controllers": data_send}))
            cls.response_status = post.status_code


