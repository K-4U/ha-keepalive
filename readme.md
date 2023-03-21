Home Assistant keep-alive
====

Simple project to be used with [Uptime Kuma](https://github.com/louislam/uptime-kuma) and a TP-Link HS100 or HS110.

Uses the [Python-Kasa](https://github.com/python-kasa/python-kasa) library to toggle a TP-link plug off, waits for 500 ms and then switches is 
back on again.

### UptimeKuma configuration

Create a notification for your monitor with the following details:

**Notification Type:** Webhook<br>
**Friendly name:** Does not matter<br>
**Post URL:** `http://example.org:8001/down` <br>
**Content Type:** `application/json`

### Environment variables:

| Name         | Required | Default | Description                                                                                               |
|--------------|----------|---------|-----------------------------------------------------------------------------------------------------------|
| PLUG_IP      | Yes      |         | IP address to the TP-Link plug                                                                            | 
| PLUG_NAME    | Yes      |         | Name of the TP-Link plug. Required for checking if it has the right plug                                  |
| HA_IP        | Yes      |         | IP address or hostname to your Home Assistant instance. Used to check if the instance is actually offline |
| MONITOR_NAME | Yes      |         | Name of your Kuma monitor. Used to check if the right monitor triggered the webhook                       |
| LISTEN_PORT  | No       | 8001    | Port the application listens on                                                                           |
| HA_PORT      | No       | 8123    | Port to your Home Assistant instance.                                                                     |


