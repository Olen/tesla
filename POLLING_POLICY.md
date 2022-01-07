# How polling works

Remember that there are two components involved here, both with their different timers.

- The Home Assistant integration (this repo). Here we have a static timer (not configurable) that will do an "update" every 60 seconds.
- This "update" done towards the [teslajsonpy component](https://github.com/zabuldon/teslajsonpy).

Whenever _teslajsonpy_ receives an `update()`-request from Home Assistant, it will poll Teslas servers for a list of cars.
For each car that is online (e.g. "awake") it will then check another timer, the `polling_interval` - which _is_ configureable and defaults to 660 seconds.
If the cars status was updated _more_ than `polling_interval` seconds ago, the teslajsonpy component will do another request to Tesla to fetch the full status information about the car and update Home Assistant.

So _no_ polling is done to the car unless the car is online (awake) AND the previous poll was at least `polling_interval` seconds ago.

## Some examples:

### Polling interval is set to 660 seconds (default)

- Every minute, Teslas servers are polled to check the online status of all cars.
- If any cars are online (awake) we check what time we last did a full poll of that car.
- If this was more than 660 seconds ago, we will do a new, full poll of the car.
- This will basically update the car status (locks, charge status etc) of all online (awake) cars every 12 minutes. The reason for this is that the polling takes som time, so it will usually have to wait an extra minute before "more than" 11 minutes has passed.

E.g. The first full poll happens at 12:00:00, but it takes a little while to complete, so "Last poll timestamp" is set to 12:00:01. Then a check is done every minute to scan for online cars. 12:01:00, 12:02:00, 12:03:00 etc. All the way to 12:11:00. However, since 12:11:00 is still NOT MORE than 11 minutes after 12:00:01, it will not do another full poll until 12:12:00.

As long as the car is still awake at 12:12:00, another full poll of the car is done, and Home Assitant is updated again.

### Polling interval is set to 60 seconds

- Every minute, Teslas servers are polled to check the online status of all cars.
- If any cars are online (awake) we check what time we last did a full poll of that car.
- If this was more than 60 seconds ago, we will do another full poll of the car.

Due to the "problem" described above, this means that a car is usually polled (and Home Assistant updated) only every 2 minutes when polling interval is set to 60 seconds.

### Polling interval is set to 30 seconds

- Every minute, Teslas servers are polled to check the online status of all cars.
- If any cars are online (awake) we check what time we last did a full poll of that car.
- If this was more than 30 seconds ago (which it obviously is, because we only check every 60 seconds), we will do another full poll of the car.

So this ensures that Home Assistant always have the latest (no more than 1 minute old) data, as long as the car is online (awake).

_The data will never be updated more frequently than every minute, as that is the set interval that the Home Assitant integration uses between each "update"-request it sends to teslajsonpy._

The `polling_interval` can be set using a service call:

```
service: tesla_custom.polling_interval
data:
  polling_interval: 120
```

This allows you to dynamically adjust the `polling_interval` based on criteria such as where the car is parked, battery SOC etc. to ensure you get the most updated information when you need it, while at the same time ensuring that the car can enter sleep mode when you need to preserve energy.

## Sleeping and waking up

With newer firmware, the car tries very hard to go to sleep. So even if you do a full poll every minute (e.g set `polling_interval` to < 60 seconds), the car will _usually_ go to sleep after being parked for a short while. When a car is waken up, either using the app, an API-call, or physcally by opening a door etc. it will _usually_ go back to sleep after 10-15 minutes, even if you keep on polling it.

However, there has been reports of polling keeping the car awake, so be careful, especially when parked without a charger connected, as the car will use significantly more energy when it is awake than when it sleeps.

But if you want to keep track of e.g. charge status etc on a regular interval, you need to make sure the car is awake, and wake up the car if it goes to sleep. This can be done using an automation that triggers when the "Online Binary Sensor" turns off to send an API-request to wake it up again. But be aware that it might drain your battery more than neccesary.
Also, you might want to adjust the `polling_interval` to ensure that the data is refreshed more often than every 11 (or 12) minutes. But keep an eye on the car status, to make sure it is actually going to sleep if you want that, if you lower that interval.

## Polling Policy

The _Polling Policy_ controls how aggressively we will poll the full status of a car. While the polling is done every `polling_interval` seconds, it is also dependent on other factors.

This integration will never touch a sleeping car. So as long as the car is sleeping, polling is skipped no matter what Polling Policy is set to.

If the car is in Drive (or Reverse) it will be polled every 60 seconds no matter what you set `polling_interval` to.

### Polling Policy: Normal (default)

With Polling Policy set to "normal" it will poll the car every `polling_interval` seconds as long as the following criteria is met:

- The car is awake
  And either
- Sentry mode is on or ...
- Climate is on or ...
- The car is actively charging

If none of the above criteria are met (except that the car is online), this policy will also throttle polling of the car back to minimum 660 seconds if the car has been parked for more than 10 minutes, no matter what you set as your `polling_interval`, to try to make sure the car will be able to sleep.

### Polling Policy: Connected

With Polling Policy set to "connected" it will poll the car every `polling_interval` seconds as long as the following criteria is met:

- The car is awake
  And either
- Sentry mode is on or ...
- Climate is on or ...
- The car is connected to a charger (even if it is not actively charging)

### Polling Policy: Always

With Polling Policy set to "always" it will poll the car every `polling_interval` seconds as long as the following criteria is met:

- The car is awake

## Potential Battery impacts

Here are some things to consider and understand when implementing the Tesla component and its potential effect on your car's battery.

- The default `polling_interval` is 660 seconds. Polling a car too frequently can keep the car awake and drain the battery. Different firmware versions and measurements of Tesla cars can take from 11 to 15 minutes for sleep mode to occur. There is no official information on sleep mode timings so your mileage may vary and you should experiment with different polling times for an optimal experience.
- The car will, however, be woken up when a command is actively sent to the car, such as door unlock or turning on the HVAC. It will then also fetch updated information while the car is awake based on the `polling_interval`.
- The car can intentionally be woken up to fetch recent information by sending a harmless command, for example, a lock command or a `WAKE_UP` API-call. This can be used in an automation to, for example, ensure that updated information is available every morning. (Note that the command must be valid for that specific car model. So locking the frunk of a Model 3 will not wake up that car).
- You can also toggle the `polling switch` on/off to disable polling of the vehicle completely via automations or the Lovelace UI.