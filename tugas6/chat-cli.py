import socket
import json
import os
import base64
#rosy haqqy
TARGET_IP = "127.0.0.1"
TARGET_PORT = 8889

class ChatClient:
    def __init__(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_address = (TARGET_IP,TARGET_PORT)
        self.sock.connect(self.server_address)
        self.tokenid=""

    def proses(self,cmdline):
        j=cmdline.split(" ")
        try:
            command=j[0].strip()
            if (command=='login'):
                username=j[1].strip()
                password=j[2].strip()
                return self.login(username,password)
            elif (command=='register'):
                username=j[1].strip()
                password=j[2].strip()
                return self.register(username,password)
            elif (command=='logout'):
                return self.logout()
            elif (command=='getusername'):
                return self.getusername()
            elif (command=='inboxall'):
                return self.inboxall()
            elif (command=='inbox'):
                chatid=j[1].strip()
                return self.inbox(chatid)
            elif (command=='getnewchat'):
                return self.getnewchat()
            elif (command=='createchat'):
                username=j[1].strip()
                return self.createchat(username)
            elif (command=='creategroup'):
                groupname=j[1].strip()
                password=j[2].strip()
                return self.creategroup(groupname, password)
            elif (command=='joingroup'):
                groupid=j[1].strip()
                password=j[2].strip()
                return self.joingroup(groupid, password)
            elif (command=='sendmsg'):
                chatid=j[1].strip()
                message=""
                for w in j[2:]:
                   message="{} {}" . format(message,w)
                return self.sendmsg(chatid,message)
            elif (command=='sendfile'):
                return self.remote_post(self.tokenid,j[1],j[2])
            elif (command=='getfile'):
                return self.remote_get(self.tokenid,j[1],j[2])
            else:
                return "*Maaf, command tidak benar"
        except IndexError:
                return "-Maaf, command tidak benar"

    def sendstring(self,string):
        try:
            self.sock.sendall(string.encode())
            receivemsg = ""
            while True:
                data = self.sock.recv(1024)
                print("diterima dari server",data)
                if (data):
                    receivemsg = "{}{}" . format(receivemsg,data.decode())  #data harus didecode agar dapat di operasikan dalam bentuk string
                    if receivemsg[-4:]=='\r\n\r\n':
                        print("end of string")
                        return json.loads(receivemsg)
        except:
            self.sock.close()
            return { 'status' : 'ERROR', 'message' : 'Gagal'}

    def login(self,username,password):
        string="login {} {} \r\n" . format(username,password)
        result = self.sendstring(string)
        if result['status']=='OK':
            self.tokenid=result['tokenid']
            return "username {} logged in, token {} " .format(username,self.tokenid)
        else:
            return "Error, {}" . format(result['message'])
        
    def register(self,username,password):
        string="register {} {} \r\n" .format(username,password)
        result = self.sendstring(string)
        if result['status']=='OK':
            self.tokenid=result['tokenid']
            return "username {} registered, token {} " .format(username, self.tokenid)
        else:
            return "Error, {}" . format(result['message'])

    def remote_get(self, tokenid, chat_id, file_path):
        command_str=f"getfile {tokenid} {chat_id} {file_path} \r\n"
        hasil = self.sendstring(command_str)
        if (hasil['status']=='OK'):
            #proses file dalam bentuk base64 ke bentuk bytes
            file_content = hasil['data']
            data = base64.b64decode(file_content)
            download_dir = 'downloaded_files'
            os.makedirs(download_dir, exist_ok=True)

            file_path = os.path.join(download_dir, file_path)

            fp = open(file_path,'wb+')
            fp.write(data)
            fp.close()
            return True
        else:
            print("Gagal")
            return False    
    
    def remote_post(self, tokenid, chat_id, filepath):
        with open(filepath, 'rb') as fp:
            data = base64.b64encode(fp.read()).decode()
        command_str = f"sendfile {tokenid} {chat_id} {filepath} {data} \r\n"
        hasil = self.sendstring(command_str)
        if hasil['status'] == 'OK':
            return True
        else:
            print("Gagal")
            return False
        
    def logout(self):
        if (self.tokenid==""):
            return "Error, not authorized"
        string="logout {} \r\n" .format(self.tokenid)
        result = self.sendstring(string)
        if result["status"] == "OK":
            return "user logged out"
        else:
            return "Error, {}".format(result["message"])
        
    def getusername(self):
        if (self.tokenid==""):
            return "Error, not authorized"
        string="getusername {} \r\n" .format(self.tokenid)
        result = self.sendstring(string)
        if result["status"] == "OK":
            return "{}" . format(json.dumps(result['data']))
        else:
            return "Error, {}".format(result["message"])
        
    def inboxall(self):
        if (self.tokenid==""):
            return "Error, not authorized"
        string="inboxall {} \r\n" .format(self.tokenid)
        result = self.sendstring(string)
        if result["status"] == "OK":
            return "{}" . format(json.dumps(result['data']))
        else:
            return "Error, {}".format(result["message"])
        
    def inbox(self, chatid):
        if (self.tokenid==""):
            return "Error, not authorized"
        string="inbox {} {} \r\n" .format(self.tokenid, chatid)
        result = self.sendstring(string)
        if result["status"] == "OK":
            return "{}" . format(json.dumps(result['data']))
        else:
            return "Error, {}".format(result["message"])
        
    def getnewchat(self):
        if (self.tokenid==""):
            return "Error, not authorized"
        string="getNewChat {} \r\n" .format(self.tokenid)
        result = self.sendstring(string)
        if result["status"] == "OK":
            return "{}" . format(json.dumps(result['data']))
        else:
            return "Error, {}".format(result["message"])
        
    def createchat(self, username):
        if (self.tokenid==""):
            return "Error, not authorized"
        string="createChat {} private {} \r\n" .format(self.tokenid, username)
        result = self.sendstring(string)
        if result["status"] == "OK":
            return "{}" . format(json.dumps(result['data']))
        else:
            return "Error, {}".format(result["message"])

    def creategroup(self, groupname, password):
        if (self.tokenid==""):
            return "Error, not authorized"
        string="createGroup {} group {} {} \r\n" .format(self.tokenid, groupname, password)
        result = self.sendstring(string)
        if result["status"] == "OK":
            return "{}" . format(json.dumps(result['data']))
        else:
            return "Error, {}".format(result["message"])

    def joingroup(self, groupid, password):
        if (self.tokenid==""):
            return "Error, not authorized"
        string="joinGroup {} {} {} \r\n" .format(self.tokenid, groupid, password)
        result = self.sendstring(string)
        if result["status"] == "OK":
            return "joined group"
        else:
            return "Error, {}".format(result["message"])
        
    def sendmsg(self, chatid, message):
        if (self.tokenid==""):
            return "Error, not authorized"
        string="sendmsg {} {}{} \r\n" . format(self.tokenid,chatid,message)
        print(string)
        result = self.sendstring(string)
        if result['status']=='OK':
            return "message sent"
        else:
            return "Error, {}" . format(result['message'])
        
# cc = ChatClient()

if __name__=="__main__":
    cc = ChatClient()
    while True:
        cmdline = input("Command {}:" . format(cc.tokenid))
        print(cc.proses(cmdline))