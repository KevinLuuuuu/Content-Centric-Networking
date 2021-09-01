# Real-Time-System


## Project 1 :

Goal : Network topology construction & Socket implementation  

Given an network topology and input with a JSON format and implement sockets for data transmission.  

## Project 2 :

Goal : Implement Content-Centric Networking (CCN) based on Project 1.  

According to process flow, construct a CCN simulator(interest.py、 data.py、 forward.py、 ps.py、 pit.py...) and creat tables.(Queue、 PS、 PIT)  

## Project 3 :

Goal : Optimize the CCN network based on project 2.  

Add cs.py, fib.py, CS table and FIB table to CCN.  
When the interest_queue or data_queue is full, update them according to FIFO, LRU, LFU, etc.  
When the CS is full, update them according to FIFO, LRU, LFU, Cost-based or Time-based, etc.  
Compare and find the best cache hit rate & average response time under different conditions.  
