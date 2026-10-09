# Reolink Lumus floodlight for Home Assistant

A tiny custom integration that adds a **floodlight on/off entity** for the
Reolink Lumus (hardware `IPC_325C7`, firmware `v2.0.0.687_20102800`).

The official [Reolink integration](https://www.home-assistant.io/integrations/reolink)
does not create a light entity for this camera, because the firmware reports
`ledCtrl = 0` in its abilities. The camera does however accept the Baichuan
floodlight commands, so this integration sends them directly.

## How it works

- Reuses the existing Baichuan connection (TCP port 9000) of the official
  Reolink integration. No second login, no credentials to configure.
- Turn on/off: Baichuan `cmd_id 288` (`FloodlightManual`).
- State: Baichuan push `cmd_id 291` (`FloodlightStatusList`), so changes made
  in the Reolink app are reflected in Home Assistant.
- The entity is attached to the existing Reolink device.

## Requirements

- The official Reolink integration, set up and working for the camera.
- A Reolink Lumus that does not already expose a floodlight entity.

## Installation (HACS)

1. HACS → menu → **Custom repositories**.
2. Add `https://github.com/bitsbiter/HA---Reolink-Lumus-floodlight`, type **Integration**.
3. Download "Reolink Lumus floodlight" and restart Home Assistant.
4. Settings → Devices & services → **Add integration** → "Reolink Lumus floodlight".

A `Floodlight` light entity then appears on the camera device.

## Limitations

- On/off only, no brightness.
- The on command carries a duration of 180 seconds, after which the camera
  switches the light off by itself (`DURATION` in `light.py`).
- Relies on internals of the official integration (`runtime_data.host.api`)
  and of `reolink-aio`, so a Home Assistant update may require a small fix.
- Only tested on hardware `IPC_325C7` with firmware `v2.0.0.687_20102800`.
