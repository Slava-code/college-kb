---
title: "Laptop Wi-Fi drops in one lecture hall"
type: incident
status: done
description: "DEMO: Example laptop lost campus Wi-Fi every few minutes in one building; stale network profile, fixed 2099-09-26"
updated: 2099-09-26
---

> DEMO — fictional example; delete once you add real pages.

# Laptop Wi-Fi drops in one lecture hall (2099-09-25)

## TL;DR

In the DEMO 101 lecture hall, [[devices/example-laptop]] lost campus Wi-Fi every 3–5 minutes. Other buildings were fine. The cause was a stale campus network profile left over from orientation week, still holding an old certificate. Forgetting the network and re-joining fixed it.

## Timeline of evidence

- 2099-09-25 09:05: first drop during lecture; reconnects after about 20 s. [Source: session notes]
- 2099-09-25 09:30: a classmate's phone stays connected in the same seat, so the room's access point is up.
- 2099-09-25 14:00: no drops in the library over 2 hours.
- 2099-09-26 08:55: after forgetting and re-adding the network, no drops for the whole lecture.

## Root cause

A duplicate network profile with an expired certificate. In that building the laptop kept roaming to the stale profile and failing authentication.

## Theories that were wrong

- **"The access point in that room is overloaded."** Ruled out: other devices in the same seat stayed connected.
- **"The VPN client is dropping the link."** Ruled out: drops happened with the VPN off too.

## Diagnostics that helped

- The OS network log, filtered for authentication failures, showed the old certificate name.

## Prevention

- After an IT certificate rotation, remove old campus network profiles before re-joining.
