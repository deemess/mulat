import zmq

def main():
    context = zmq.Context()
    pubs = context.socket(zmq.PUB)
    pubs.bind("tcp://*:7570")
    subs = context.socket(zmq.SUB)
    subs.bind("tcp://*:7770")
    subs.setsockopt_string(zmq.SUBSCRIBE, "".decode('ascii'))
    
    while True:
        message = subs.recv_string()
        print message
        pubs.send_string(message)
    
    pass

if __name__ == '__main__':
    main()