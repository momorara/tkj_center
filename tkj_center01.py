"""
2022/12/08  家のエアコン,除湿器のコントロールWebApp
            このプログラムはブラウザをリロードするたびに起動します。
"""

import streamlit as st
import paho.mqtt.client as mqtt     # MQTTのライブラリをインポート
from time import sleep              # 3秒間のウェイトのために使う
 
# ブローカーに接続できたときの処理
def on_connect(client, userdata, flag, rc):
  print("Connected with result code " + str(rc))

# ブローカーが切断したときの処理
def on_disconnect(client, userdata, flag, rc):
  if rc != 0:
     print("Unexpected disconnection.")

# publishが完了したときの処理
def on_publish(client, userdata, mid):
  print("publish: {0}".format(mid))

def mqtt_pub(broker,pin_code,mes):
    try:
        client = mqtt.Client()                 # クラスのインスタンス(実体)の作成
        client.on_connect = on_connect         # 接続時のコールバック関数を登録
        client.on_disconnect = on_disconnect   # 切断時のコールバックを登録
        client.on_publish = on_publish         # メッセージ送信時のコールバック
        print()
        print('***',broker,'***')
        sleep(1)
        client.connect(broker, 1883, 60)  # 接続先は自分自身
        print('connect')
        sleep(1)
        # 通信処理スタート
        client.loop_start()    # subはloop_forever()だが，pubはloop_start()で起動だけさせる
        print('loop_start')
        sleep(3)
        # 除湿器スタートコマンド送信
        print('publish',mes)
        client.publish(mes,pin_code)
        sleep(1)
        # プローカーの調子が悪くmqttが通らなくてもエラーにならない
        # なので、2個届いてしまう。
    except:
        print('publish error')

def mqtt_broker_set(pin_code,mes):
    # ブローカーが調子の悪い時があるので、切り替えてpubします。
    # なので、調子の良い時には2つのpublishが届くので、注意が必要
    broker = 'mqtt.eclipseprojects.io' 
    mqtt_pub(broker,pin_code,mes)
    broker = 'broker.emqx.io'
    mqtt_pub(broker,pin_code,mes)

def input():
    # webAppの画面を構成
    st.title('TKJ center')
    date1 = st.date_input('Input date1')
    date2 = st.date_input('Input date2')
    pin_code = st.text_input('セキュリティコードを6桁で入力してください。')
    #print('pin_code',pin_code)
    air_on  = st.button('エアコンON')
    air_off = st.button('エアコンOFF')
    defumdy = st.button('除湿器ON/OFF')
    return pin_code,air_on,air_off,defumdy,date1,date2

def main():
    pin_code,air_on,air_off,defumdy,date1,date2 = input()
    #st.write(date1,date2)
    st.write(pin_code)
    st.write(air_on,air_off,defumdy)

    # 入力した日付からpin_codeを作ります。
    # セキュリティコードは実はダミーです。
    date1_str = date1.strftime('%Y-%m-%d')[-2:]
    date2_str = date2.strftime('%Y-%m-%d')[-2:]
    pin_code = date1_str + date2_str

    # 押されたボタンによって、publish内容を変える。
    if air_on == True :
        mes = "aircon/Operation_command/air_on"
    if air_off == True :
        mes = "aircon/Operation_command/air_off"
    if defumdy == True :
        mes = "dehumdy/Operation_command"

    # 一つでもボタンが押されていることが送信の条件
    if air_on == True or air_off == True or defumdy == True:
        # ピンコードをmqttでpublishする
        # st.write('publish',pin_code,mes)
        st.write('publish',mes)
        mqtt_broker_set(pin_code,mes)


if __name__ == '__main__':
    main()