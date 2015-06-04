'''Low level code for socket networking + HTTP'''
import socket
import select
import sys

CHUNK = 4096
CRLF = '\r\n'
CRLF2 = 2*CRLF

def recv_n(conn, n, data=''):
    '''Calls recv on conn until data is n bytes long.
    If data is given as an argument, then bytes are appended
    to it until data is n bytes long.'''
    while len(data) < n:
        data += conn.recv(n - len(data))
    return data

def recv_until(conn, sym, split=True, n=1):
    '''Collects bytes by calling recv on conn until sym is in
    the bytes. Returns a list of bytes before and after sym.'''
    data = ''
    while sym not in data:
        data += conn.recv(CHUNK)
    if split:
        return data.split(sym, n)
    else:
        return data

def raw_headers_to_dict(headers):
    '''Turns bytes containing header data into a dictionary.'''
    result = {}
    for line in headers.split(CRLF):
        key, val = line.split(': ')
        result[key] = val
    return result

def raw_firstline_to_dict(firstline):
    '''Takes the first line of an http response and turns it
    into a dict with the fields 'vers', 'code', and 'msg'.'''
    fields = ('vers', 'code', 'msg')
    return dict(zip(fields, firstline.split(' ', 2)))

def is_chunked(headers):
    '''True if the headers say the body is chunked.'''
    key = 'Transfer-Encoding'
    return key in headers and headers[key]=='chunked'

def recv_chunks(conn, body):
    '''Calls recv on conn until all chunks of body have been
    collected.'''
    new_body = ''
    while True:
        chunklength, body = body.split(CRLF, 1)
        chunklength = int(chunklength, 16)
        if chunklength > 0:
            if len(body) < chunklength:
                # The + 2 is to account for the extra CRLF
                # at the end of each chunk
                body = recv_n(conn, chunklength + 2, body)
                body += recv_until(conn, CRLF, split=False)
            new_body += body[:chunklength]
            body = body[chunklength + 2:]
        else:
            break
    return new_body

def is_too_short(headers, body):
    key = 'Content-Length'
    return key in headers and len(body) < int(headers[key])

def read_full_body(conn, headers, body):
    '''Collects all bytes of body smartly, handling
    chunked encoding and/or unfinished transfers of a body
    given a 'Content-Length' header.'''
    if is_chunked(headers):
        return recv_chunks(conn, body)
    if is_too_short(headers, body):
        length = int(headers['Content-Length'])
        return recv_n(conn, length, body)
    #if we get here then there is nothing more to do to body
    return body

def full_message(firstline, headers, body):
    '''Stuff all the data into a dict.'''
    result = {}
    result.update(firstline)
    result['headers'] = headers
    result['body'] = body
    return result

def read_message(conn):
    '''Reads an HTTP response from the socket 'conn',
    and returns a dict with the fields 'vers', 'code',
    'msg', 'headers', and 'body'.'''
    metadata, body = recv_until(conn, CRLF2)
    firstline, headers = metadata.split(CRLF, 1)
    firstline = raw_firstline_to_dict(firstline)
    headers = raw_headers_to_dict(headers)
    body = read_full_body(conn, headers, body)
    return full_message(firstline, headers, body)

def simple_server(ip, port, func):
    '''A socket server bound to the given ip and port.
    Requests are parsed into dictionaries and passed onto
    func. Func must return a string, which is then sent
    as a response to the connection.'''
    listener = socket.socket()
    listener.listen(100)
    listener.bind((ip, port))
    readmap = {listener.fileno():listener}
    
    try:
        while True:
            for read, _, _ in select.select(readmap.keys(), [], []):
                for fd in read:
                    if readmap[fd] == listener:
                        conn, _ = listener.accept()
                        readmap[conn.fileno()] = conn
                    else:
                        conn = readmap[fd]
                        try:
                            request = read_message(conn)
                        except: #this should only happen when the connection is closed
                            readmap.pop(fd)
                            conn.close()
                        else:
                            conn.sendall(func(request))
    except KeyboardInterrupt as exc:
        print '\r'
        for sock in readmap.values():
            sock.close()
