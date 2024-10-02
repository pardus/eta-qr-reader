# ETA QR Code Reader

ETA QR Reader is an application that reads QR codes from the screen.

[![Packaging status](https://repology.org/badge/vertical-allrepos/eta-qr-reader.svg)](https://repology.org/project/eta-qr-reader/versions)

### **Dependencies**

This application is developed based on Python3 and GTK+ 3. Dependencies:
```bash
gir1.2-ayatanaappindicator3-0.1 gir1.2-glib-2.0 gir1.2-gtk-3.0
```

### **Run Application from Source**

Install dependencies
```bash
sudo apt install gir1.2-ayatanaappindicator3-0.1 gir1.2-glib-2.0 gir1.2-gtk-3.0
```

Clone the repository
```bash
git clone https://github.com/pardus/eta-qr-reader.git ~/eta-qr-reader
```

Run application
```bash
python3 ~/eta-qr-reader/src/Main.py
```

### **Build deb package**

```bash
sudo apt install devscripts git-buildpackage
sudo mk-build-deps -ir
gbp buildpackage --git-export-dir=/tmp/build/eta-qr-reader -us -uc
```

### **Screenshots**

![eta-qr-reader 1](screenshots/eta-qr-reader-1.png)
