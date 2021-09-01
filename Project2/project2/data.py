from io import RawIOBase
import time
import csv
import socket
import json

class DATA():
    def __init__(self):
        self.data_packet = []

    def Creat_data(self, route_ID, interest):
        self.data_packet.append(route_ID)
        dic = { 
                'type' : 'data',
                'consumer_ID' : interest['consumer_ID'],
                'route_ID' : route_ID,
                'content_name' : interest['content_name'],
                'content_data' : interest['content_name'] + str(time.time()),
                'data_hop' : 0,
                'run_start_time' : interest['run_start_time'],
                'path' : "p",
              }
        self.data_packet.append(dic)

    def Send_data(self, Infaces, route_ID, data):
        new_data = DATA()
        new_data.data_packet.append(route_ID)
        new_data.data_packet.append({})
        new_data.data_packet[1]['type'] = "data"
        new_data.data_packet[1]['consumer_ID'] = data[1]['consumer_ID']
        new_data.data_packet[1]['route_ID'] = route_ID
        new_data.data_packet[1]['content_name'] = data[1]['content_name']
        new_data.data_packet[1]['content_data'] = data[1]['content_name'] + str(time.time())
        new_data.data_packet[1]['data_hop'] = data[1]['data_hop'] + 1
        new_data.data_packet[1]['run_start_time'] = data[1]['run_start_time']
        new_data.data_packet[1]['path'] = data[1]['path'] + str(route_ID) + "/"

        send_data = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        send_data.connect(('127.0.0.1', 8000 + Infaces))
        send_data.sendall(bytes(json.dumps(new_data.data_packet), encoding='utf-8'))
        
    def Output_data_txt(self, data, times, result, hit_consumer, hit_PIT, miss_PIT):
        fieldnames = ['Time', 'Type', 'Consumer_ID', 'Route_ID', 'Content_name', 'Data_hop', 'Path', 'Result', 'Hit_consumer', 'Hit_PIT', 'Hit_Miss']
        write_dic = { 
                        'Time' : str( int( time.time() - data['run_start_time']) ),
                        'Type' : data['type'],
                        'Consumer_ID' : 'C' + str(data['consumer_ID']),
                        'Route_ID' : 'R' + str(data['route_ID']),
                        'Content_name' : data['content_name'],
                        'Data_hop' : data['data_hop'],
                        'Path' : data['path'],
                        'Result' : result,
                        'Hit_consumer' : hit_consumer,
                        'Hit_PIT' : hit_PIT,
                        'Hit_Miss' : miss_PIT,
                    }
        file = open('output_data.csv', 'a', newline='')
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writerow(write_dic)
        file.close()