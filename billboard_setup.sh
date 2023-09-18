#!/usr/bin/env bash


gsettings set org.gnome.desktop.background picture-uri 'file:///home/zeta/billboard/images/wallpaper.png'

#no idle no lock
gsettings set org.gnome.desktop.session idle-delay 0
gsettings set org.gnome.desktop.screensaver lock-enabled false

if [ -f /usr/local/lib/docker/cli-plugins/docker-compose ]; then
    echo "docker compose already exists"
else
    #docker compose install
    sudo apt-get update && sudo apt-get -y install curl v4l-utils
    sudo mkdir -p /usr/local/lib/docker/cli-plugins  \
        && sudo curl -SL "https://github.com/docker/compose/releases/download/v2.15.1/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/lib/docker/cli-plugins/docker-compose
    sudo chmod +x /usr/local/lib/docker/cli-plugins/docker-compose  \
        && sudo usermod -aG docker ${USER} \
        && docker compose version # test installation
fi

#SWAP MEMORY SETTING
SWAP_SIZE=4
SWAP_PATH="/mnt/${SWAP_SIZE}GB.swap"

if swapon -s | grep $SWAP_PATH; then
  echo "swap file $SWAP_PATH is already on."
else
  if [ ! -f "$SWAP_PATH" ]; then
    sudo fallocate -l ${SWAP_SIZE}G $SWAP_PATH
    sudo chmod 600 $SWAP_PATH
    sudo mkswap $SWAP_PATH
    sudo swapon $SWAP_PATH
    echo -e "$SWAP_PATH swap swap defaults 0 0\n" | sudo tee -a /etc/fstab
    echo "$SWAP_PATH is activated."
  else
    current_size=$(sudo du -h $SWAP_PATH | cut -f1)
    if [ "$current_size" != "${SWAP_SIZE}G" ]; then
      echo "swap file $SWAP_PATH already exists but has the wrong size ($current_size). Deleting and creating a new one."
      sudo swapoff $SWAP_PATH
      sudo rm $SWAP_PATH
      sudo fallocate -l ${SWAP_SIZE}G $SWAP_PATH
      sudo chmod 600 $SWAP_PATH
      sudo mkswap $SWAP_PATH
      sudo swapon $SWAP_PATH
      echo -e "$SWAP_PATH swap swap defaults 0 0\n" | sudo tee -a /etc/fstab
      echo "$SWAP_PATH is activated."
    else
      sudo swapon $SWAP_PATH
      echo -e "$SWAP_PATH swap swap defaults 0 0\n" | sudo tee -a /etc/fstab
      echo "$SWAP_PATH is activated."
    fi
  fi
fi


#Default xhost setting
if [ -e "$HOME/.xsessionrc" ]; then
    if grep -q "xhost +" $HOME/.xsessionrc; then
        echo "xhost already"
    else
        echo "xhost +" >> "$HOME/.xsessionrc"
    fi
fi

#Default DISPLAY setting
if [ -e "$HOME/.bashrc" ]; then
    if grep -q "export DISPLAY=:0" $HOME/.bashrc; then
        echo "'export DISPLAY=:0' already"
    else
        echo "export DISPLAY=:0" >> "$HOME/.bashrc"
    fi
fi