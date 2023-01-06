from socket import *
import sys


def webServer(port=6791):
  serverSocket = socket(AF_INET, SOCK_STREAM)
  serverSocket.bind(("127.0.0.1", port))
  serverSocket.listen(1)

  while True:
    print('Ready...')
    connectionSocket, addr = serverSocket.accept()  
    print ("addr:\n", addr)
    try:

      try:
        message = connectionSocket.recv(1024)  
        file = message.split()[1]
        f = open(file[1:])
        outputdata = f.read()  
        print(outputdata)

       
        connectionSocket.send('HTTP/1.1 200 OK \r\n\r\n'.encode()) 
        print('200 OK message')
        
        for i in range(0, len(outputdata)):
          connectionSocket.send(outputdata[i].encode())

        connectionSocket.send("\r\n".encode())
        connectionSocket.close()
      except IOError:
       
        connectionSocket.send('HTTP/1.1 404 Not Found\r\n'.encode())
        print('404 Not Found message')
       
        connectionSocket.close()
 

    except (ConnectionResetError, BrokenPipeError):
      pass
  
  serverSocket.close()
  sys.exit()  # Terminate the program after sending the corresponding data

if __name__ == "__main__":
  webServer(6791)