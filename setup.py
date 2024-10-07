#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Oct  2 14:53:13 2024

@author: fatihaltun
"""

import os
import subprocess

from setuptools import setup, find_packages


def create_mo_files():
    podir = "po"
    mo = []
    for po in os.listdir(podir):
        if po.endswith(".po"):
            os.makedirs("{}/{}/LC_MESSAGES".format(podir, po.split(".po")[0]), exist_ok=True)
            mo_file = "{}/{}/LC_MESSAGES/{}".format(podir, po.split(".po")[0], "eta-qr-reader.mo")
            msgfmt_cmd = 'msgfmt {} -o {}'.format(podir + "/" + po, mo_file)
            subprocess.call(msgfmt_cmd, shell=True)
            mo.append(("/usr/share/locale/" + po.split(".po")[0] + "/LC_MESSAGES",
                       ["po/" + po.split(".po")[0] + "/LC_MESSAGES/eta-qr-reader.mo"]))
    return mo


changelog = "debian/changelog"
if os.path.exists(changelog):
    head = open(changelog).readline()
    try:
        version = head.split("(")[1].split(")")[0]
    except:
        print("debian/changelog format is wrong for get version")
        version = "0.0.0"
    f = open("src/__version__", "w")
    f.write(version)
    f.close()

data_files = [
                 ("/usr/bin", ["eta-qr-reader"]),
                 ("/usr/share/applications",
                  ["data/tr.org.pardus.eta-qr-reader.desktop"]),
                 ("/usr/share/pardus/eta-qr-reader/ui",
                  ["ui/MainWindow.glade"]),
                 ("/usr/share/pardus/eta-qr-reader/src",
                  ["src/Main.py",
                   "src/MainWindow.py",
                   "src/UserSettings.py",
                   "src/__version__"]),
                 ("/usr/share/pardus/eta-qr-reader/data",
                  ["data/tr.org.pardus.eta-qr-reader.desktop",
                   "data/tr.org.pardus.eta-qr-reader-autostart.desktop"]),
                 ("/usr/share/icons/hicolor/scalable/apps/",
                  ["data/eta-qr-reader.svg",
                   "data/eta-qr-reader-symbolic.svg"]),
                 ("/etc/skel/.config/autostart",
                  ["data/tr.org.pardus.eta-qr-reader-autostart.desktop"])
             ] + create_mo_files()

setup(
    name="eta-qr-reader",
    version=version,
    packages=find_packages(),
    scripts=["eta-qr-reader"],
    install_requires=["PyGObject"],
    data_files=data_files,
    author="Fatih Altun",
    author_email="fatih.altun@pardus.org.tr",
    description="ETA QR Reader application.",
    license="GPLv3",
    keywords="eta-qr-reader",
    url="https://github.com/pardus/eta-qr-reader",
)
