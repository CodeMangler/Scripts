netsh interface ip set address name="Ethernet" source=static addr=202.142.66.49 mask=255.255.255.0 gateway=202.142.66.1 gwmetric=0
netsh interface ip set dns name="Ethernet" source=static addr=202.142.66.7 register=NONE
netsh interface ip add dns name="Ethernet" addr=202.142.66.8 index=2
