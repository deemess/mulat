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
pub_port = "7770"
sub_port = "7570"

if len(sys.argv) > 1:
    pub_port =  sys.argv[1]
    int(pub_port)

context = zmq.Context()
pub_socket = context.socket(zmq.PUB)
pub_conn_str = "tcp://%s:%s" % (addr, pub_port)
print "Connecting module PUB to %s" % pub_conn_str
pub_socket.connect(pub_conn_str)

sub_socket = context.socket(zmq.SUB)
sub_conn_str = "tcp://%s:%s" % (addr, sub_port)
print "Connecting module SUB to %s" % sub_conn_str
sub_socket.connect(sub_conn_str)
sub_socket.setsockopt_string(zmq.SUBSCRIBE, u"")

poller = zmq.Poller()

import thread

# heartbeat
def heartbeat():
    while True:
        messagedata = "module1.heart|beat"
        pub_socket.send_string(messagedata)
        time.sleep(1)


# msgloop
def msgloop():
    while True:
        messagedata = "module1.in.slot1|string|content string"
        pub_socket.send_string(messagedata)
        time.sleep(1)


# rcvloop
def rcvloop():
    print("Registering sockets")
    poller.register(sub_socket, zmq.POLLIN)
    socks = dict(poller.poll())

    while True:
        if sub_socket in socks and socks[sub_socket] == zmq.POLLIN:
            message = sub_socket.recv()
            print "Module received", message


thread.start_new_thread(heartbeat, ())
thread.start_new_thread(msgloop, ())
thread.start_new_thread(rcvloop, ())
#
#



while True:
    # messagedata = "module1.some|string|useful data"
    # sub_socket.send("%s" % (messagedata))
    time.sleep(1)


