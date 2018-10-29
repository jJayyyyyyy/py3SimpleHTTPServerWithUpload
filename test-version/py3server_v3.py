#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Simple HTTP Server With Upload based on python3.
Python2-Version by [bones7456] and [BUPTGuo]:
    This module builds on BaseHTTPServer by implementing the standard GET and HEAD requests in a fairly straightforward manner.

Python3-Version by [FrozenMap]:
    Based on the new features in python3, this module is built on [http.server] by rewriting some implementations of do_GET, do_HEAD and do_POST and other functions in Python2-Version.

This is test version 3. <Upload> will be implemented.

More details can be found on GitHub Pages: https://jjayyyyyyy.github.io
"""

__version__ = "0.3"
__all__ = ["SimpleHTTPRequestHandler"]
__author__ = "bones7456, BUPTGuo, FrozenMap"
__home_page__ = "http://luy.li/, http://buptguo.com, https://jjayyyyyyy.github.io"


import os
import posixpath
import http.server
import urllib
import cgi
import shutil
import mimetypes
import re


class SimpleHTTPRequestHandler(http.server.BaseHTTPRequestHandler):

    """Simple HTTP request handler with GET/HEAD/POST commands.
    This serves files from the current directory and any of its
    subdirectories.  The MIME type for files is determined by
    calling the .guess_type() method. And can reveive file uploaded
    by client.
    The GET/HEAD/POST requests are identical except that the HEAD
    request omits the actual contents of the file.
    """

    server_version = "SimpleHTTPWithUpload/" + __version__

    def do_GET(self):
        """Serve a GET request."""
        f = self.send_head()
        if f:
            self.wfile.write(f)

    def do_HEAD(self):
        """Serve a HEAD request."""
        f = self.send_head()

    def do_POST(self):
        """Serve a POST request."""
        r, info = self.deal_post_data()
        print(r, info, "by: ", self.client_address)
        f = ('<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01//EN" "http://www.w3.org/TR/html4/strict.dtd">') +\
            ('<html><head>') +\
            ('<meta http-equiv="Content-Type" content="text/html; charset=utf-8">') +\
            ('<title>Upload Result Page</title>') +\
            ('</head><body>') +\
            ('<h1>Upload Result Page</h1>') +\
            ('<hr>')
        if r:
            f = f + ('<strong>Success:<strong>') + info
        else:
            f = f + ('<strong>Failed:<strong>') + info
        f = f + '<br><a href="%s">back</a>' % self.headers['referer'] +\
            '</body></html>'

        f = f.encode('utf-8')
        length = len(f)
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.send_header("Content-Length", str(length))
        self.end_headers()
        self.wfile.write(f)

    def deal_post_data(self):
        boundary = self.headers["Content-Type"].split("=")[1].encode('utf-8')
        remainbytes = int(self.headers['Content-length'])

        line = self.rfile.readline()
        remainbytes = remainbytes - len(line)
        if not boundary in line:
            return (False, "Content NOT begin with boundary")

        line = self.rfile.readline().decode('utf-8')
        remainbytes = remainbytes - len(line)

        fn = re.findall(r'Content-Disposition.*name="file"; filename="(.*)"', line)
        # the () is the key to re.findall
        if not fn[0]:
            return (False, "Can't find out file name...")
        path = self.translate_path(self.path)
        fn = os.path.join(path, fn[0])
        while os.path.exists(fn):
            fn += "_copy"

        # headers ends with \r\n\r\n
        line = self.rfile.readline()
        remainbytes = remainbytes - len(line)
        line = self.rfile.readline()
        remainbytes = remainbytes - len(line)
        try:
            localfile = open(fn, 'wb')
        except IOError:
            return (False, "Can't create file to write, do you have permission to write?")

        preline = self.rfile.readline()
        remainbytes = remainbytes - len(preline)

        while remainbytes > 0:
            line = self.rfile.readline()
            remainbytes = remainbytes - len(line)
            if boundary in line:
                preline = preline[0:-1]
                if preline.endswith(b'\r'):
                    preline = preline[0:-1]
                localfile.write(preline)
                localfile.close()
                return (True, "File '%s' upload success!" % fn)
            else:
                localfile.write(preline)
                preline = line
        return (False, "Unexpect Ends of data.")

    def send_head(self):
        """Common code for GET and HEAD commands.
        This sends the response code and MIME headers.
        Return value is either a file object (which has to be copied
        to the outputfile by the caller unless the command was HEAD,
        and must be closed by the caller under all circumstances), or
        None, in which case the caller has nothing further to do.
        """
        path = self.translate_path(self.path)
        f = None
        if os.path.isdir(path):
            if not self.path.endswith('/'):
                # redirect browser - doing basically what apache does
                self.send_response(301)
                self.send_header("Location", self.path + "/")
                self.end_headers()
                return None
            for index in "index.html", "index.htm":
                index = os.path.join(path, index)
                if os.path.exists(index):
                    path = index
                    break
            else:
                return self.list_directory(path)
        ctype = self.guess_type(path)
        try:
            # Always read in binary mode. Opening files in text mode may cause
            # newline translations, making the actual size of the content
            # transmitted *less* than the content-length!
            f = open(path, 'rb')
        except IOError:
            self.send_error(404, "File not found")
            return None
        self.send_response(200)
        self.send_header("Content-type", ctype)
        fs = os.fstat(f.fileno())
        self.send_header("Content-Length", str(fs[6]))
        self.send_header("Last-Modified", self.date_time_string(fs.st_mtime))
        self.end_headers()
        data = f.read()
        f.close()

        return data

    def list_directory(self, path):
        """Helper to produce a directory listing (absent index.html).
        Return value is either a file object, or None (indicating an
        error).  In either case, the headers are sent, making the
        interface the same as for send_head().
        """
        try:
            list = os.listdir(path)
        except os.error:
            self.send_error(404, "No permission to list directory")
            return None
        list.sort(key=lambda a: a.lower())
        displaypath = cgi.escape(urllib.parse.unquote(self.path))

        f = ('<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01//EN" "http://www.w3.org/TR/html4/strict.dtd">') +\
            ('<html><head>') +\
            ('<meta http-equiv="Content-Type" content="text/html; charset=utf-8">') +\
            ('<title>Directory listing for %s</title>' % displaypath) +\
            ('</head><body>') +\
            ('<h1>Directory listing for %s</h1>' % displaypath) +\
            ('<form ENCTYPE="multipart/form-data" method="post">') +\
            ('<input name="file" type="file"/>') +\
            ('<input type="submit" value="upload"/></form>') +\
            ('<hr><ul>')

        for name in list:
            fullname = os.path.join(path, name)
            displayname = linkname = name
            # Append / for directories or @ for symbolic links
            if os.path.isdir(fullname):
                displayname = name + "/"
                linkname = name + "/"
            if os.path.islink(fullname):
                displayname = name + "@"
                # Note: a link to a directory displays with @ and links with /
            f = f + ('<li><a href="%s">%s</a>' % (urllib.parse.quote(linkname), cgi.escape(displayname)))
        f = f + ("</ul><hr></body></html>")

        f = f.encode('utf-8')
        length = len(f)
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.send_header("Content-Length", str(length))
        self.end_headers()
        return f

    def translate_path(self, path):
        """Translate a /-separated PATH to the local filename syntax.
        Components that mean special things to the local file system
        (e.g. drive or directory names) are ignored.  (XXX They should
        probably be diagnosed.)
        """
        # abandon query parameters
        path = path.split('?',1)[0]
        path = path.split('#',1)[0]
        path = posixpath.normpath(urllib.parse.unquote(path))
        words = path.split('/')
        words = filter(None, words)
        path = os.getcwd()
        for word in words:
            drive, word = os.path.splitdrive(word)
            head, word = os.path.split(word)
            if word in (os.curdir, os.pardir): continue
            path = os.path.join(path, word)
        return path

    def guess_type(self, path):
        """Guess the type of a file.
        Argument is a PATH (a filename).
        Return value is a string of the form type/subtype,
        usable for a MIME Content-type header.
        The default implementation looks the file's extension
        up in the table self.extensions_map, using application/octet-stream
        as a default; however it would be permissible (if
        slow) to look inside the data to make a better guess.
        """

        base, ext = posixpath.splitext(path)
        if ext in self.extensions_map:
            return self.extensions_map[ext]
        ext = ext.lower()
        if ext in self.extensions_map:
            return self.extensions_map[ext]
        else:
            return self.extensions_map['']

    if not mimetypes.inited:
        mimetypes.init() # try to read system mime.types
    extensions_map = mimetypes.types_map.copy()
    extensions_map.update({
        '': 'application/octet-stream', # Default
        '.py': 'text/plain',
        '.c': 'text/plain',
        '.h': 'text/plain',
        })


def test(HandlerClass = SimpleHTTPRequestHandler,
         ServerClass = http.server.HTTPServer):
    http.server.test(HandlerClass, ServerClass)

if __name__ == '__main__':
    test()
