from socket import *
import sys
import re
import os




def createsent(file, info):
    
    hHeading = 'HTTP/1.1 200 OK\r\n'
    if '.jpg' in file:
        hHeading += 'Content-Type: image/jpeg\r\n'
    elif 'html' or 'htm' in file:
        hHeading += 'Content-Type: text/html\r\n'
    elif '.ico' in file:
        hHeading += 'Content-Type: image/x-icon\r\n'
    elif '.css' in file:
        hHeading += 'Content-Type: text/css\r\n'
    elif '.js' in file:
        hHeading += 'Content-Type: application/javascript\r\n'
    elif '.txt' in file:
        hHeading += 'Content-Type: text/plain\r\n'
    else:
        hHeading += 'Content-Type: application/octet-stream\r\n'
    hHeading += ('Content-Length: ' + str(len(info)))
    hHeading += '\r\n\r\n'
    print ('HEADER FROM PROXY TO CLIENT')
    print (hHeading)
    hHeading += info
    return hHeading

def createRequest(host, url, prior):
    try:
        hostInd = url.index(host)
        if len(url[hostInd + len(host):]) < 3:
            url = 'http://www.' + url

            pass
        else:
            url = url[hostInd + len(host):]
    except ValueError:
        pass
    hHeading = "GET " + url + " HTTP/1.1\r\n"
    hHeading += ("Host: " + host + '\r\n')
    hHeading += "Connection: close\r\n"
    
    for line in prior.split('\r\n'):
        if 'User-Agent' in line:
            hHeading += (line + '\r\n')
        if 'Accept:' in line:
            hHeading += (line + '\r\n')
        if 'Referer:' in line:
            hHeading += (line + '\r\n')
        if 'Accept-Encoding:' in line:
            hHeading += (line + '\r\n')
        if 'Accept-Language:' in line:
            hHeading += (line + '\r\n')
        if 'Cookie:' in line:
            hHeading += (line + '\r\n')
    hHeading += '\r\n\r\n'
    return hHeading

def prin404(info):
    hHeading = 'HTTP/1.1 404 Not Found\r\n'
    hHeading += 'Content-Type: text/html; charset=UTF-8\r\n'
    print ('HEADER FROM PROXY TO CLIENT')
    print (hHeading)
    hHeading += '\r\n\r\n'
    hHeading += info
    return hHeading

if len(sys.argv) <= 1:
  print ('Usage : "python proxyserver.py server_ip"\n[server_ip : Address of the proxy server')
  sys.exit(2)

serverIP = sys.argv[1]

BUFFER = 1048576

#port number is arbituary
incomingPort = 5005
# holds names of files sent with special encoding i.e gzip
encodeFlag = []
encodeDict = {}

try:
    #create welcoming socket
    incoming = socket(AF_INET, SOCK_STREAM)

    #bind to the server address
    incoming.bind((serverIP, incomingPort))

    #begin listening (argument is number of allowed queued connections)
    incoming.listen(5)


