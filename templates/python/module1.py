# import zmq
# import thread
# import time
#
# inport = 7570
# outport = 7770
#
# insub = "module1.in.input1"
# outsub = "module1.out.output1"
# hbsub = "module1.heart"
#
# c = zmq.Context()
#
# #module output
# outs = c.socket(zmq.PUB)
# outs.connect("tcp://localhost:%s" % str(outport))
#
# #module input
# ins = c.socket(zmq.SUB)
# ins.connect("tcp://localhost:%s" % str(inport))
# ins.setsockopt_string(zmq.SUBSCRIBE, insub.decode('ascii'))
#
# #heartbeat
# def heartbeat():
# 	hbs = c.socket(zmq.PUB)
# 	hbs.connect("tcp://localhost:%s" % str(outport))
# 	while True:
# 		hbs.send_string("%s|%s" % (hbsub, "Beat"))
# 		time.sleep(30)
#
# thread.start_new_thread( heartbeat, () )
#
# #main loop
# while True:
# 	message = ins.recv_string().split("|")
# 	if(len(message) > 2):
# 		#process message
# 		print message[2]
# 		outs.send_string("%s|%s|%s" % (outsub, "String",message[2]+" handled"))

import zmq
import random
import sys
import time

addr = "127.0.0.1"
port = "7770"
if len(sys.argv) > 1:
    port =  sys.argv[1]
    int(port)

context = zmq.Context()
socket = context.socket(zmq.PUB)
conn_str = "tcp://%s:%s" % (addr, port)
print "Binding to %s" % conn_str
socket.bind(conn_str)

import thread

# heartbeat
def heartbeat():
    while True:
        messagedata = "module1.heart|beat"
        socket.send_string(messagedata)
        time.sleep(1)

# msgloop
def msgloop():
    while True:
        messagedata = "module1.string|content string"
        socket.send_string(messagedata)
        time.sleep(1)

thread.start_new_thread(heartbeat, ())
thread.start_new_thread(msgloop, ())
#
#
while True:
    messagedata = "module1.some|string|useful data"
    socket.send("%s" % (messagedata))
    time.sleep(1)
