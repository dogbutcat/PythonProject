# -*- coding: utf-8 -*
import frida
import sys

rdev = frida.get_remote_device()
pid = rdev.spawn("tv.danmaku.bili")
session = rdev.attach(pid)


src = open('./hookjs.js').read()
script = session.create_script(src)


def on_message(message, data):
    print(message)


script.on("message", on_message)
script.load()
rdev.resume(pid)
sys.stdin.read()