#listening loop
    while True:
        print('Ready...')
        
        client, clientAddress = incoming.accept()
        print('WEB PROXY SERVER CONNECTED ' + str(clientAddress))

        try:
            client.settimeout(0.1)
            request = client.recv(BUFFER)
        except timeout:
            client.shutdown(SHUT_RDWR)
            client.close()
            continue 
        
        if(len(request) > 0):
            print('CLIENT MESSAGE:')
            print(request)
        else:
            client.shutdown(SHUT_RDWR)
            client.close()
            continue 
        

        method = request.split(" ")[0]
        url = request.split(" ")[1]

        url_pos = url.find("://")
        if url_pos != -1:
            url = url[(url_pos+3):]
        path_pos = url.find("/")
        host = url
        if path_pos != -1:
            host = url[:path_pos]
        for line in request.split('\r\n'):
            if "Referer:" in line:
                var = line.split(" ")[1]
                var = var.split(':'.join([str(serverIP), str(incomingPort)]))[1]
                domIndex = var.find(".")
                host = var[1:domIndex+4]
        
        print ('METHOD = ' + method + ', ADDRESS = ' + url)

                
        writefile = True
        filematcher = re.compile("((.?)*\.(jpg|htm|html)$)")
        fmatch = filematcher.match(url)
        print (fmatch)
        file = url.split('/')[-1]   
        if (fmatch):
            
            if file in os.listdir("."):
                with open(file, 'r') as file:
                    hHeading = 'HTTP/1.1 200 OK\r\n'
                    if '.jpg' in file:
                        hHeading += 'Content-Type: image/jpeg\r\n'
                    elif 'html' or 'htm' in file:
                        hHeading += 'Content-Type: text/html\r\n'
                    else:
                        hHeading += 'Content-Type: application/octet-stream\r\n'
                    
                    info = file.read()
                    hHeading += ('Content-Length: ' + str(len(info)))
                    
                    if file in encodeFlag:
                        hHeading += (encodeDict[file] + '\r\n') 
                    
                    hHeading += '\r\n\r\n'
                    
                    print (hHeading)
                    hHeading += info
                    
                    client.send(hHeading)
                    client.close()
                    continue                                        
        else:
            writefile = False
            
        
        try:
            print ('SEARCH CACHE')
            SOC = socket(AF_INET, SOCK_STREAM)
            print (host)

            if host[0] == '/':
                host = host[1:]
            host = host
            print ('HOSTNAME IS ' + host )
            IP = gethostbyname(host)
            print (IP)
            address = (IP, 80)
            SOC.connect(address)
            newRequest = createRequest(host, url, request)
            print ('REQUEST MESSAGE')
            print (newRequest)
            SOC.send(newRequest)
            error = False 
            print(writefile)
            if(writefile):
                with open(file, 'w') as file:                
                    while True:
                        SOC.settimeout(0.5) 
                        sent = SOC.recv(BUFFER)
                        if(len(sent) > 0):
                            try:
                                if '404' in sent.split('\r\n\r\n')[0]:
                                    var = sent.split('\r\n\r\n')
                                    header = var[0]
                                    print (header)
                                    if len(var) < 3:
                                        info = var[1]
                                    else:
                                        info = '\r\n\r\n'.join(var[1:])
                                    new = prin404(info)
                                    client.send(sent)
                                    error = True
                                    break
                                    
                                if 'HTTP' in sent.split('\r\n\r\n')[0]:
                                    var = sent.split('\r\n\r\n')
                                    header = var[0]
                                    print ('SENT HEADER FROM ORIGINAL SERVER')
                                    print (header)
                                    print ('[WRITE FILE INTO CACHE]: ' + file +'\n')
                                    if len(var) < 3:
                                        info = var[1]
                                    else:
                                        info = '\r\n\r\n'.join(var[1:])
                                    file.write(info)
                                else:
                                    file.write(sent)
                                
                                for line in sent.split('\r\n'):
                                    if 'Content-Encoding:' in line:
                                        encodeFlag.append(file)
                                        encodeDict[file] = line

                            except IndexError:
                                file.write(sent)
                                client.send(sent)
                            
                        else:
                           

                            break
            else:
                while True:
                        SOC.settimeout(1.0)
                        sent = SOC.recv(BUFFER)
    
                        if(len(sent) > 0):
                            client.send(sent)
                        else:
                            break
            if error:
                print('here1')
                with open(file, 'r') as file:
                    info = file.read()
                    new = prin404(info)
                    client.send(new)
            else:
                print('here2')
                with open(file, 'r') as file:
                    info = file.read()
                    new = createsent(file, info)
                    client.send(new)
            SOC.close()
            client.close()
        except timeout:
            print ('timeout')
            SOC.close()
            client.close()
        except Exception as e:
            print(e)
            
except KeyboardInterrupt:
    print ('Exiting Gracefully')
    incoming.shutdown(SHUT_RDWR)
    incoming.close()
    sys.exit()

    
if __name__ == '__main__':
    main()
