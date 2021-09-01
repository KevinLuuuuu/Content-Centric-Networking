from enum import Flag

import threading, queue
import time
import socket
import json

from network import NETWORK
from interest import INTEREST
from data import DATA
from ps import PS
from cs import CS
from pit import PIT
from fib import FIB

result_save = {"cache_hit_cs":0,"cache_miss_cs":0,"response_time":0.0,"send_interest":0}

threadLock = threading.Lock()

class Server(threading.Thread):
    def __init__(self, serverID, sizes, producer_contents, run_start_time, network, HOST='127.0.0.1'):
        threading.Thread.__init__(self)
        self.HOST = HOST
        self.PORT= 8000 + serverID
        self.id = serverID      # number
        self.sizes = sizes      # sizes = [queue_size, cache_size, fib_size]
        self.queue_size, _, _ = sizes
        self.interest_queue = queue.Queue(self.queue_size)    # queue.Queue()
        self.data_queue = queue.Queue(self.queue_size)        # queue.Queue()
        self.Last_time = run_start_time
        self.step = 0
        self.result_save = result_save
        self.threadLock = threadLock

        # Create class instance
        Network = NETWORK()
        Pit = PIT()
        Ps = PS()
        Cs = CS()
        Fib = FIB()
        Interest = INTEREST()
        Data = DATA()
        # Create a network link table
        self.network = Network.Creat_network(network)
        # Create pit table
        self.pit = {}   #Pit.Creat_pit(route_ID=self.id)
        #######################################################
        # Get the producer contents of the current router
        # producer_content = producer_contents['r'+str(self.id)]
        # Create a producer content store table
        # self.ps = Ps.Creat_ps(route_ID=self.id, route_num=12, content_num=100, producer_content=producer_content)
        #######################################################
        # Create a producer content store table
        self.ps = producer_contents['r'+str(self.id)]
        # Create router CS table
        self.cs = []    #Cs.Creat_cs(route_ID=self.id)
        # Create router FIB table
        self.fib = {} #Fib.Creat_FIB(route_ID=self.id)
        self.Tables = [self.network, self.ps, self.cs, self.pit, self.fib]
        self.interest_table = []

    # Create thread
    def run(self):
        threading.Thread(target = self.accept, daemon=True).start()
        threading.Thread(target = self.interest_process, daemon=True).start()
        threading.Thread(target = self.data_process, daemon=True).start()

    # Each router sends a fixed number of new interest packets to the network every second
    def start_network(self, run_start_time, frequency, content_num, route_num, interests):
        Interest = INTEREST()
        interest = interests['r' + str(self.id)]
        while True:
            if time.process_time() - self.Last_time > 1:
                self.Last_time = time.process_time()
                start_packets = Interest.Generate_interest(route_ID=self.id, run_start_time=run_start_time,
                                                           interest=interest[frequency*self.step : frequency*self.step+frequency],
                                                           result_save=self.result_save,threadLock=self.threadLock)
                self.step += 1
                for i in range(0, len(start_packets)):
                    if self.interest_queue.qsize() > self.queue_size:   # self.interest_queue.full():
                        break
                    else:
                        self.interest_queue.put(start_packets[i])
                break
        # time.sleep(1)

    # Receive packet
    def accept(self):
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server.bind((self.HOST, self.PORT))
        server.listen(10)
                
        while True:
            conn, addr = server.accept()
            packet = conn.recv(1024)
            packet = json.loads(packet)
            # packet = [interest] or [data]
            if packet['type'] == 'interest': # Interest packet received
                Interest = INTEREST()
                if Interest.Time_out(packet,self.result_save,self.threadLock) == True:
                    if self.interest_queue.qsize() < self.queue_size:
                        self.interest_queue.put(packet)
                    else:
                        index_dict = {}
                        index = 0
                        ##############################################
                        # optimization
                        # FIFO
                        
                        temp = self.interest_queue.get()
                        self.interest_queue.put(packet)

                        # LRU
                        '''
                        for i in range(len(self.interest_queue.queue)):
                            content_name = self.interest_queue.queue[i]['content_name']
                            if not content_name in index_dict:
                                index_dict[content_name] = [self.interest_queue.queue[i], index]
                            else:
                                index_dict[content_name][1] = index
                            index = index + 1
                        index_dict = dict(sorted(index_dict.items(), key=lambda item: item[1][1])) # sorted index
                        for key, value in index_dict.items():
                            self.interest_queue.queue.remove(value[0]) # delete LRU
                            break
                        # self.interest_queue.queue.remove(index_dict[0][0]) # delete LRU
                        '''
                        # LFU
                        '''
                        for i in range(len(self.interest_queue.queue)):
                            content_name = self.interest_queue.queue[i]['content_name']
                            if not content_name in index_dict:
                                index_dict[content_name] = [self.interest_queue.queue[i], 1]
                            else:
                                index_dict[content_name][1] += 1
                        index_dict = dict(sorted(index_dict.items(), key=lambda item: item[1][1])) # sorted index
                        for key, value in index_dict.items():
                            self.interest_queue.queue.remove(value[0]) # delete LFU
                            break
                        '''
                        ##############################################
                else:
                    pass
            elif packet['type'] == 'data': # Data packet received'
                if self.data_queue.qsize() < self.queue_size:
                    self.data_queue.put(packet)
                else:
                    index_dict = {}
                    index = 0
                    ##############################################
                    # optimization
                    # FIFO
                    
                    temp = self.data_queue.get()
                    self.data_queue.put(packet)
                    
                    # LRU
                    '''
                    for i in range(len(self.data_queue.queue)):
                        content_name = self.data_queue.queue[i]['content_name']
                        if not content_name in index_dict:
                            index_dict[content_name] = [self.data_queue.queue[i], index]
                        else:
                            index_dict[content_name][1] = index
                        index = index + 1
                    index_dict = dict(sorted(index_dict.items(), key=lambda item: item[1][1])) # sorted index
                    for key, value in index_dict.items():
                        self.data_queue.queue.remove(value[0]) # delete LRU
                        break
                    # self.data_queue.queue.remove(index_dict[0][0]) # delete LRU
                    '''
                    # LFU
                    '''
                    for i in range(len(self.data_queue.queue)):
                        content_name = self.data_queue.queue[i]['content_name']
                        if not content_name in index_dict:
                            index_dict[content_name] = [self.data_queue.queue[i], 1]
                        else:
                            index_dict[content_name][1] += 1
                    index_dict = dict(sorted(index_dict.items(), key=lambda item: item[1][1])) # sorted index
                    for key, value in index_dict.items():
                        self.data_queue.queue.remove(value[0]) # delete LFU
                        break
                    '''
                    ##############################################

    # process interest
    def interest_process(self):
        while self.interest_queue.empty is not True:
            interest = self.interest_queue.get()
            Interest = INTEREST()
            packet = Interest.On_interest(route_ID=self.id, interest=interest, tables=self.Tables, sizes=self.sizes,
                                          result_save=self.result_save,threadLock=self.threadLock)
            if len(packet)>0:
                if packet[0][1]['type'] == 'data':  # send Datas packet
                    for i in range(len(packet)):
                        #time.sleep(1)
                        send_data = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                        send_data.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                        send_data.connect((self.HOST, 8000 + packet[i][0]))
                        send_data.sendall(bytes(json.dumps(packet[i][1]), encoding='utf-8'))
                elif packet[0][1]['type'] == 'interest':  # send Interests packet
                    for i in range(len(packet)):
                        #time.sleep(1)
                        send_interest = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                        send_interest.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                        send_interest.connect((self.HOST, 8000 + packet[i][0]))
                        send_interest.sendall(bytes(json.dumps(packet[i][1]), encoding='utf-8'))
            pass    # Drop interest

    # process data
    def data_process(self):
        while self.data_queue.empty is not True:
            data = self.data_queue.get()
            Data = DATA()
            packet = Data.On_data(sizes=self.sizes, route_ID=self.id, data=data, tables=self.Tables,
                                  result_save=self.result_save,threadLock=self.threadLock)
            if len(packet)>0:
                if packet[0][1]['type'] == 'data':     # send Datas packet
                    for i in range(len(packet)):
                        #time.sleep(1)
                        send_data = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                        send_data.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                        send_data.connect((self.HOST, 8000 + packet[i][0]))
                        send_data.sendall(bytes(json.dumps(packet[i][1]), encoding='utf-8'))
            pass    # Drop data
