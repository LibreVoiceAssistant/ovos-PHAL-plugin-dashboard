import os
import secrets
import string
import subprocess
import time

from mycroft_bus_client.message import Message
from ovos_plugin_manager.phal import PHALPlugin
from ovos_utils import classproperty
from ovos_utils.log import LOG
from ovos_utils.network_utils import NetworkRequirements
from ovos_utils.network_utils import get_ip


class OVOSDashboardPlugin(PHALPlugin):
    def __init__(self, bus=None, config=None):
        super().__init__(bus=bus, name="ovos-PHAL-plugin-dashboard",
                         config=config)
        self.bus = bus
        self.bus.on("ovos.PHAL.dashboard.enable",
                    self.handle_device_developer_enable_dash)
        self.bus.on("ovos.PHAL.dashboard.disable",
                    self.handle_device_developer_disable_dash)
        self.bus.on("ovos.PHAL.dashboard.get.status",
                    self.handle_device_dashboard_status_check)

        # Dashboard Specific
        alphabet = string.ascii_letters + string.digits
        self.dash_secret = ''.join(secrets.choice(alphabet) for i in range(5))
        self.username = self.config.get('username') or "OVOS"
        LOG.info("Dashboard Plugin Initialized")

    @classproperty
    def network_requirements(self):
        """ developers should override this if they do not require connectivity
         some examples:
         IOT plugin that controls devices via LAN could return:
            scans_on_init = True
            NetworkRequirements(internet_before_load=False,
                                 network_before_load=scans_on_init,
                                 requires_internet=False,
                                 requires_network=True,
                                 no_internet_fallback=True,
                                 no_network_fallback=False)
         online search plugin with a local cache:
            has_cache = False
            NetworkRequirements(internet_before_load=not has_cache,
                                 network_before_load=not has_cache,
                                 requires_internet=True,
                                 requires_network=True,
                                 no_internet_fallback=True,
                                 no_network_fallback=True)
         a fully offline plugin:
            NetworkRequirements(internet_before_load=False,
                                 network_before_load=False,
                                 requires_internet=False,
                                 requires_network=False,
                                 no_internet_fallback=True,
                                 no_network_fallback=True)
        """
        return NetworkRequirements(internet_before_load=False,
                                   network_before_load=True,
                                   requires_internet=False,
                                   requires_network=True,
                                   no_internet_fallback=False,
                                   no_network_fallback=False)

    def handle_device_dashboard_status_check(self, _):
        if self._check_dash_running():
            self.bus.emit(Message("ovos.PHAL.dashboard.status.response",
                                  {"status": True,
                                   "url": "https://{0}:5000".format(get_ip()),
                                   "user": self.username,
                                   "password": self.dash_secret}))
        else:
            self.bus.emit(Message("ovos.PHAL.dashboard.status.response",
                                  {"status": False, "url": None,
                                   "user": None, "password": None}))

    def _check_dash_running(self) -> bool:
        build_status_check_call = "systemctl --user is-active --quiet ovos-dashboard@'{0}'.service".format(
            self.dash_secret)
        dash_status = subprocess.run(build_status_check_call, shell=True,
                                     env=dict(os.environ))
        LOG.debug(f"Dash status check got return: {dash_status.returncode}")
        return dash_status.returncode == 0

    def handle_device_developer_enable_dash(self, message):
        os.environ["SIMPLELOGIN_USERNAME"] = self.username
        os.environ["SIMPLELOGIN_PASSWORD"] = self.dash_secret
        build_call = "systemctl --user start ovos-dashboard@'{0}'.service".format(
            self.dash_secret)
        LOG.debug(f'Starting dash with: `{build_call}`')
        dash_create = subprocess.run(build_call, shell=True,
                                     env=dict(os.environ))
        LOG.debug(f'Dash returned: {dash_create.returncode}')
        # time.sleep(3)
        self.handle_device_dashboard_status_check(message)

    def handle_device_developer_disable_dash(self, message):
        build_call = "systemctl --user stop ovos-dashboard@'{0}'.service".format(
            self.dash_secret)
        subprocess.Popen([build_call], shell=True)
        time.sleep(3)

        if not self._check_dash_running():
            self.bus.emit(Message("ovos.PHAL.dashboard.status.response",
                                  {"status": False, "url": None, "user": None,
                                   "password": None}))
