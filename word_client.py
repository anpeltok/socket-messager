import socket
import sys
import struct
import string
import random

# Iterate through string and key, return xorred string 
def xor(string1,string2):
  return "".join([chr(ord(char1) ^ ord(char2)) for (char1,char2) in zip(string1,string2)])

# Gets message and remaining length in parameter, packs the data and sends it
def pack_and_send(message, remain):
  ack = True
  eom = False
  rem = remain
  length = len(message)
  data = struct.pack('!8s??HH64s',cid, ack, eom, rem, length, message)
  sock.sendto(data, (server, uport))

# Unpacks message and returns end of message flag
def check_eom(data):
  s_cid, s_ack, s_eom, s_rem, s_length, s_msg = struct.unpack('!8s??HH64s', data)
  return s_eom

# Unpacks message and returns remaining length
def check_rem(data):
  s_cid, s_ack, s_eom, s_rem, s_length, s_msg = struct.unpack('!8s??HH64s', data)
  return s_rem
  
# Unpacks message and returns the actual contents
def unpack(data):
  s_cid, s_ack, s_eom, s_rem, s_length, s_msg = struct.unpack('!8s??HH64s', data)
  
  # Clears empty bytes from end of message
  for i in range (0, 64-s_length):
    s_msg = s_msg[:-1]
  return s_msg

# Gets message in parameter, returns it reversed
def reverse(message):
  words = s_msg.split(" ")
  msg = " ".join(reversed(words))
  return msg

# Split message into list of parts and return list
def pieces(message, length=64):
  return [message[i: i + 64] for i in range(0,len(message),64)]

# TCP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Get server and port as input
print
server = raw_input("Input server: ")
print
port = int(raw_input("Input port: "))

server_address = (server, port)

# Connect to socket
print
sock.connect(server_address)

# Send TCP message
sock.send("HELLO ENC MUL\r\n")
print

sentKey = list()

# Generate and send random encryption keys
for x in range(0, 20):
  key = ''.join(random.choice('0123456789abcdefABCDEF') for i in range(64))
  sock.send("%s\r\n" %key)
  sentKey.append(key)
sock.send(".\r\n")
print

# Receive message, split message and keys into list
line = sock.recv(2048)
line = line.split()

# Take cid and port number from list, then format the keys into index 0-19
cid = line[1]
uport = int(line[2])
del line[0], line[0], line[0], line[20]

# Open UDP socket, encrypt, pack and send first message
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
msg = ("Hello from %s" %cid)
msg = xor(msg,sentKey[0])
del sentKey[0]
pack_and_send(msg, 0)

# Loop for UDP messaging
s_eom = False       
while not s_eom:
  
  # Receive and unpack data
  data, adr = sock.recvfrom(1024)
  s_eom = check_eom(data)
  s_rem = check_rem(data)
  s_msg = unpack(data)
  
  # Decrypt message
  if not s_eom:
    s_msg = xor(s_msg,line[0])
    del line[0]
  
  # Receive and unpack multipart messages, add them to string
  while s_rem > 0:
    data, adr = sock.recvfrom(1024)
    s_rem = check_rem(data)
    next_part = unpack(data)
    next_part = xor(next_part,line[0])
    del line[0]
    s_msg += next_part
    
  print ("Server: " + s_msg)
  
  # Reverse, pack and send messages back  
  if not s_eom:
    rev = reverse(s_msg)
    
    rem = len(rev)
    
    for piece in pieces(rev):
      rem -= len(piece)
      piece = xor(piece,sentKey[0])
      del sentKey[0]
      pack_and_send(piece, rem)
      
    print ("Client: " + rev)

  print

# Close socket
sock.close()
