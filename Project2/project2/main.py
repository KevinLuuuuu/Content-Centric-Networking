from os import pipe
from server import Server
import json
import threading
import time
import csv

def main():
    fieldnames = ['Time', 'Type', 'Consumer_ID', 'Route_ID', 'Content_name', 'Data_hop', 'Path', 'Result', 'Hit_consumer', 'Hit_PIT', 'Hit_Miss']
    file = open('output_data.csv', 'w', newline='')
    writer = csv.DictWriter(file, fieldnames=fieldnames)
    writer.writeheader()
    file.close()

    fieldnames = ['Time', 'Type', 'Interest_ID', 'Consumer_ID', 'Route_ID', 'Content_name', 'Interest_hop', 'Path', 'Result', 'Hit', 'Miss']
    file = open('output_interest.csv', 'w', newline='')
    writer = csv.DictWriter(file, fieldnames=fieldnames)
    writer.writeheader()
    file.close()

    server_list = []
    # read file
    network_file = open('input_data/network.json', 'r')
    parameter_file = open('input_data/peremiters.json', 'r')
    pro_content_file = open('input_data/producer_contents.json', 'r')
    interest_file = open('input_data/interests.json', 'r')

    # parse file
    network = json.load(network_file)
    parameters = json.load(parameter_file)
    produce_content = json.load(pro_content_file)
    interests = json.load(interest_file)
    lock = threading.Lock()
    
    start = time.time()
    # run network
    for i in range(len(network)):
        server = Server(i, produce_content["r"+str(i)], start, network["r"+str(i)], lock)
        server.start()
        server_list.append(server)

    #while True:
    finish_time = start+20
    content_num = 0
    while time.time() <= finish_time:
        for j in server_list:
            j.start_network(start, parameters['frequency'], content_num, parameters['route_num'], interests["r"+str(j.id)])
        content_num += 1
        print(content_num)
        time.sleep(1)

if __name__ == '__main__':
    main()