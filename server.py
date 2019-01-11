#  coding: utf-8 
import socketserver
import os
import mimetypes
# Copyright 2013 Abram Hindle, Eddie Antonio Santos
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
#
# Furthermore it is derived from the Python documentation examples thus
# some of the code is Copyright © 2001-2013 Python Software
# Foundation; All Rights Reserved
#
# http://docs.python.org/2/library/socketserver.html
#
# run: python freetests.py

# try: curl -v -X GET http://127.0.0.1:8080/


class MyWebServer(socketserver.BaseRequestHandler):
    ENCODING = "utf-8" # Default Encoding For Things
    BASEPATH = os.getcwd() + "/www" # Default Content Path For Requests

    def handle(self):
        ''' Handles all incoming requests to the server.

        Decodes requests crudely and handles GET requests, otherwise issues a 405 error.
        '''
        self.data = self.request.recv(1024).strip()

        request_as_list = self.data.split()
        request_as_list = [ item.decode("utf-8") for item in request_as_list]

        if not request_as_list:
            return

        request_type = request_as_list[0]
        request_path = request_as_list[1]

        if request_type == "GET":
            self.GET(request_path)
        else:
            self.sendError(405)

    def GET(self, request_path):
        ''' Handles GET requests using the request path.

        Defaults to index.html for directories.
        Sends 404 for paths not found or not starting with the path BASEPATH.
        '''
        
        final_path = self.BASEPATH + request_path

        if not os.path.exists(final_path):
            self.sendError(404)
            return

        if not os.path.realpath(final_path).startswith(self.BASEPATH):
            self.sendError(404)
            return

        if os.path.isdir(final_path):
            final_path += "index.html"

        content = open(final_path).read()

        self.sendStr(self.generateHttpHeader(200) + self.generateHttpContentType(final_path) + content)


    def sendStr(self, string):        
        byte_string = bytearray(string,self.ENCODING)
        self.request.sendall(byte_string)

    def sendError(self, num):
        self.sendStr(self.generateHttpHeader(str(num)))

    def generateHttpHeader(self, code):
        return "HTTP/1.1 {code} \r\n".format(code = code)

    def generateHttpContentType(self, path):
        return  "Content-type: {content_type}; \r\n\r\n".format(content_type=mimetypes.guess_type(path)[0])
        

if __name__ == "__main__":
    HOST, PORT = "localhost", 8080

    socketserver.TCPServer.allow_reuse_address = True
    # Create the server, binding to localhost on port 8080
    server = socketserver.TCPServer((HOST, PORT), MyWebServer)

    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C
    server.serve_forever()
