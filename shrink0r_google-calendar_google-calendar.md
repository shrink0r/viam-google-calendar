# Model shrink0r:google-calendar:google-calendar

Provides API access to a calendar via sharing with the configured service account.

## Configuration
The following attribute template can be used to configure this model:

```json
{
  "service_account_file": "/ABS/PATH/TO/SERVICE_ACCOUNT_KEY.json",
  "calendar_id": "YOUR_CALENDAR_ID@calendar.google.com"
}
```

### Attributes

The following attributes are available for this model:

| Name                   | Type   | Inclusion | Description                |
|------------------------|--------|-----------|----------------------------|
| `service_account_file` | string | Required  | Google Cloud JSON-Key for ServiceAccount |
| `calendar_id`          | string | Required  | Google Calendar ID (Shared with SA above) |

### Example Configuration

```json
{
  "service_account_file": "/Users/foobar/.service_accounts/viam-calendar-asdasd-2332423.json",
  "calendar_id": "asd234211ed6b338eacd437f7ssad221@group.calendar.google.com"
}
```

## DoCommand

Test the configuration with the payload snippet below:

### Execute DoCommand

```json
{
  "get_events": {
    "max_results": 10
  }
}
```
