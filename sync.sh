nix shell nixpkgs#usbutils nixpkgs#screen
cd /dev/serial/by-id
sudo screen usb-Ultima_Keyboard_4BA354DAE28D-if00 115200
sudo mount /dev/sda1 /mnt
sudo cp main_ewi.py /mnt/main.py
