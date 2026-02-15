from typing import ClassVar, Final, Mapping, Optional, Sequence, Tuple, List, Dict, Any

from typing_extensions import Self
from viam.proto.app.robot import ComponentConfig
from viam.proto.common import ResourceName
from viam.resource.base import ResourceBase
from viam.resource.easy_resource import EasyResource
from viam.resource.types import Model, ModelFamily
from viam.services.generic import *
from viam.utils import ValueTypes

import time
import asyncio
from google.oauth2 import service_account
from googleapiclient.discovery import build
import datetime


class GoogleCalendar(Generic, EasyResource):
    # To enable debug-level logging, either run viam-server with the --debug option,
    # or configure your resource/machine to display debug logs.
    MODEL: ClassVar[Model] = Model(
        ModelFamily("shrink0r", "google-calendar"), "google-calendar"
    )

    SCOPES: Final = ["https://www.googleapis.com/auth/calendar"]

    calendar_id: str
    service_account_file: str
    google_calendar_api: Any

    @classmethod
    def new(
        cls, config: ComponentConfig, dependencies: Mapping[ResourceName, ResourceBase]
    ) -> Self:
        """This method creates a new instance of this Generic service.
        The default implementation sets the name from the `config` parameter.

        Args:
            config (ComponentConfig): The configuration for this resource
            dependencies (Mapping[ResourceName, ResourceBase]): The dependencies (both required and optional)

        Returns:
            Self: The resource
        """
        self = super().new(config, dependencies)
        self.reconfigure(config, dependencies)
        return self

    @classmethod
    def validate_config(
        cls, config: ComponentConfig
    ) -> Tuple[Sequence[str], Sequence[str]]:
        """This method allows you to validate the configuration object received from the machine,
        as well as to return any required dependencies or optional dependencies based on that `config`.

        Args:
            config (ComponentConfig): The configuration for this resource

        Returns:
            Tuple[Sequence[str], Sequence[str]]: A tuple where the
                first element is a list of required dependencies and the
                second element is a list of optional dependencies
        """
        if not config.attributes.fields.get("calendar_id"):
            raise Exception("A 'calendar_id' must be defined in the configuration.")
        if not config.attributes.fields.get("service_account_file"):
            raise Exception(
                "A 'service_account_file' must be defined in the configuration."
            )
        return [], []

    def reconfigure(
        self, config: ComponentConfig, dependencies: Mapping[ResourceName, ResourceBase]
    ):
        self.logger.debug("reconfigure with config: %s", config)

        self.calendar_id = config.attributes.fields["calendar_id"].string_value
        self.service_account_file = config.attributes.fields[
            "service_account_file"
        ].string_value

        self.credentials = service_account.Credentials.from_service_account_file(
            self.service_account_file, scopes=self.SCOPES
        )
        self.google_calendar_api = build("calendar", "v3", credentials=self.credentials)

    async def do_command(
        self,
        command: Mapping[str, ValueTypes],
        *,
        timeout: Optional[float] = None,
        **kwargs,
    ) -> Mapping[str, ValueTypes]:
        self.logger.debug("executing `do_command` with: %s", command)

        if "get_events" in command:
            return {
                "events": self.get_events(command["get_events"].get("max_results", 10))
            }
        elif "add_event" in command:
            event_data = command["add_event"]
            return {"event_id": self.add_event(event_data)}
        elif "delete_event" in command:
            event_id = command["delete_event"].get("event_id")
            self.delete_event(event_id)
            return {"status": "Event deleted successfully."}
        else:
            raise Exception("Unknown command")

    # Fetch upcoming events
    def get_events(self, max_results: int = 10) -> List[Dict[str, Any]]:
        now = datetime.datetime.utcnow().isoformat() + "Z"
        events_result = (
            self.google_calendar_api.events()
            .list(
                calendarId=self.calendar_id,
                timeMin=now,
                maxResults=max_results,
                singleEvents=True,
                orderBy="startTime",
            )
            .execute()
        )
        events = events_result.get("items", [])
        self.logger.info(f"Fetched {len(events)} events.")
        return [
            {
                "summary": e.get("summary", "No Title"),
                "start": e["start"].get("dateTime", e["start"].get("date")),
                "end": e["end"].get("dateTime", e["end"].get("date")),
            }
            for e in events
        ]

    # Add a new event
    def add_event(self, event_data: Dict[str, Any]) -> str:
        event = (
            self.google_calendar_api.events()
            .insert(calendarId=self.calendar_id, body=event_data)
            .execute()
        )
        self.logger.info(f"Event created: {event.get('id')}")
        return event.get("id")

    # Delete an event
    def delete_event(self, event_id: str):
        self.google_calendar_api.events().delete(
            calendarId=self.calendar_id, eventId=event_id
        ).execute()
        self.logger.info(f"Event {event_id} deleted.")
