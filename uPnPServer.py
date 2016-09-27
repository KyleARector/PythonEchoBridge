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
          "LOCATION: http://" + "ad.dr.e.ss:8080" + "/static/description.xml\r\n" + \
          "SERVER: Linux/3.14.0, UPnP/1.0, IpBridge/1.13.0\r\n" + \
          "hue-bridgeid: 001788FFFE222A8F\r\n" + \
          "ST: urn:schemas-upnp-org:device:basic:1\r\n" + \
          "USN: uuid:2f402f80-da50-11e1-9b23-001788222a8f\r\n\r\n" 

while True:
    msgRecv, addressInfo = sock.recvfrom(10240)
    if "M-SEARCH" in msgRecv:
        sock.sendto(msgSend, addressInfo)
