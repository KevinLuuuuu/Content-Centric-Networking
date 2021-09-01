# -*- coding: UTF-8 -*-
# Author: Junbin Zhang
# E-mail: p78083025@ncku.edu.tw
# Update time: 2021.02.27

from __future__ import print_function

class NETWORK():
    def __init__(self):
        self.network = {}

    def Creat_network(self, network):
        self.network = network
        return self.network

    def Get_network(self, network):
        '''
        self.network = {'r0': [1,3],'r1': [0,2,3],'r2': [1,5],'r3': [0,1,4],'r4': [3,5,6],'r5': [2,4,7],'r6': [4,7,10],
             'r7': [5,6,8,9],'r8': [7],'r9': [7,11],'r10': [6,11],'r11': [9,10]}
        '''
        self.network = network
        return self.network