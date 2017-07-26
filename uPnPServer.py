import socket
import struct


# Create a parent class for UPnP Servers and Clients
class UPnPInterface(object):
    # Arguments include the address and port to listen for UPnP packets on
    def __init__(self, address, port):
        # Set up a socket
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM,
                                  socket.IPPROTO_UDP)
        # Set socket options
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        # Bind the socket to the port argument
        self.sock.bind(('', port))
        mreq = struct.pack("=4sl", socket.inet_aton(address),
                           socket.INADDR_ANY)

        self.sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)


# Create a derived class to serve UPnP packets upon search request
class UPnPServer(UPnPInterface):
    def __init__(self, address, port):
        # Initialize parent class
        UPnPInterface.__init__(self, address, port)
        # Format a response to broadcast as a Philips Hue Bridge
        # Would be nice to acquire IP from system
        local_ip = [l for l in ([ip for ip in socket.gethostbyname_ex(socket.gethostname())[2] if not ip.startswith("127.")][:1], [[(s.connect(('8.8.8.8', 53)), s.getsockname()[0], s.close()) for s in [socket.socket(socket.AF_INET, socket.SOCK_DGRAM)]][0][1]]) if l][0][0]
        self.response = "HTTP/1.1 200 OK\r\n" + \
                        "CACHE-CONTROL: max-age=100\r\n" + \
                        "EXT:\r\n" + \
                        "LOCATION: http://" + local_ip + ":8080" + \
                        "/static/description.xml\r\n" + \
                        "SERVER: Linux/3.14.0, UPnP/1.0, " + \
                        "IpBridge/1.13.0\r\n" + \
                        "hue-bridgeid: 001788FFFE222A8F\r\n" + \
                        "ST: urn:schemas-upnp-org:device:basic:1\r\n" + \
                        "USN: uuid:" + \
                        "2f402f80-da50-11e1-9b23-001788222a8f\r\n\r\n"

    # Receive message from port and return content and address
    def receive(self, port):
        message, return_address = self.sock.recvfrom(port)
        return {"message": message, "address": return_address}

    # Send message back to M-SEARCH initiator
    def respond(self, address):
        self.sock.sendto(self.response, address)


def main():
    # Instantiate a server
    upnp_serv = UPnPServer("239.255.255.250", 1900)
    while True:
        # Repeatedly receive data on specified port
        data = upnp_serv.receive(10240)
        # If packet is a search, send back response
        if "M-SEARCH" in data["message"]:
            upnp_serv.respond(data["address"])

if __name__ == "__main__":
    main()
