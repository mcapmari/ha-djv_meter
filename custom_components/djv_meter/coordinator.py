"""Data coordinator for DJV-COM Meter integration."""
import logging

import requests
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator
from homeassistant.exceptions import ConfigEntryAuthFailed

_LOGGER = logging.getLogger(__name__)

class DJVMeterAPI:
    """API client for DJV-COM Meter."""
    
    def __init__(self, username: str, password: str) -> None:
        """Initialize the API client."""
        self.username = username
        self.password = password
        self.base_url = "http://djv-com.net:3000"
        self.token = None
        self.headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "Connection": "keep-alive",
            "Accept": "*/*",
            "User-Agent": "Balance/32 CFNetwork/1568.300.101 Darwin/24.2.0",
            "Accept-Language": "en-US,en;q=0.9",
            "Accept-Encoding": "gzip, deflate",
        }

    def login(self) -> None:
        """Authenticate with the API."""
        login_url = f"{self.base_url}/v1/pv/login"
        login_payload = {"username": self.username, "password": self.password}
        
        response = requests.post(login_url, json=login_payload, headers=self.headers)
        response.raise_for_status()
        
        data = response.json()
        if "data" not in data or "token" not in data["data"]:
            raise ConfigEntryAuthFailed("Invalid credentials")
            
        self.token = data["data"]["token"]
        self.headers["Authorization"] = f"Bearer {self.token}"

    def get_meter_data(self) -> dict:
        """Get meter data from the API."""
        if not self.token:
            self.login()
            
        url = f"{self.base_url}/v1/pv/getmeterdescriptionwithlastdata"
        response = requests.get(url, headers=self.headers)
        response.raise_for_status()
        return response.json()

    def test_connection(self) -> None:
        """Test the API connection."""
        self.login()

class DJVMeterDataUpdateCoordinator(DataUpdateCoordinator):
    """Class to manage fetching data from the API."""

    def __init__(
        self,
        hass: HomeAssistant,
        config: dict,
    ) -> None:
        """Initialize."""
        self.api = DJVMeterAPI(
            username=config["username"],
            password=config["password"],
        )

        super().__init__(
            hass,
            _LOGGER,
            name=f"DJV Meter {config['username']}",
        )

    async def _async_update_data(self):
        """Update data via library."""
        try:
            return await self.hass.async_add_executor_job(self.api.get_meter_data)
        except requests.exceptions.RequestException as error:
            _LOGGER.error("Error communicating with API: %s", error)
            raise ConfigEntryAuthFailed("Authentication failed") from error