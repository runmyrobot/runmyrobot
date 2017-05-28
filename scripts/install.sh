cd ~
wget ftp://ftp.alsa-project.org/pub/lib/alsa-lib-1.0.25.tar.bz2
tar xjf alsa-lib-1.0.25
cd alsa-lib-1.0.25
./configure --host=arm-unknown-linux-gnueabi
make -j4
sudo make install






