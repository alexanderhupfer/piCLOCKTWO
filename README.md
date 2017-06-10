# piCLOCKTWO
A watch face with temperature display on a small display

Installation:

copy clocktwo.service to /lib/systemd/system/
make startup.sh executable

enable with systemd: 
sudo systemctl enable clocktwo.service

set timezone using: sudo dpkg-reconfigure tzdata

sudo pip install xmltodict

and reboot...
