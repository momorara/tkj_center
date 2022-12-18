#!usr/bin/env python
# -*- coding: utf-8 -*- 
"""
受信側

インストール
sudo pip3 install paho-mqtt

2022/04/14  ngrok起動テスト
2022/04/16
2022/12/18  除湿器、エアコンからのmqttを受信してファィルを作る
"""
import subprocess
import paho.mqtt.client as mqtt     # MQTTのライブラリをインポート
import os
import time



# ブローカー
#broker = 'mqtt.eclipseprojects.io'
broker  = 'broker.emqx.io'

# 受診するトピック
topic = "testmqtt/aircon/temp003"

# 起動の印を書く
with open('sub_flag.txt', mode='w') as f: #上書き
    f.write('run')


print('sub start')

# ブローカーに接続できたときの処理
def on_connect_sub(client, userdata, flag, rc):
    print("Connected with result code " + str(rc))  # 接続できた旨表示
    client.subscribe(topic)  # subするトピックを設定 

# ブローカーが切断したときの処理
def on_disconnect_sub(client, userdata, flag, rc):
    if  rc != 0:
        print("Unexpected disconnection.")

# メッセージが届いたときの処理
def on_message(client, userdata, msg):
    # msg.topicにトピック名が，msg.payloadに届いたデータ本体が入っている
    # print("Received message '" + str(msg.payload) + "' on topic '" + msg.topic + "' with QoS " + str(msg.qos))

    # print(msg.payload)
    # print(type(msg.payload))

    mes = msg.payload
    mes = str(mes, encoding='utf-8', errors='replace')
    print(mes)
    with open('temp.txt', mode='w') as f: #上書き
        f.write(mes)


# MQTTの接続設定
client = mqtt.Client()                 # クラスのインスタンス(実体)の作成
client.on_connect = on_connect_sub         # 接続時のコールバック関数を登録
client.on_disconnect = on_disconnect_sub   # 切断時のコールバックを登録
client.on_message = on_message         # メッセージ到着時のコールバック
client.connect(broker, 1883, 60)       # 接続先は自分自身
client.loop_start()                  # ループスタート
while True:
    with open('sub_flag.txt') as f:
        sub_flag = f.read()
    time.sleep(0.1)
    if sub_flag == 'stop':
        print("END!")
        break
