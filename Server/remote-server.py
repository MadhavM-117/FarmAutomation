from time import sleep
import socket
from threading import Thread
import json
server_socket = socket.socket()
server_socket_port = 3213
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server_socket.bind(("",3213))
server_socket.listen(10)
clients = []

class ClientHandler(Thread):
    def __init__(self,client,addr):
        print "New Connection from ",addr
        super(ClientHandler,self).__init__()
        self.client = client
        self.addr = addr
        self.setDaemon(True)
    def run(self):
        while True:
            try:
                data = self.client.recv(1000)
            except socket.error as err:
                print err
                clients.remove(self)
                break
            if not data:
                print "Closing connection with client",self.addr
                break
            try:
                json_data = json.loads(data)
                print json_data
                write_back = False
                control_status =  json.load(open("controls.json","r"))
                if "control-pump-main-tank" in json_data:
                    control_status["control-pump-main-tank"]=json_data["control-pump-main-tank"]
                    write_back = True

                if "control-blower" in json_data:
                    control_status["control-blower"]=json_data["control-blower"]
                    write_back = True


                if "control-valve-raft-tank-1" in json_data:
                    control_status["control-valve-raft-tank-1"]=json_data["control-valve-raft-tank-1"]
                    write_back = True

                if "control-valve-raft-tank-2" in json_data:
                    control_status["control-valve-raft-tank-2"]=json_data["control-valve-raft-tank-2"]
                    write_back = True

                if write_back:
                    with open("controls.json","w") as fp:
                        json.dump(control_status,fp,indent = 4)

            except err :
                print err
                continue


    def send_data(self,data):
        data_string = json.dumps(data)
        self.client.send(data_string)

class ServerHandler(Thread):
    def __init__(self,):
        super(ServerHandler,self).__init__()
        self.setDaemon(True)
    def run(self):
        while True:
            client,client_addr = server_socket.accept()
            clients_handler = ClientHandler(client,client_addr)
            clients.append(clients_handler)
            clients_handler.start()
server = ServerHandler()
server.start()
while True:
    try:
        sensor_status = json.load(open("sensors.json","r"))
        control_status =  json.load(open("controls.json","r"))
	configuration = json.load(open("configuration.json","r"))
        # print "On Server ",sensor_status
        # print "On Server ",control_status
        all_data = sensor_status.copy()
        all_data.update(control_status)
	all_data["alert-message"]=configuration["alert-message"]
        for client in clients:
            try:
                client.send_data(all_data)
            except:
                clients.remove(client)
    except Exception as e:
        print e
    sleep(1)
