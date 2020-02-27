import subprocess
import re
import json
import pathlib
import datetime
import time
import chardet

LOG_FILE = 'log.txt'
LOW_THRESHOLD = 100
RECORD_COUNT = 100

wasError = False
count = 0
his = []

def log(s, toFile):
    print(s)
    if toFile:
        with open(LOG_FILE, 'a') as f:
            print(s, file=f, flush=True)

def WriteHis(t, his):
    if len(his) != 0:
        average = sum(his) / len(his)
        log(f'{t} 近{len(his)}次的平均速度: {average} ms, 最大: {max(his)} ms, 最小: {min(his)} ms', True)
        his.clear()

def RunEng(cmd):
    ret = subprocess.run(cmd, capture_output=True, encoding='utf-8')
    pattern = r'bytes=\d+ time=(\d+)ms TTL=\d+\b'
    return re.search(pattern, ret.stdout)

def RunBig5(cmd):
    ret = subprocess.run(cmd, capture_output=True, encoding='Big5')
    pattern = r'位元組=\d+ 時間=(\d+)ms TTL=\d+\b'
    return re.search(pattern, ret.stdout)

def Run(cmd, encoding):
    if encoding == 'ascii':
        return RunEng(cmd)
    elif encoding == 'Big5':
        return RunBig5(cmd)
    else:
        raise f'Unsupport encoding'

encoding = chardet.detect(subprocess.run(['ping', '/?'], capture_output=True).stdout)['encoding']

while True:
    cmd = ['ping', '-n', '1', '-w', '2000', '8.8.8.8']
    t = str(datetime.datetime.now())
    if m := Run(cmd, encoding):
        if wasError:
            log(f'{count} {t}: connect', True)
            wasError = False
        speed = int(m.group(1))
        if (speed > LOW_THRESHOLD):
            print(f'{count} {str(datetime.datetime.now())}: slow: {speed}')
        his.append(speed)
        if len(his) == RECORD_COUNT:
            WriteHis(t, his)
    else:
        if not wasError:
            t = str(datetime.datetime.now())
            log(f'{count} {str(datetime.datetime.now())}: disconnect', True)
            wasError = True
            WriteHis(t, his)
    time.sleep(1)
    count += 1