"""Tests for the Tesla device tracker."""

from homeassistant.components.device_tracker import DOMAIN as DEVICE_TRACKER_DOMAIN
from homeassistant.const import STATE_UNKNOWN
from homeassistant.core import HomeAssistant
from homeassistant.helpers import entity_registry as er

from .common import setup_platform
from .mock_data import car as car_mock_data

# async def test_registry_entries(hass: HomeAssistant) -> None:
#     """Tests devices are registered in the entity registry."""
#     await setup_platform(hass, DEVICE_TRACKER_DOMAIN)

#     entity_registry = er.async_get(hass)

#     entry = entity_registry.async_get("device_tracker.my_model_s_location_tracker")
#     assert entry.unique_id == f"{car_mock_data.VIN.lower()}_location_tracker"


# async def test_car_location(hass: HomeAssistant) -> None:
#     """Tests car location is getting the correct value."""
#     await setup_platform(hass, DEVICE_TRACKER_DOMAIN)

#     state = hass.states.get("device_tracker.my_model_s_location_tracker")

#     assert (
#         state.attributes.get("heading")
#         == car_mock_data.VEHICLE_DATA["drive_state"]["heading"]
#     )
#     assert (
#         state.attributes.get("speed")
#         == car_mock_data.VEHICLE_DATA["drive_state"]["speed"]
#     )

# async def test_car_destination_location(hass: HomeAssistant) -> None:
#     """Tests car destination location is getting the correct value."""
#     await setup_platform(hass, DEVICE_TRACKER_DOMAIN)

#     state = hass.states.get("device_tracker.my_model_s_destination_location_tracker")


async def test_car_destination_location_no_active_route(hass: HomeAssistant) -> None:
    """Tests car destination location is getting the correct value when there is no active route."""
    car_mock_data.VEHICLE_DATA["drive_state"]["active_route_miles_to_arrival"] = None

    await setup_platform(hass, DEVICE_TRACKER_DOMAIN)

    state = hass.states.get("device_tracker.my_model_s_destination_location_tracker")
    assert state.state == STATE_UNKNOWN
