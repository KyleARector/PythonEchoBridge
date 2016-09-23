import socket
import struct

address = "239.255.255.250"
port = 1900
 
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
sock.bind(('', port))
mreq = struct.pack("=4sl", socket.inet_aton(address), socket.INADDR_ANY)
 
sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)

msgSend = "HTTP/1.1 200 OK\r\n" + \
          "CACHE-CONTROL: max-age=100\r\n" + \
          "EXT:\r\n" + \
          "LOCATION: http://" + socket.gethostbyname(socket.gethostname()) + "/description.xml\r\n" + \
          "SERVER: FreeRTOS/6.0.5, UPnP/1.0, IpBridge/1.10.0\r\n" + \
          "ST: urn:schemas-upnp-org:device:basic:1\r\n" + \
          "USN: uuid:2fa00080-d000-11e1-9b23-001f80007bbe::upnp:rootdevice" 

while True:
    msgRecv, addressInfo = sock.recvfrom(10240)
    if "M-SEARCH" in msgRecv:
        sock.sendto(msgSend, addressInfo)
