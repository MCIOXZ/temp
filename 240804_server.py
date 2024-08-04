import asyncio
import websockets
from pynput.keyboard import Key, Controller
import json
import ctypes
keyboard = Controller()
# 维护粘滞键状态
sticky_keys = {
    'Shift': False,
    'Ctrl': False,
    'Win': False,
    'Alt': False
}

def is_caps_lock_on():
    # Get the state of the Caps Lock key
    hllDll = ctypes.WinDLL("User32.dll")
    VK_CAPITAL = 0x14
    return hllDll.GetKeyState(VK_CAPITAL) & 1

async def handler(websocket, path):
    global sticky_keys
    print(f"连接来自: {path}")
    async for message in websocket:
        data = json.loads(message)
        print(websocket)
        if data['type'] == 'STICKY_KEY':
            key = data['key']
            sticky_keys[key] = not sticky_keys[key]
            if sticky_keys[key]:
                keyboard.press(key.capitalize())
            else:
                keyboard.release(key.capitalize())
            # 返回当前粘滞键状态
            print(f"粘滞键：{json.dumps({'type': 'STICKY_KEYS', 'stickyKeys': sticky_keys})}")
            await websocket.send(json.dumps({'type': 'STICKY_KEYS', 'stickyKeys': sticky_keys}))
        
        elif data['type'] == 'KEY_PRESS':
            key = data['key'] 
            keyboard.press(key)
            keyboard.release(key)
            state="On" if is_caps_lock_on() else "Off"
            await websocket.send(json.dumps({'type': 'CAPS_LOCK', 'state':state}))
            # keyboard.release(key)
        # 打印收到的按键请求
        print(f"收到按键请求: {data}")

async def main():
    async with websockets.serve(handler, "0.0.0.0", 8765):
        await asyncio.Future()  # run forever

if __name__ == "__main__":
    asyncio.run(main())
