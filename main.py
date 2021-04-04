#!/usr/bin/env python3

from modules.configuration import ConfigurationAccessorType
from modules.extracts import configure, countdown, ignition, main_engine_start, orbital_checkout, preflight_checks, \
    takeoff, to_infinity

if __name__ == '__main__':
    preflight_checks()

    configuration: ConfigurationAccessorType = configure()

    ignition(configuration)

    main_engine_start(configuration)

    countdown(configuration)

    takeoff(configuration)

    orbital_checkout(configuration)

    to_infinity(configuration)
