# DEPRECATED - OVOS PHAL Dashboard Plugin

This repository is no longer maintained by OpenVoiceOS

___________________________________________________________
The Dashboard PHAL plugin provides a simple interface to start, stop and provide status for the onboard flask based web dashboard for the device a user can connect to using his local network.

# Requirements
- Requires OVOS Dashboard Application: https://github.com/OpenVoiceOS/OVOS-Dashboard

# Install
`pip install ovos-PHAL-plugin-dashboard`

# Event Details:

##### Dashboard Management System

- Enable GUI Dashboard Service:
```python
       # type: Request
       # "ovos.PHAL.dashboard.enable"
```

- Disable GUI Dashboard Service:
```python
       # type: Request
       # "ovos.PHAL.dashboard.disable"
```

- Get Dashboard Service Status:
```python
       # type: Request
       # "ovos.PHAL.dashboard.status"
```
