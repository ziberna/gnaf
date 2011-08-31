Installation
============

Download the installer:

    $ git clone git@github.com:Kantist/gnaf-installer.git

Make files executable:

    $ cd gnaf-installer
    $ chmod +x {gnaf-install,gnaf-applet-install}

Install GNAF (the framework):

    $ ./gnaf-install

To install an official GNAF applet:

    $ ./gnaf-applet-install [APPLET-NAME]

To see list of the official applets:

    $ ./gnaf-applet-install

To install a custom applet simply copy the applet to .gnaf in your home directory:

    $ cp -r [APPLET-DIR] /home/your-username/.gnaf/[APPLET-NAME]


Settings
========

Settings are defined in the `/home/your-username/.gnaf/settings.py` file. See examples in that file for further information.


Running GNAF
============

To start GNAF run:

    $ gnaf

