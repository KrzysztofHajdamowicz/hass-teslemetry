"""Binary Sensor platform for Teslemetry integration."""
from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
    BinarySensorEntityDescription,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import EntityCategory
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import StateType

from .const import DOMAIN, TeslemetryState
from .entity import (
    TeslemetryEnergyEntity,
    TeslemetryVehicleEntity,
    TeslemetryWallConnectorEntity,
)
from .coordinator import (
    TeslemetryEnergyDataCoordinator,
    TeslemetryVehicleDataCoordinator,
)
from .models import TeslemetryEnergyData, TeslemetryVehicleData


@dataclass(frozen=True, kw_only=True)
class TeslemetryBinarySensorEntityDescription(BinarySensorEntityDescription):
    """Describes Teslemetry binary sensor entity."""

    is_on: Callable[..., bool] = lambda x: x
    available_fn: Callable[[StateType], bool] = lambda x: x is not None


DESCRIPTIONS: tuple[TeslemetryBinarySensorEntityDescription, ...] = (
    TeslemetryBinarySensorEntityDescription(
        key="state",
        device_class=BinarySensorDeviceClass.CONNECTIVITY,
        is_on=lambda x: x == TeslemetryState.ONLINE,
    ),
    TeslemetryBinarySensorEntityDescription(
        key="charge_state_battery_heater_on",
        device_class=BinarySensorDeviceClass.HEAT,
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    TeslemetryBinarySensorEntityDescription(
        key="charge_state_preconditioning_enabled",
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    TeslemetryBinarySensorEntityDescription(
        key="charge_state_scheduled_charging_pending",
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    TeslemetryBinarySensorEntityDescription(
        key="charge_state_trip_charging",
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    TeslemetryBinarySensorEntityDescription(
        key="charge_state_conn_charge_cable",
        is_on=lambda x: x != "<invalid>",
        entity_category=EntityCategory.DIAGNOSTIC,
        device_class=BinarySensorDeviceClass.CONNECTIVITY,
    ),
    TeslemetryBinarySensorEntityDescription(
        key="climate_state_auto_seat_climate_left",
        device_class=BinarySensorDeviceClass.HEAT,
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    TeslemetryBinarySensorEntityDescription(
        key="climate_state_auto_seat_climate_right",
        device_class=BinarySensorDeviceClass.HEAT,
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    TeslemetryBinarySensorEntityDescription(
        key="climate_state_auto_steering_wheel_heat",
        device_class=BinarySensorDeviceClass.HEAT,
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    TeslemetryBinarySensorEntityDescription(
        key="climate_state_cabin_overheat_protection",
        device_class=BinarySensorDeviceClass.RUNNING,
        is_on=lambda x: x == "On",
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    TeslemetryBinarySensorEntityDescription(
        key="climate_state_cabin_overheat_protection_actively_cooling",
        device_class=BinarySensorDeviceClass.HEAT,
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    TeslemetryBinarySensorEntityDescription(
        key="vehicle_state_dashcam_state",
        device_class=BinarySensorDeviceClass.RUNNING,
        is_on=lambda x: x == "Recording",
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    TeslemetryBinarySensorEntityDescription(
        key="vehicle_state_is_user_present",
        device_class=BinarySensorDeviceClass.PRESENCE,
    ),
    TeslemetryBinarySensorEntityDescription(
        key="vehicle_state_tpms_soft_warning_fl",
        device_class=BinarySensorDeviceClass.PROBLEM,
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    TeslemetryBinarySensorEntityDescription(
        key="vehicle_state_tpms_soft_warning_fr",
        device_class=BinarySensorDeviceClass.PROBLEM,
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    TeslemetryBinarySensorEntityDescription(
        key="vehicle_state_tpms_soft_warning_rl",
        device_class=BinarySensorDeviceClass.PROBLEM,
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    TeslemetryBinarySensorEntityDescription(
        key="vehicle_state_tpms_soft_warning_rr",
        device_class=BinarySensorDeviceClass.PROBLEM,
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    TeslemetryBinarySensorEntityDescription(
        key="vehicle_state_fd_window",
        device_class=BinarySensorDeviceClass.WINDOW,
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    TeslemetryBinarySensorEntityDescription(
        key="vehicle_state_fp_window",
        device_class=BinarySensorDeviceClass.WINDOW,
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    TeslemetryBinarySensorEntityDescription(
        key="vehicle_state_rd_window",
        device_class=BinarySensorDeviceClass.WINDOW,
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    TeslemetryBinarySensorEntityDescription(
        key="vehicle_state_rp_window",
        device_class=BinarySensorDeviceClass.WINDOW,
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    TeslemetryBinarySensorEntityDescription(
        key="vehicle_state_df",
        device_class=BinarySensorDeviceClass.DOOR,
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    TeslemetryBinarySensorEntityDescription(
        key="vehicle_state_dr",
        device_class=BinarySensorDeviceClass.DOOR,
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    TeslemetryBinarySensorEntityDescription(
        key="vehicle_state_pf",
        device_class=BinarySensorDeviceClass.DOOR,
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    TeslemetryBinarySensorEntityDescription(
        key="vehicle_state_pr",
        device_class=BinarySensorDeviceClass.DOOR,
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
)


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Set up the Teslemetry binary sensor platform from a config entry."""
    data = hass.data[DOMAIN][entry.entry_id]

    async_add_entities(
        TeslemetryBinarySensorEntity(vehicle, description)
        for vehicle in data.vehicles
        for description in DESCRIPTIONS
    )


class TeslemetryBinarySensorEntity(TeslemetryVehicleEntity, BinarySensorEntity):
    """Base class for Teslemetry binary sensors."""

    entity_description: TeslemetryBinarySensorEntityDescription

    def __init__(
        self,
        vehicle: TeslemetryVehicleData,
        description: TeslemetryBinarySensorEntityDescription,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(vehicle, description.key)
        self.entity_description = description

    @property
    def is_on(self) -> bool:
        """Return the state of the binary sensor."""
        return self.entity_description.is_on(self.get())

    @property
    def available(self) -> bool:
        """Return if sensor is available."""
        return super().available and self.entity_description.available_fn(self.get())