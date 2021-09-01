from os import truncate
import threading
import json
import socket
import queue
from time import sleep
import time
from ps import PS
from pit import PIT
from interest import INTEREST
from data import DATA

class Server(threading.Thread):
    def __init__(self, serverID, producer_contents, run_start_time, network, lock, HOST='127.0.0.1'):
        threading.Thread.__init__(self)
        self.HOST = HOST
        self.PORT= 8000 + serverID
        self.id = serverID
        self.network = network
        
        self.ps = PS()
        self.ps.Creat_ps(self.id, self.id, self.id, producer_contents)

        self.pit = PIT()

        self.interest_queue = queue.Queue()
        self.data_queue = queue.Queue()
        
        self.lock = lock
        
    def run(self):
        threading.Thread(target=self.accept).start()
        threading.Thread(target=self.interest_process).start()
        threading.Thread(target=self.data_process).start()

    def start_network(self, run_start_time, fre, content_num, route_num, interests):
        interests_packet = INTEREST()
        interests_packet.Generate_interest(self.id, run_start_time, fre, content_num, route_num, interests)

        network_list = self.network[:]
        self.pit.Creat_pit_entry(interests_packet.interest)
        for i in network_list:
            INTEREST.Send_interest(self, self.pit.pit, i, self.id, interests_packet.interest)
            INTEREST.Output_interests_txt(self, interests_packet.interest, 0, 'Miss in PS', 0, 1)

    def accept(self):
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.bind((self.HOST, self.PORT))
        server.listen(10)
        while True:
            conn, addr = server.accept()
            packet = conn.recv(1024)
            packet = json.loads(packet)
            if type(packet) == dict and packet['type']=="interest" and self.interest_queue.qsize() < 1000:
                self.interest_queue.put(packet)
            elif type(packet) == list and packet[1]['type']=="data" and self.data_queue.qsize() < 1000:
                self.data_queue.put(packet)
            else:
                continue

    def interest_process(self):
        while True:
            sleep(0.1)
            while not self.interest_queue.empty():
                interest_packet = self.interest_queue.get()
                if INTEREST.Time_out(self, interest_packet):
                    INTEREST.Output_interests_txt(self, interest_packet, 0, 'Time out', 0, 1)
                    continue
                data_packet = DATA()
                if PS.Search_ps_interest(self, self.ps.ps, interest_packet['content_name']):
                    data_packet.Creat_data(self.id, interest_packet)
                    INTEREST.Output_interests_txt(self, interest_packet, 0, 'Interest hit in PS', 1, 0)
                    DATA.Send_data(self, interest_packet['route_ID'], self.id, data_packet.data_packet)
                elif PIT.Search_pit_interest(self, self.pit.pit, interest_packet):
                    INTEREST.Output_interests_txt(self, interest_packet, 0, 'Miss in PS', 0, 1)
                    self.pit.Merge_pit_entry(interest_packet)
                else:
                    INTEREST.Output_interests_txt(self, interest_packet, 0, 'Miss in PS', 0, 1)
                    self.pit.Creat_pit_entry(interest_packet)
                    network_list = self.network[:]
                    for i in network_list:
                        if i != interest_packet['route_ID']:
                            INTEREST.Send_interest(self, self.pit.pit, i, self.id, interest_packet)

    def data_process(self):
         while True:
            sleep(0.2)
            while not self.data_queue.empty():
                data_packet = self.data_queue.get()
                if not PIT.Search_pit_data(self, self.pit.pit, data_packet[1]):
                    DATA.Output_data_txt(self, data_packet[1], 0, 'Data miss in PIT', 0, 0, 1)
                else:
                    DATA.Output_data_txt(self, data_packet[1], 0, 'Data hit in PIT', 0, 1, 0)
                    pit_entry = self.pit.Get_pit_entry(data_packet[1]['content_name'])
                    if self.id == data_packet[1]['consumer_ID']:
                        DATA.Output_data_txt(self, data_packet[1], 0, 'Data hit in consumer', 1, 0, 0)
                    else:
                        for i in pit_entry[0]:
                            if i != data_packet[0]:
                               DATA.Send_data(self, i, self.id, data_packet)
                    self.pit.Remove_pit_entry(0, data_packet[1])