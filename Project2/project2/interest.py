import time
import csv
import socket
import json
from pit import PIT

class INTEREST():
    def __init__(self):
        self.interest = {}

    def Generate_interest(self, route_ID, run_start_time, fre, content_num, route_num, interest):
        self.interest['type'] = "interest"
        self.interest['interest_ID'] = interest[content_num]['interest_ID']
        self.interest['consumer_ID'] = route_ID                     #??????
        self.interest['route_ID'] = route_ID
        self.interest['content_name'] = interest[content_num]['content_name']
        self.interest['interest_hop'] = 0    #??????
        self.interest['life_hop'] = 5        #??????
        self.interest['run_start_time'] = run_start_time
        self.interest['path'] = "p" + str(route_ID)

    def Time_out(self, interest):
        if interest['interest_hop'] > interest['life_hop']:
            return True

    def Send_interest(self, pit, Outfaces, route_ID, interest):
        new_interest = INTEREST()
        new_interest.interest['type'] = "interest"
        new_interest.interest['interest_ID'] = interest['interest_ID']
        new_interest.interest['consumer_ID'] = interest['consumer_ID']
        new_interest.interest['route_ID'] = route_ID
        new_interest.interest['content_name'] = interest['content_name']
        new_interest.interest['interest_hop'] = interest['interest_hop'] + 1
        new_interest.interest['life_hop'] = 5
        new_interest.interest['run_start_time'] = interest['run_start_time']
        new_interest.interest['path'] = interest['path'] + "/" + str(route_ID)

        PIT.Update_pit_outface(self, pit, Outfaces, new_interest.interest)

        send_data = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        send_data.connect(('127.0.0.1', 8000 + Outfaces))
        send_data.sendall(bytes(json.dumps(new_interest.interest), encoding='utf-8'))
    
    def Output_interests_txt(self, interest, times, result, hit, miss):
        fieldnames = ['Time', 'Type', 'Interest_ID', 'Consumer_ID', 'Route_ID', 'Content_name', 'Interest_hop', 'Path', 'Result', 'Hit', 'Miss']
        write_dic = { 
                        'Time' : str( int( time.time() - interest['run_start_time']) ),
                        'Type' : interest['type'],
                        'Interest_ID' : 'I' + str(interest['interest_ID']),
                        'Consumer_ID' : 'C' + str(interest['consumer_ID']),
                        'Route_ID' : 'R' + str(interest['route_ID']),
                        'Content_name' : interest['content_name'],
                        'Interest_hop' : interest['interest_hop'],
                        'Path' : interest['path'],
                        'Result' : result,
                        'Hit' : hit,
                        'Miss' : miss,
                    }
        file = open('output_interest.csv', 'a', newline='')
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writerow(write_dic)
        file.close()