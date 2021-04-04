#!/usr/bin/env python3

from modules.configuration import ConfigurationAccessorType
from modules.extracts import configure, countdown, ignition, main_engine_start, preflight_checks, takeoff

if __name__ == '__main__':
    preflight_checks()

    configuration: ConfigurationAccessorType = configure()

    ignition(configuration)

    main_engine_start(configuration)

    countdown(configuration)

    takeoff(configuration)
