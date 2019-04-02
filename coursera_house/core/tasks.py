from __future__ import absolute_import, unicode_literals
from celery import task

from coursera_house.core.smarthome import SmartHome


@task()
def smart_home_manager():
    # Здесь ваш код для проверки условий
    SmartHome.get_controllers()
    SmartHome.get_values()
    SmartHome.is_leak()
    SmartHome.is_cold_water_close()
    SmartHome.boiler_handler()
    SmartHome.curtains_handler()
    SmartHome.is_smoke()
    SmartHome.conditioner_handler()
    SmartHome.post_controllers(SmartHome.change_controllers)

