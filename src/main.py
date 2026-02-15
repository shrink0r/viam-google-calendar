import asyncio
from viam.module.module import Module
from .models.google_calendar import GoogleCalendar


if __name__ == "__main__":
    asyncio.run(Module.run_from_registry())
