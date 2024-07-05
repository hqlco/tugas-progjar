import sys
import os
import json
import uuid
import logging
import socket
import threading
import base64
import json
from queue import Queue
from datetime import datetime
#rosy haqqy
class Chat:
	def __init__(self):
		self.realm_auth = "secret1"
		self.realm_ip = "172.16.16.101"
		self.sessions={}

		self.users = {}

		self.users['messi']={'password': 'secret', 'chats' : []}
		self.users['henderson']={'password': 'secret', 'chats': []}
		self.users['lineker']={'password': 'secret', 'chats': []}

		self.chats = {}



		self.file_storage_path = 'uploads'
		if not os.path.exists(self.file_storage_path):
			os.makedirs(self.file_storage_path)


		self.realms = {}

		self.realms["172.16.16.102"] = {
				"port": 8889,
				"users": [
					"hmd",
					"hfd",
					"hq"
				],
				"auth": "secret2"
			}
		

	def proses(self,data):
		j=data.split(" ")
		try:
			command=j[0].strip()
			if (command == 'login'):
				username=j[1].strip()
				password=j[2].strip()
				logging.warning("AUTH: login {} {}" . format(username, password))
				return self.autentikasi_user(username, password)

			elif (command == 'register'):
				username=j[1].strip()
				password=j[2].strip()
				logging.warning("REGISTER: register {} {}" . format(username, password))
				return self.register(username, password)

			elif (command == 'logout'):
				tokenid=j[1].strip()
				return self.logout(tokenid)

			elif (command == 'addUserRealm'):
				auth=j[1].strip()
				ipRealm=j[2].strip()
				username=j[3].strip()
				logging.warning("SYNC: addUserRealm {} {} {}" . format(auth, ipRealm, username))
				return self.add_user_realm(auth, ipRealm, username)
			
			elif (command == 'getusername'):
				tokenid=j[1].strip()
				logging.warning("GETUSERNAME: {}" . format(tokenid))
				return self.get_username(tokenid)
			
			elif (command == 'sendmsg'):
				tokenid=j[1].strip()
				chat_id=j[2].strip()
				message = " ".join(j[3:])
				message = message[:-3]
				logging.warning("SENDMSG: {}" . format(tokenid, chat_id, message))
				return self.send_message(tokenid, chat_id, message)
			
			elif (command == 'syncmsg'):
				auth=j[1].strip()
				ipRealm=j[2].strip()
				chat_id=j[3].strip()
				message = json.loads(' '.join(j[4:]).strip())
				logging.warning("SYNC: syncmsg {} {} {} {}" . format(auth, ipRealm, chat_id, message))
				return self.sync_message(auth, ipRealm, chat_id, message)
			
			elif(command == 'addRealmChat'):
				auth=j[1].strip()
				ipRealm=j[2].strip()
				chat_id = j[3].strip()
				username = j[4].strip()
				logging.warning("SYNC: addRealmChat {} {} {} {}" . format(auth, ipRealm, chat_id, username))
				return self.add_realm_chats(auth, ipRealm, chat_id, username)
			
			elif(command == 'changeSelfChat'):
				auth=j[1].strip()
				ipRealm=j[2].strip()
				chat_id = j[3].strip()
				chat_dict = json.loads(' '.join(j[4:]).strip())
				logging.warning("SYNC: changeSelfChat {} {} {} {}" . format(auth, ipRealm, chat_id, chat_dict))
				return self.change_self_chat(auth, ipRealm, chat_id, chat_dict)

			elif (command == 'createGroup'):
				tokenid = j[1].strip()
				type= j[2].strip()
				group_name = j[3].strip()
				password = j[4].strip()
				logging.warning("CREATE_GROUP: createGroup {} {} {}" . format(type, group_name, password))
				return self.create_chat(tokenid, type, group_name, password = password)
			
			elif(command == 'createChat'):
				tokenid = j[1].strip()
				type = j[2].strip()
				group_name = j[3].strip()
				member = j[3].strip()
				logging.warning("CREATE_CHAT: createChat {} {} {}" . format(type, group_name, member))
				return self.create_chat(tokenid, type, group_name, member = member)
			
			elif (command == 'inboxall'):
				tokenid=j[1].strip()
				logging.warning("INBOXALL: {}" . format(tokenid))
				return self.get_all_inbox(tokenid)
			
			elif (command == 'inbox'):
				tokenid=j[1].strip()
				chat_id=j[2].strip()
				logging.warning("INBOX: {} {}" . format(tokenid, chat_id))
				return self.get_inbox(tokenid, chat_id)

			elif (command == 'getNewChat'):
				tokenid=j[1].strip()
				logging.warning("GETNEWCHAT: {}" . format(tokenid))
				return self.get_new_chat(tokenid)
			
			elif (command == 'getNewChatRealm'):
				auth=j[1].strip()
				ipRealm=j[2].strip()
				username=j[3].strip()
				logging.warning("SYNC: getNewChatRealm {} {} {}" . format(auth, ipRealm, username))
				return self.get_new_chat_realm(auth, ipRealm, username)

			elif (command == 'addMember'):
				auth=j[1].strip()
				ipRealm=j[2].strip()
				chat_id = j[3].strip()
				username = j[4].strip()
				logging.warning("SYNC: addMember {} {} {} {}" . format(auth, ipRealm, chat_id, username))
				result = self.sync_self_chat(auth, ipRealm, chat_id, username)
				print(self.chats[chat_id])
				return result

			elif (command == 'joinGroup'):
				tokenid = j[1].strip()
				group_id = j[2].strip()
				password = j[3].strip()
				logging.warning("JOIN_GROUP: {} {} {}" . format(tokenid, group_id, password))
				result = self.join_group(tokenid, group_id, password)
				return result
			
			elif (command == 'sendfile'):
				tokenid=j[1].strip()
				chat_id=j[2].strip()
				filepath = j[3].strip()
				filecontent = ' '.join(j[4:]).strip()
				logging.warning("SENDFILE: {} {} {}" . format(tokenid, chat_id, filepath))
				return self.upload_file(tokenid, chat_id, filecontent, filepath)
			
			elif (command == 'syncfile'):
				auth=j[1].strip()
				ipRealm=j[2].strip()
				filepath=j[3].strip()
				filecontent = ' '.join(j[4:]).strip()
				logging.warning("SYNC: syncfile {} {} {} {}" . format(auth, ipRealm, filepath, filecontent))
				return self.sync_file(auth, ipRealm, filepath, filecontent)

			elif (command == 'getfile'):
				tokenid=j[1].strip()
				chat_id=j[2].strip()
				filepath = j[3].strip()
				logging.warning("getfile: {} {} {}" . format(tokenid, chat_id, filepath))
				return self.getfile(tokenid, chat_id, filepath)
			
			else:
				return {'status': 'ERROR', 'message': '**Protocol Tidak Benar'}
		except KeyError:
			return { 'status': 'ERROR', 'message' : 'Informasi tidak ditemukan'}
		except IndexError:
			return {'status': 'ERROR', 'message': '--Protocol Tidak Benar'}

	def sendstring(self, string, targetIp, targetPort):
		sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		server_address = (targetIp,targetPort)
		sock.connect(server_address)
		try:
			sock.sendall(string.encode())
			receivemsg = ""
			while True:
				data = sock.recv(1024)
				print("diterima dari server",data)
				if (data):
					receivemsg = "{}{}" . format(receivemsg,data.decode())  #data harus didecode agar dapat di operasikan dalam bentuk string
					if receivemsg[-4:]=='\r\n\r\n':
						print("end of string")
						sock.close()
						return json.loads(receivemsg)
		except:
			sock.close()
			return { 'status' : 'ERROR', 'message' : 'Gagal'}

	def check_user(self, username):
		if (username in self.users):
			return True
		for realm in self.realms:
			if username in self.realms[realm]['users']:
				return True
		return False

	def autentikasi_user(self, username, password):
		if (username not in self.users):
			return { 'status': 'ERROR', 'message': 'User Tidak Ada' }
		if (self.users[username]['password'] != password):
			return { 'status': 'ERROR', 'message': 'Password Salah' }
		tokenid = str(uuid.uuid4()) 
		self.sessions[tokenid] = { 'username': username, 'userdetail':self.users[username]}
		return { 'status': 'OK', 'tokenid': tokenid }

	def add_user_realm(self, auth, ipRealm, username):
		if self.realms[ipRealm]['auth'] != auth:
			return { 'status': 'ERROR', 'message': 'Autentikasi Realm Gagal' }
		self.realms[ipRealm]['users'].append(username)
		return { 'status': 'OK', 'message': f'Berhasil menambahkan {username} kedalam {ipRealm} pada realm {self.realm_ip}' }

	def register(self,username,password):
		if (self.check_user(username)):
			return { 'status': 'ERROR', 'message': 'User Sudah Ada' }
		self.users[username] = {"password": password, "chats": []}
		tokenid = str(uuid.uuid4()) 
		self.sessions[tokenid] = { 'username': username, 'userdetail': self.users[username]}
		
		# sync new users across realms
		for ipRealm in self.realms:
			string="addUserRealm {} {} {} \r\n" . format(self.realm_auth, self.realm_ip, username)
			result = self.sendstring(string, ipRealm, self.realms[ipRealm]['port'])
			if result['status']=='OK':
				continue
			else:
				return {'status': 'ERROR', 'message': result['message']}
				
		return { 'status': 'OK', 'tokenid': tokenid }
		
	def logout(self, tokenid):
		if tokenid not in self.sessions:
			return {'status': 'ERROR', 'message': 'User Belum Login'}
		del self.sessions[tokenid]
		return {'status': 'OK', 'message': 'User Berhasil Logout'}
	
	def get_username(self, tokenid):
		if tokenid not in self.sessions:
			return {'status': 'ERROR', 'message': 'User Belum Login'}
		return {'status': 'OK', 'data': self.sessions[tokenid]['username']}
	
	def add_realm_chats(self, auth, ipRealm, chat_id, username): # memasukkan chat_id kedalam parameter user
		if self.realms[ipRealm]['auth'] != auth:
			return { 'status': 'ERROR', 'message': 'Autentikasi Realm Gagal' }
		
		if chat_id not in self.chats:
			return {'status': 'ERROR', 'message': 'Chat tidak ditemukan'}

		self.users[username]['chats'].append(chat_id)
		# self.chats[chat_id]= chat_dict
		return { 'status': 'OK', 'message': f'Berhasil menambahkan chat {chat_id} kedalam {self.realm_ip} pada user {username}' }
	
	def change_self_chat(self, auth, ipRealm, chat_id, chat_dict):
		if self.realms[ipRealm]['auth'] != auth:
			return { 'status': 'ERROR', 'message': 'Autentikasi Realm Gagal' }

		self.chats[chat_id] = chat_dict
		return { 'status': 'OK', 'message': f'Berhasil mengubah chat chats dengan chat_id {chat_id} kedalam {self.realm_ip}' }

	def create_chat(self, tokenid, type, group_name, member = None, password = None):
		if tokenid not in self.sessions:
			return {'status': 'ERROR', 'message': 'User Belum Login'}
		members = []
		user = self.sessions[tokenid]
		username = user['username']
		members.append(username)
		if member is not None:
			if self.check_user(member) == False:
				return {'status': 'ERROR', 'message': 'User Tidak Ditemukan'}
			members.append(member)
		now = datetime.now()
		current_time = now.strftime("%Y-%m-%d %H:%M:%S")
		chat_id = str(uuid.uuid4()).replace('-', '')[:10]
		chat_dict = {
			'type': type,
			'name': group_name,
			'password': password,
			'message': [],
			'member': members,
			'updatedAt': current_time
		}
		self.chats[chat_id] = chat_dict
		user['userdetail']['chats'].append(chat_id)
		# melakukan broadcast chat group ke semua user
		chat_json = json.dumps(chat_dict)
		if type == 'group':
			for ip,val in self.realms.items():
				string="changeSelfChat {} {} {} {} \r\n" . format(self.realm_auth, self.realm_ip, chat_id, chat_json)
				self.sendstring(string, ip, self.realms[ip]['port'])
		else:
			for ip,val in self.realms.items():
				if member in val['users']:
					string="changeSelfChat {} {} {} {} \r\n" . format(self.realm_auth, self.realm_ip, chat_id, chat_json)
					self.sendstring(string, ip, self.realms[ip]['port'])

		# untuk member akan disambungkan ke realm yang bersangkutan
		if member is not None: # jika ada member
			if  member not in self.users.keys(): # jika member tidak dari realm ini
				for ip,val in self.realms.items(): # mencari di realm lain
					if member in val['users']:
						string="addRealmChat {} {} {} {} \r\n" . format(self.realm_auth, self.realm_ip, chat_id, member)
						result = self.sendstring(string, ip, self.realms[ip]['port'])
						if result['status']=='OK':
							continue
						else:
							return { 'status': 'ERROR', 'message': result['message'] }
			else:
				self.users[member]['chats'].append(chat_id)
		if type == 'private':
			for member in members:
				if member != username:
					chat_name = member
					break
		else:
			chat_name = group_name
		response = {
			'id': chat_id,
			'type': chat_dict["type"],
			'name': chat_name,
			'message': chat_dict["message"],
			'member': chat_dict["member"],
			'updatedAt': chat_dict["updatedAt"]
		}
		return { 'status': 'OK', 'message': f'Berhasil membuat chat', 'data': response}

	def sync_message(self, auth, ipRealm, chat_id, message):
		if self.realms[ipRealm]['auth'] != auth:
			return { 'status': 'ERROR', 'message': 'Autentikasi Realm Gagal' }
		
		if chat_id not in self.chats:
			return {'status': 'ERROR', 'message': 'Chat tidak ditemukan'}

		print(self.chats[chat_id])
		self.chats[chat_id]['message'].append(message)

		self.chats[chat_id]['updatedAt'] = message['timestamp']

		return {'status': 'OK', 'message': 'Pesan berhasil disinkronisasi'}

	def send_message(self, tokenid, chat_id, message):
		if tokenid not in self.sessions:
			return {'status': 'ERROR', 'message': 'User Belum Login'}
		users = self.sessions[tokenid]['userdetail']

		if chat_id not in users['chats']:
			return {'status': 'ERROR', 'message': 'Chat tidak ditemukan'}
		
		timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
		sender = self.sessions[tokenid]['username']

		message_dict = {
			'sender': sender,
			'message': message,
			'isFile': False,
			'timestamp': timestamp
		}

		self.chats[chat_id]['message'].append(message_dict)

		self.chats[chat_id]['updatedAt'] = timestamp

		# sync new message across realms
		message_json = json.dumps(message_dict)
		for ipRealm in self.realms:
			for member in self.chats[chat_id]['member']:
				if member in self.realms[ipRealm]['users']:
					string="syncmsg {} {} {} {} \r\n" . format(self.realm_auth, self.realm_ip, chat_id, message_json)
					result = self.sendstring(string, ipRealm, self.realms[ipRealm]['port'])
					if result['status']=='OK':
						break
					else:
						return {'status': 'ERROR', 'message': result['message']}

		return {'status': 'OK', 'message': 'Pesan berhasil dikirim'}

	def upload_file(self, tokenid, chat_id, file_content, file_path):
		if tokenid not in self.sessions:
			return {'status': 'ERROR', 'message': 'User not logged in'}
		
		users = self.sessions[tokenid]['userdetail']
		
		if chat_id not in users['chats']:
			return {'status': 'ERROR', 'message': 'Chat not found'}
		
		filename = os.path.basename(file_path)
		dest_path = os.path.join(self.file_storage_path, filename)
		
		timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
		sender = self.sessions[tokenid]['username']
		
		with open(dest_path, 'wb') as f_dest:
			f_dest.write(base64.b64decode(file_content))
					
		message = {
			'sender': sender,
			'message': filename,
			'isFile': True,
			'timestamp': timestamp
			}
		
		self.chats[chat_id]['message'].append(message)
		self.chats[chat_id]['updatedAt'] = message['timestamp']

		# sync new file across realms
		message_json = json.dumps(message)
		for ipRealm in self.realms:
			for member in self.chats[chat_id]['member']:
				if member in self.realms[ipRealm]['users']:
					string="syncmsg {} {} {} {} \r\n" . format(self.realm_auth, self.realm_ip, chat_id, message_json)
					result = self.sendstring(string, ipRealm, self.realms[ipRealm]['port'])
					if result['status']=='OK':
						string="syncfile {} {} {} {} \r\n" . format(self.realm_auth, self.realm_ip, file_path, file_content)
						result = self.sendstring(string, ipRealm, self.realms[ipRealm]['port'])
						if result['status']=='OK':
							break
						else:
							return {'status': 'ERROR', 'message': result['message']}
					else:
						return {'status': 'ERROR', 'message': result['message']}

		return {'status': 'OK', 'message': f"File {filename} uploaded successfully"}
	
	def sync_file(self, auth, ipRealm, file_path, file_content):
		if self.realms[ipRealm]['auth'] != auth:
			return { 'status': 'ERROR', 'message': 'Autentikasi Realm Gagal' }

		filename = os.path.basename(file_path)
		dest_path = os.path.join(self.file_storage_path, filename)
		
		with open(dest_path, 'wb') as f_dest:
			f_dest.write(base64.b64decode(file_content))
		
		return {'status': 'OK', 'message': f"File {filename} uploaded successfully"}

	def getfile(self, tokenid, chat_id, file_path):
		if tokenid not in self.sessions:
			return {'status': 'ERROR', 'message': 'User not logged in'}
		
		users = self.sessions[tokenid]['userdetail']
		
		if chat_id not in users['chats']:
			return {'status': 'ERROR', 'message': 'Chat not found'}
		
		filename = os.path.basename(file_path)
		src_path = os.path.join(self.file_storage_path, filename)
		
		if not os.path.exists(src_path):
			return {'status': 'ERROR', 'message': 'File not found'}
		
		with open(src_path, 'rb') as f_src:
			file_content = base64.b64encode(f_src.read()).decode()
		
		return {'status': 'OK', 'data': file_content}
		
	def get_all_inbox(self, tokenid):
		if tokenid not in self.sessions:
			return {'status': 'ERROR', 'message': 'User Belum Login'}
		users = self.sessions[tokenid]['userdetail']
		inbox = []
		for chat_id in users['chats']:
			if self.chats[chat_id]['type'] == 'private':
				for member in self.chats[chat_id]['member']:
					if member != self.sessions[tokenid]['username']:
						chat_name = member
						break
			else:
				chat_name = self.chats[chat_id]['name']
			if self.chats[chat_id]['message'] != []:
				message = self.chats[chat_id]['message'][-1]
			else:
				message = []
			inbox.append({
				"id": chat_id,
				"type": self.chats[chat_id]['type'],
				"name": chat_name,
				"message": message,
				"member": self.chats[chat_id]['member'],
				"updatedAt": self.chats[chat_id]['updatedAt']
			})
		return {'status': 'OK', 'data': inbox}	
	
	def get_inbox(self, tokenid, chat_id):
		if tokenid not in self.sessions:
			return {'status': 'ERROR', 'message': 'User Belum Login'}
		users = self.sessions[tokenid]['userdetail']

		if chat_id not in users['chats']:
			return {'status': 'ERROR', 'message': 'Chat tidak ditemukan'}
		
		if self.chats[chat_id]['type'] == 'private':
			for member in self.chats[chat_id]['member']:
				if member != self.sessions[tokenid]['username']:
					chat_name = member
					break
		else:
			chat_name = self.chats[chat_id]['name']
		inbox = {
			"id": chat_id,
			"type": self.chats[chat_id]['type'],
			"name": chat_name,
			"message": self.chats[chat_id]['message'],
			"member": self.chats[chat_id]['member'],
			"updatedAt": self.chats[chat_id]['updatedAt']
		}
		return {'status': 'OK', 'data': inbox}
	
	def get_new_chat(self, tokenid):
		if tokenid not in self.sessions:
			return {'status': 'ERROR', 'message': 'User Belum Login'}
		username = self.sessions[tokenid]['username']

		data = []
		for user in self.users:
			found = False
			if user == username:
				continue
			for chat in self.chats:
				if self.chats[chat]['type'] == 'private':
					if username in self.chats[chat]['member'] and user in self.chats[chat]['member']:
						found = True
						break
			if not found:
				data.append({
					'type': 'private',
					'id': user,
					'name': user
				})
		
		for ipRealm in self.realms:
			string="getNewChatRealm {} {} {} \r\n" . format(self.realm_auth, self.realm_ip, username)
			result = self.sendstring(string, ipRealm, self.realms[ipRealm]['port'])
			if result['status']=='OK':
				data = data + result['data']
			else:
				return "Error, {}" . format(result['message'])

		for chat in self.chats:
			if self.chats[chat]['type'] == 'group':
				if username not in self.chats[chat]['member']:
					data.append({
					'type': 'group',
					'id': chat,
					'name': self.chats[chat]['name']
				})
		
		return {'status': 'OK', 'data': data}
	
	def get_new_chat_realm(self, auth, ipRealm, username):
		if self.realms[ipRealm]['auth'] != auth:
			return { 'status': 'ERROR', 'message': 'Autentikasi Realm Gagal' }

		data = []
		for user in self.users:
			found = False
			if user == username:
				continue
			for chat in self.chats:
				if self.chats[chat]['type'] == 'private':
					if username in self.chats[chat]['member'] and user in self.chats[chat]['member']:
						found = True
						break
			if not found:
				data.append({
					'type': 'private',
					'id': user,
					'name': user
				})
		
		return {'status': 'OK', 'data': data}
	
	def sync_self_chat(self, auth, ipRealm, chat_id, username):
		if self.realms[ipRealm]['auth'] != auth:
			return { 'status': 'ERROR', 'message': 'Autentikasi Realm Gagal' }
		
		if chat_id not in self.chats:
			return {'status': 'ERROR', 'message': 'Chat tidak ditemukan'}

		self.chats[chat_id]['member'].append(username)
		return {'status': 'OK', 'message': 'Berhasil menambahkan user {} ke dalam chat {}' . format(chat_id,self.chats[chat_id]['name'])}
	# joingroup <token> <groupname> <password>
	def join_group(self, tokenid, chat_id, password):
		if tokenid not in self.sessions:	
			return {'status': 'ERROR', 'message': 'User Belum Login'}
		users = self.sessions[tokenid]['userdetail']
		username = self.sessions[tokenid]['username']
		if chat_id not in self.chats:
			return {'status': 'ERROR', 'message': 'Chat tidak ditemukan'}
		if self.chats[chat_id] ['type'] != 'group':
			return {'status': 'ERROR', 'message': 'Chat tidak ditemukan (bukan grpoup)'}
		if password == self.chats[chat_id]['password']:
			if username in self.chats[chat_id]['member']:
				return {'status': 'ERROR', 'message': 'Anda sudah menjadi member group {}' . format(self.chats[chat_id]['name'])}
			else:
				users['chats'].append(chat_id)
				self.chats[chat_id]['member'].append(username)
				for ip,val in self.realms.items():#menambahkan member kedalam chats dimasing masing realm
					string = 'addMember {} {} {} {} \r\n' . format(self.realm_auth, self.realm_ip, chat_id, username)
					self.sendstring(string, ip, self.realms[ip]['port'])
				return {'status': 'OK', 'message': 'Berhasil masuk kedalam group {}' . format(self.chats[chat_id]['name'])}
		return {'status': 'ERROR', 'message': 'Password Tidak Sesuai'}

if __name__=="__main__":
	j = Chat()
