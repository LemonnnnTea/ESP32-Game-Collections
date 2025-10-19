import network
import time

SSID = '1'
PASSWORD = '12345678'

station = network.WLAN(network.STA_IF)
station.active(True)

if not station.isconnected():
    print(f'正在连接到 {SSID}...')
    station.connect(SSID, PASSWORD)
    while not station.isconnected():
        print('.', end='')
        time.sleep(0.5)

print(f'\n连接成功! IP 地址: {station.ifconfig()[0]}')