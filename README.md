
## billboard
### spec
- h/w
  - jetson nano 
- s/w
  - 18.04(bionic)
  - jepack 4.7.1
- ros
  - melodic(docker)

### 08.23
- zetabankhub/edu:melodic-billboard 생성

1. wifi 연결
   - zeta_billboard / 12345678
   - ip주소 바꾸기
     - ip address 10.42.100.100
     - netmask 255.255.255.0
     - gateway 10.42.100.1
2. ssh zeta@10.42.100.100 / password

3. 초기 작업
```bash
cd billboard
sudo chmod +x billboard_setup.sh
./billboard_setup.sh
source ~/.bashrc
source ~/.xsessionrc
```
4. 자동 실행
```bash
mkdir ~/.config/autostart
vim ~/.config/autostart/billboard.desktop
---
[Desktop Entry]
Type=Application
Exec=/home/zeta/billboard/scripts/billboard_autostart.sh
Hidden=false
NoDisplay=false
X-GNOME-Autostart-enabled=true
Name[en_US]=billboard
Name=billboard
Comment[en_US]=
Comment=
---

sudo chmod +x /home/zeta/billboard/scripts/billboard_autostart.sh

sudo vim /usr/local/bin/start-docker-compose.sh
---
#!/bin/bash
xhost +
cd /home/zeta/billboard
docker compose up -d
---
sudo chmod +x /usr/local/bin/start-docker-compose.sh

```