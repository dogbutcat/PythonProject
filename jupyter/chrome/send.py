from chrome_cookie import chrome_cookies

import hashlib, binascii
import time
import threading
import websocket
import queue

from buffer_coder import BufferCoder


# get cookie
url = "https://www.douyu.com"
dict = chrome_cookies(url)
did = dict['dy_did']
stk = dict['acf_stk']

a = 999805542
s = 0

def crypto(e):
    global a, s
    t = f'{e[0]}{e[1]}{a}'
    r = hashlib.md5(t.encode()).hexdigest()
    for idx in range(s):
        r = hashlib.md5((r+str(a)).encode()).hexdigest()
    c = (binascii.crc32(bytes(r,'utf-8')) & 0xffffffff)
    return c

# crypto('123')
from format_msg import decode_msg

cdr = BufferCoder()
q = queue.Queue()
stop_event = threading.Event()
room_id = input("input room id:")


def input_thread(ws):
    while connected:
        user_input = input("Please Input: ")
        if stop_event.isSet():
            break
        if user_input != "":
            # q.put(user_input)
            if user_input == 'pause':
                time.sleep(30)
            else:
                t = int(time.time() * 1000)
                re = crypto([room_id, t])
                ws.send(cdr.encode(f'pe@=0/content@={user_input}/col@=0/type@=chatmessage/dy@={did}/sender@=2478605/ifs@=0/nc@=0/dat@=0/rev@=0/tts@={int(t // 1000)}/admzq@=0/cst@={t}/dmt@=0/re@={re}/'))

# 设置心跳包发送时间间隔（单位：秒）
heartbeat_interval = 30
kd = ""

def get_heartbeat_data():
    tick = int(time.time() * 1000 // 1000)
    heartbeat_data = cdr.encode(f'type@=keeplive/vbw@=0/cdn@=/tick@={tick}/kd@={kd}/')
    return heartbeat_data

def send_heartbeat(ws):
    # 发送心跳包
    ws.send(get_heartbeat_data())
    # 重新调度下一次发送心跳包
    global timer
    timer = threading.Timer(heartbeat_interval, send_heartbeat, [ws])
    timer.start()

def before_close():
    print('end at: {}'.format(time.strftime('%Y-%B-%d %H:%M:%S')))
    global connected, timer
    timer.cancel()
    stop_event.set()
    connected = False

# def check_input_queue(ws):
#     while not stop_event.is_set():
#         if not q.empty() and connected:
#             user_input = q.get()
#             # 处理用户输入
#             print("你输入了：", user_input)
#             if user_input == 'exit':
#                 break
#             t = int(time.time() * 1000)
#             re = crypto([room_id, t])
#             ws.send(cdr.encode(f'pe@=0/content@={user_input}/col@=0/type@=chatmessage/dy@={did}/sender@=2478605/ifs@=0/nc@=0/dat@=0/rev@=0/tts@={int(t // 1000)}/admzq@=0/cst@={t}/dmt@=0/re@={re}/'))
#         # 执行其他操作
#         time.sleep(1)

def on_message(ws, message):
    def on_cdr_decoded(txt):
        obj = decode_msg(txt)
        if obj['type'] == 'chatmsg':
            print((f"[{obj['bnn']}/{obj['bl']}] " if obj.get('bnn') else '') + obj['nn'] + ": ", obj['txt'])
        elif obj['type'] == 'loginres':
            global a, s
            a = int(obj['rn'])
            s = int(obj['rct'])
            # ws.send(cdr.encode(f"type@=joingroup/rid@={room_id}/gid@=0/"))
            ws.send(cdr.encode(f'type@=h5ckreq/rid@={room_id}/ti@=220120230408/'))
            ws.send(get_heartbeat_data())
            timer.start()

            global sender
            sender = threading.Thread(target=input_thread, args=(ws,))
            sender.start()

            # 这样线程就会在后台一直运行，不会卡住主线程。需要注意的是，删除该行代码之后，需要通过其他方式来停止线程
            # sender.join()
        elif obj['type'] == 'chatres':
            print('send success')
        elif obj['type'] == 'keeplive':
            global kd
            # print(obj, kd)
            kd = obj['kd']
        # else:
            # print(obj)
    cdr.decode(message, on_cdr_decoded)

def on_error(ws, error):
    print(error)
    before_close()

def on_close(ws, close_status_code, close_msg):
    print("Connection closed")
    before_close()

def on_open(ws):
    print('start at: {}'.format(time.strftime('%Y-%B-%d %H:%M:%S')))
    # 发送登录消息
    # start = f"type@=loginreq/roomid@={room_id}/dfl@=sn@AA=106@ASss@AA=1@Ssn@AA=107@ASss@AA=1@Ssn@AA=108@ASss@AA=1@Ssn@AA=105@ASss@AA=1@Ssn@AA=110@ASss@AA=1/username@=auto_U4FlKFzGj1/uid@=2478605/ver@=20220825/aver@=218101901/ct@=0/"
    t = int(time.time())
    s = r"r5*^5;}2#${XF[h+;'./.Q'1;,-]f'p["
    vk = hashlib.md5(f"{t}{s}{did}".encode()).hexdigest()
    startMsg = f"type@=loginreq/roomid@={room_id}/dfl@=sn@AA=106@ASss@AA=1@Ssn@AA=107@ASss@AA=1@Ssn@AA=108@ASss@AA=1@Ssn@AA=105@ASss@AA=1@Ssn@AA=110@ASss@AA=1/username@=auto_U4FlKFzGj1/password@=/ltkid@=25618386/biz@=1/stk@={stk}/devid@={did}/ct@=0/pt@=2/cvr@=0/tvr@=7/apd@=/rt@={t}/vk@={vk}/ver@=20220825/aver@=218101901/dmbt@=chrome/dmbv@=112/er@=1/"
    ws.send(cdr.encode(startMsg))

    global connected
    connected = True

    # 启动调度器，开始定时发送心跳包
    global timer
    timer = threading.Timer(heartbeat_interval, send_heartbeat, [ws])

if __name__ == "__main__":
    if room_id != "":
        websocket.enableTrace(False)
        ws = websocket.WebSocketApp(
            "wss://wsproxy.douyu.com:6671/",
            on_message = on_message,
            on_error = on_error,
            on_close = on_close,
            on_open = on_open,
        )
        ws.run_forever()
        # check_input_queue(ws)
