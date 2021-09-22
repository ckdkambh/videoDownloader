from flask import Flask,request
from flask import render_template
import shelve
import time
from multiprocessing import Process, Queue
import json
from downloadstreamvideo import downloadVideo

app = Flask(__name__)
g_process_list = {}


@app.route('/')
def hello_world():
    dbase = shelve.open("mydbase")
    anchorList = dbase['anchorList']
    dbase.close()
    return render_template('index.html', anchorList = anchorList)

@app.route('/addName', methods=["POST"])
def addName():
    name = request.form['name']
    dbase = shelve.open("mydbase")
    tmplist = dbase['anchorList']
    if name not in tmplist:
        tmplist.append(name)
        dbase['anchorList'] = tmplist
        dbase.close()
        return name
    return ""

@app.route('/delName', methods=["POST"])
def delName():
    name = request.form['name']
    dbase = shelve.open("mydbase")
    tmplist = dbase['anchorList']
    tmplist.remove(name)
    dbase['anchorList'] = tmplist
    dbase.close()
    return name

@app.route('/download', methods=["POST"])
def download():
    name = request.form['name']
    videoUrl = request.form['videoUrl']
    if name not in g_process_list:
        q = Queue(1)
        p = Process(target=downloadVideo, args=(name, videoUrl, q))
        p.start()
        g_process_list[name] = [p, q]
    return ""

@app.route('/watch', methods=["GET"])
def watch():
    result = []
    for k, v in g_process_list.items():
        try:
            info = v[1].get_nowait()
            result.append({
                "name" : k,
                "state" : v[0].is_alive(),
                "totalSize" : info["totalSize"] if "totalSize" in info else 0,
                "totalFileNum" : info["totalFileNum"] if "totalFileNum" in info else 0,
                "currentSize" : info["currentSize"] if "currentSize" in info else 0})
        except:
            result.append({
                "name" : k,
                "state" : v[0].is_alive(),
                "totalSize" : 0,
                "totalFileNum" : 0,
                "currentSize" : 0})
        try:
            v[1].put_nowait(info)
        except:
            pass
    return json.dumps(result, ensure_ascii = False)

@app.route('/deleteProcess', methods=["POST"])
def deleteProcess():
    name = request.form['name']
    if name in g_process_list:
        p = g_process_list[name]
        p.terminate()
        del g_process_list[name]
    return ""

if __name__ == '__main__':
    # dbase = shelve.open("mydbase")
    # dbase['anchorList'] = ['腐团儿', 'Minana呀', '苏恩Olivia', 'Chance喵',  '张琪格', 'Sun佐伊',  '小a懿', '秀秀呢']
    # dbase.close()
    app.run(host='127.0.0.1', port=18888)