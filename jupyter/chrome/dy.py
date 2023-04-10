# %pip install websocket-client

import threading
import websocket
import time

from buffer_coder import BufferCoder
from format_msg import decode_msg

# import sched
# import logging


cdr = BufferCoder()
room_id = input("input room id:")

# 设置心跳包发送时间间隔（单位：秒）
heartbeat_interval = 30
heartbeat_data = cdr.encode('type@=mrkl/')
# 创建调度器
# scheduler = sched.scheduler(time.time, time.sleep)


def send_heartbeat(ws):
    # 发送心跳包
    ws.send(heartbeat_data)
    # 重新调度下一次发送心跳包
    global timer
    timer = threading.Timer(heartbeat_interval, send_heartbeat, [ws])
    timer.start()
    # scheduler.enter(heartbeat_interval, 1, send_heartbeat, (ws,))

def on_message(ws, message):
    def on_cdr_decoded(txt):
        obj = decode_msg(txt)
        # print(obj)
        if obj['type'] == 'chatmsg':
            print((f"[{obj['bnn']}/{obj['bl']}] " if obj.get('bnn') else '') + obj['nn'] + ": ", obj['txt'])
        elif obj['type'] == 'loginres':
            ws.send(cdr.encode(f"type@=joingroup/rid@={room_id}/gid@=0/"))
            ws.send(heartbeat_data)
            timer.start()
            # scheduler.run()
        else:
            print(obj)


    cdr.decode(message, on_cdr_decoded)

def on_error(ws, error):
    print(error)

def on_close(ws, close_status_code, close_msg):
    print('end at: {}'.format(time.strftime('%Y-%B-%d %H:%M:%S')))
    print("Connection closed")
    global timer
    timer.cancel()
    # scheduler.cancel(e_hb)

def on_open(ws):
    print('start at: {}'.format(time.strftime('%Y-%B-%d %H:%M:%S')))
    # 发送登录消息
    start = f"type@=loginreq/roomid@={room_id}/dfl@=sn@AA=106@ASss@AA=1@Ssn@AA=107@ASss@AA=1@Ssn@AA=108@ASss@AA=1@Ssn@AA=105@ASss@AA=1@Ssn@AA=110@ASss@AA=1/username@=auto_U4FlKFzGj1/uid@=2478605/ver@=20220825/aver@=218101901/ct@=0/"
    ws.send(cdr.encode(start))

    # 启动调度器，开始定时发送心跳包
    global timer
    timer = threading.Timer(heartbeat_interval, send_heartbeat, [ws])
    # e_hb = scheduler.enter(heartbeat_interval, 1, send_heartbeat, (ws,))
    
    # 获取用户输入并发送消息
    # while True:
    #     msg = input()
    #     if msg:
    #         data = {
    #             "type": "chatmessage",
    #             "receiver": 0,
    #             "content": msg
    #         }
    #         ws.send(json.dumps(data))
        
if __name__ == "__main__":
    if room_id is not None:
        websocket.enableTrace(False)
        ws = websocket.WebSocketApp(
            "wss://danmuproxy.douyu.com:8503/",
            on_message = on_message,
            on_error = on_error,
            on_close = on_close,
            on_open = on_open,
        )
        ws.run_forever()
