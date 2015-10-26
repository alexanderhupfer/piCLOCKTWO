# piCLOCKTWO
A watch face with temperature display on a small display

Installation:

put clocktwo into /etc/init.d/ (make sure it's executable)

then register initscript by:

sudo update-rc.d clocktwo defaults

set timezone using: sudo dpkg-reconfigure tzdata

sudo pip install xmltodict

and reboot...
