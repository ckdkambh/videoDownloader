import requests
from datetime import datetime
import time
import sys, getopt,os
from multiprocessing import Queue

maxSize = 100*1024000
maxConnectTry = 30
outpath = 'D:\\MY_DownLoad\\'
file_url = """
https://fb0ad1f5f3b6eea213cf5447c66e2753.v.smtcdns.net/mobilep2.douyucdn2.cn/dyliveflv3a/549212rJJKi5Eg67.xs?playid=1632223170348-8128119341&uuid=f806ed7c-2c24-4483-a6b0-cb1c64d7a00b&txSecret=b9a391cb8d6a354459c337eaa865c311&txTime=6149c21a&origin=tct
"""

# True False
# 斗鱼需要 flash模式的 高清才能下载，超清无法下载  11111 影熙热舞妖精 恩熙ovo 小深深儿 朴雨彬

g_UseDirName = True 
# 腐团儿 Minana呀 苏恩Olivia Chance喵  张琪格 Sun佐伊  小a懿 南妹儿呀 夏只只i 性感热舞阿离 乔妹eve 大宝好哇塞呀  宝儿lucky 暴躁的鹿鹿猪  王羽杉Barbieshy 陈小花呢 Lovely璐璐酱 猫九酱O3O      暴走小卡车 萌宝绵绵Z啊 王羽杉Barbieshy 米儿啊i 素素不吃肉  淼淼喵酱呀 是Ari瑞哥 
# 湖南小橙子 沈亦Mona 尹恩恩1 VIVI小小酥 阿让让丶 Y智恩 何菱

# 秀秀呢 lone考拉  你的咪咪酱 子诺小姐姐 Ss莹莹酱 珊儿兔兔兔 MICO要抱抱 子然学姐 舞法天女小慕林 Ellin艾琳  同桌小美 Sunny温晴
# 你的口罩表妹 陈小花呢 血色东霓 秀秀呢



DirName = "慕一cc"

def analysisFileName(url):
    fileName = url
    print(fileName)
    outfile = outpath+fileName
    date = datetime.now().__str__()
    date = date.replace(' ', '').replace('-', '').replace(':', '').replace('.', '')
    outfile = outfile.split('.')[0]+'_'+date+'.flv'
    return outfile

def getNextFileName(fileName):
    index1 = fileName.split('.')[0]
    index2 = index1.find('##')
    index3 = 1
    if index2 == -1:
        index2 = len(index1)
    else:
        index3 = fileName[index2+2:len(index1)]
        index3 = int(index3) + 1
    return fileName[:index2]+'##'+str(index3)+'.flv'

def get_FileSize(filePath):
    fsize = os.path.getsize(filePath)
    fsize = fsize/float(1024)
    return round(fsize,2)

def get_is_dispersed(link):
    print(link.find('type='))
    print(len(link))
    if link.find('type=')>len(link)-8:
        return True
    return False
    
def get_dispersed_index(link):
    i=link.rfind('/')
    j=link.rfind('.')
    if i!=-1 and j!=-1:
        return link[i+1:j]
    else:
        print('get_dispersed_index error')
        exit(0)
    
def get_next_num_link(link):
    cur_num=get_dispersed_index(link)
    next_num=hex(int(cur_num,16)+1)
    i=link.rfind('/')
    j=link.rfind('.')
    return link[:i+1]+next_num[2:]+link[j:]
    
def downloadVideo(name, url, queue):
    count = 0
    connectTryCount = 0
    last_work_time = time.time()

    totalSize = 0
    totalFileNum = 0
    
    is_dispersed = get_is_dispersed(url)
    if is_dispersed:
        print('current index is:%s'%(get_dispersed_index(url)))
        print('nxet index is:%s'%(get_next_num_link(url)))
        exit(0)
    fileName = analysisFileName(name)
    headers = {'user-agent': 'Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.98 Safari/537.36 LBBROWSER'}
    while(True):
        if connectTryCount > maxConnectTry:
            print('reach maxmium times of try, exit')
            break
        try:
            r = requests.get(url, stream=True, timeout=1, headers=headers, verify=False)
        except OSError as e:
            print(e)
            print('link break wait to connect, %dth try...' % (connectTryCount))
            time.sleep(1)
            connectTryCount = connectTryCount + 1
            continue
        if time.time() - last_work_time < 2:
            time.sleep(10)
            print('too fast, stop download!')
            continue
        else:
            last_work_time = time.time()
            
        count = 0
        fileName = getNextFileName(fileName)
        print('start download to ', fileName)
        with open(fileName, "wb") as pdf:
            try:
                for chunk in r.iter_content(chunk_size=1024000):
                    if count < maxSize and chunk:
                        pdf.write(chunk)
                        count = count + chunk.__sizeof__()
                        updateQueue(queue, totalSize, totalFileNum, count)
                    else:
                        break
            except OSError as e:
                print('link break close current file, wait for link resume')

        if os.path.exists(fileName) and get_FileSize(fileName) < 800:
            connectTryCount = connectTryCount + 1
            print('file:%s too small(%dKB), delete!'%(fileName, get_FileSize(fileName)))
            try:
                os.remove(fileName)
            except IOError as e:
                print(e)
                continue
        else:
            connectTryCount = 0
            totalFileNum = totalFileNum + 1
            totalSize = totalSize + os.path.getsize(fileName)
            updateQueue(queue, totalSize, totalFileNum, 0)
    print('complete')

def updateQueue(queue, totalSize, totalFileNum, currentSize):
    try:
        queue.get_nowait()
    except:
        pass
    try:
        queue.put_nowait({ "totalSize" : totalSize, 'totalFileNum' : totalFileNum, "currentSize" : currentSize})
    except:
        pass


if __name__=="__main__":
    downloadVideo(DirName, file_url)
