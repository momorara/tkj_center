"""
2022/12/08  家のエアコン,除湿器のコントロールWebApp
            このプログラムはブラウザをリロードするたびに起動します。
2022/12/18  温度湿度のファィルを読んで表示
            sub_humedy,tempを起動 1つだけ起動するように工夫する
2023/07/17  sozuのためにボタンを追加、offはizumoと共用
2023/08/28  ハッキングが疑われるので、アドレスを変更
"""

import streamlit as st
import paho.mqtt.client as mqtt     # MQTTのライブラリをインポート
from time import sleep              # 3秒間のウェイトのために使う
import os
import subprocess
import time

# --------------- subを立ち上げる ---------------
# ファイルがあるか無いかを確認する。
if os.path.exists('sub_flag.txt'):
    with open('sub_flag.txt') as f:
        sub_flag = f.read()
    if sub_flag == 'stop':
        prog = 'python3 ' + 'sub_temp.py'
        subprocess.Popen(prog, shell=True)
        prog = 'python3 ' + 'sub_humedy.py'
        subprocess.Popen(prog, shell=True)
else:
    st.info('sub_flag.txtがありません')

# --------------- publish ---------------
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
    date1 = st.date_input('Input date1')
    date2 = st.date_input('Input date2')
    
    #print('pin_code',pin_code)
    air_on_izumo  = st.button('エアコンON @ izumo')
    air_off = st.button('エアコンOFF')
    air_on_sozu  = st.button('エアコンON @ sozu')
    defumdy = st.button('除湿器ON/OFF')
    return air_on_izumo,air_off,air_on_sozu,defumdy,date1,date2

def main():

    st.title('TKJ center')
    # with open('humdy.txt', mode='w') as f: #上書き
    #     f.write('99')
    # time.sleep(5)
    # st.title('TKJ center')

    # ラズパイからのメッセージをsub_**で受けてファイルを作っているので、
    # そのデータを表示する。
    if os.path.exists('temp.txt'):
        with open('temp.txt') as f:
            temp = f.read()
    else:
        temp = 'no file'
    if os.path.exists('humdy.txt'):
        with open('humdy.txt') as f:
            humdy = f.read()
    else:
        humdy = 'no file'

    st.write("温度:",temp," / 湿度:",humdy)

    air_on_izumo,air_off,air_on_sozu,defumdy,date1,date2 = input()
    st.write(air_on_izumo,air_off,air_on_sozu,defumdy)

    # 入力した日付からpin_codeを作ります。
    date1_str = date1.strftime('%Y-%m-%d')[-2:]
    date2_str = date2.strftime('%Y-%m-%d')[-2:]
    pin_code = date1_str + date2_str

    # 押されたボタンによって、publish内容を変える。
    if air_on_izumo == True :
        mes = "aircon/Operation_command/air_on"
    if air_off == True :
        mes = "aircon/Operation_command/air_off"
    if air_on_sozu == True :
        mes = "aircon/Operation_command/sozu_air_on"   # air_on_sozuではダメみたい
                                                       # ハッキング対策でアドレス変更 旧:air_sozu_on     
    if defumdy == True :
        mes = "dehumdy/Operation_command"

    # 一つでもボタンが押されていることが送信の条件
    if air_on_izumo == True or air_off == True or air_on_sozu == True or defumdy == True:
        # ピンコードをmqttでpublishする
        # st.write('publish',pin_code,mes)
        st.write('publish',mes)
        mqtt_broker_set(pin_code,mes)

    # セキュリティコードは実はダミーです。
    pin_code = st.text_input('セキュリティコードを6桁で入力してください。')
    st.write("入力内容:",pin_code)

    # リセットボタンが押されたらsub起動フラグ、温度・湿度ファィルを削除
    reset  = st.button('reset')
    if reset == True :
        try:
            # これによりsubも自分で止まる
            with open('sub_flag.txt', mode='w') as f: #上書き
                f.write('stop')
            with open('temp.txt', mode='w') as f: #上書き
                f.write('null')
            with open('humdy.txt', mode='w') as f: #上書き
                f.write('null')
        except:
            pass


if __name__ == '__main__':
    main()
