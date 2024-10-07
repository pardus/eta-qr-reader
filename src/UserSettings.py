#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Oct  2 14:53:13 2024

@author: fatih
"""

import os
from configparser import ConfigParser
from pathlib import Path

import gi

gi.require_version("GLib", "2.0")
from gi.repository import GLib


class UserSettings(object):
    def __init__(self):
        self.default_autostart = True

        self.user_config_dir = Path.joinpath(Path(GLib.get_user_config_dir()), Path("eta/eta-qr-reader"))
        self.user_config_file = Path.joinpath(self.user_config_dir, Path("settings.ini"))

        self.autostart_dir = Path.joinpath(Path(GLib.get_user_config_dir()), Path("autostart"))
        self.autostart_file = Path.joinpath(self.autostart_dir, Path("tr.org.pardus.eta-qr-reader-autostart.desktop"))

        self.config = ConfigParser(strict=False)

        self.config_autostart = self.default_autostart

        if not Path.is_dir(self.user_config_dir):
            self.create_dir(self.user_config_dir)

    def create_default_config(self, force=False):
        self.config['Main'] = {"autostart": self.default_autostart}

        if not Path.is_file(self.user_config_file) or force:
            if self.create_dir(self.user_config_dir):
                with open(self.user_config_file, "w") as cf:
                    self.config.write(cf)

    def read_config(self):
        try:
            self.config.read(self.user_config_file)
            self.config_autostart = self.config.getboolean('Main', 'autostart')
        except Exception as e:
            print("{}".format(e))
            print("user config read error ! Trying create defaults")
            # if not read; try to create defaults
            self.config_autostart = self.default_autostart
            try:
                self.create_default_config(force=True)
            except Exception as e:
                print("self.createDefaultConfig(force=True) : {}".format(e))

    def write_config(self, autostart):
        self.config['Main'] = {"autostart": autostart}
        if self.create_dir(self.user_config_dir):
            with open(self.user_config_file, "w") as cf:
                self.config.write(cf)
                return True
        return False

    def create_dir(self, dir_path):
        try:
            Path(dir_path).mkdir(parents=True, exist_ok=True)
            return True
        except:
            print("{} : {}".format("mkdir error", dir_path))
            return False

    def set_autostart(self, state):
        self.create_dir(self.autostart_dir)
        if state:
            if not self.autostart_file.exists():
                self.autostart_file.symlink_to(
                    os.path.dirname(
                        os.path.abspath(__file__)) + "/../data/tr.org.pardus.eta-qr-reader-autostart.desktop")
        else:
            if self.autostart_file.exists():
                self.autostart_file.unlink(missing_ok=True)
