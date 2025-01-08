"""Data coordinator for DJV-COM Meter integration."""
import logging
from datetime import datetime, timedelta

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
        try:
            login_url = f"{self.base_url}/v1/pv/login"
            login_payload = {"username": self.username, "password": self.password}
            
            response = requests.post(login_url, json=login_payload, headers=self.headers)
            response.raise_for_status()
            
            data = response.json()
            if "data" not in data or "token" not in data["data"]:
                raise ConfigEntryAuthFailed("Invalid credentials")
                
            self.token = data["data"]["token"]
            self.headers["Authorization"] = f"Bearer {self.token}"
        except requests.exceptions.RequestException as error:
            _LOGGER.error("Login failed: %s", error)
            raise

    def get_meter_data(self) -> dict:
        """Get meter data from the API."""
        try:
            # Login every time to get a fresh token
            self.login()
                
            url = f"{self.base_url}/v1/pv/getmeterdescriptionwithlastdata"
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.RequestException as error:
            _LOGGER.error("Failed to get meter data: %s", error)
            raise

    def test_connection(self) -> None:
        """Test the API connection."""
        self.login()

class DJVMeterDataUpdateCoordinator(DataUpdateCoordinator):
    """Class to manage fetching data from the API."""

    def __init__(
        self,
        hass: HomeAssistant,
        config: dict,
        update_interval: timedelta,
    ) -> None:
        """Initialize."""
        self.api = DJVMeterAPI(
            username=config["username"],
            password=config["password"],
        )
        self.hass = hass
        self.retry_count = 0
        self.max_retries = 3
        self.retry_interval = timedelta(minutes=5)
        self.last_successful_update = None

        super().__init__(
            hass,
            _LOGGER,
            name=f"DJV Meter {config['username']}",
            update_interval=update_interval,
        )

    async def _async_update_data(self):
        """Update data via library."""
        try:
            data = await self.hass.async_add_executor_job(self.api.get_meter_data)
            
            if data and "data" in data and data["data"]:
                self.last_successful_update = datetime.now()
                self.retry_count = 0
                return data
            else:
                raise ValueError("Received empty or invalid data")

        except (requests.exceptions.RequestException, ValueError) as error:
            _LOGGER.error("Error communicating with API: %s", error)
            
            if self.retry_count < self.max_retries:
                self.retry_count += 1
                retry_minutes = self.retry_interval.total_seconds() / 60
                _LOGGER.warning(
                    "Update failed. Attempting retry %s of %s in %s minutes",
                    self.retry_count,
                    self.max_retries,
                    retry_minutes
                )
                
                # Schedule retry
                self.hass.async_create_task(self.async_refresh())
                
                # Return last data if we have it
                if self.data:
                    return self.data
                
            if self.retry_count >= self.max_retries:
                _LOGGER.error(
                    "Maximum retry attempts (%s) reached. Will try again at next update. Last successful update: %s",
                    self.max_retries,
                    self.last_successful_update
                )
                
                # Return last data if we have it
                if self.data:
                    return self.data
            
            raise ConfigEntryAuthFailed("Failed to update data") from error