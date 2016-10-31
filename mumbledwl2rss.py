#!/usr/bin/env python
#
# Converts https://dl.mumble.info/ directory listing to an rss file.
#
# Natenom <natenom@natenom.com>
#
# This code is Public Domain.
#
# HTMLParser example taken from http://stackoverflow.com/questions/753052/strip-html-from-strings-in-python

from HTMLParser import HTMLParser
import urllib, sys, uuid, re
from time import localtime, strftime

class NewHTMLParser(HTMLParser):
    def __init__(self):
        HTMLParser.__init__(self)
        self.data = []

    def handle_data(self, d):
        self.data.append(d)

    def get_data(self):
        return ''.join(self.data)

def print_help():
    print("%s output.rss" % sys.argv[0])

def get_target_os_info(filename):
    """Determine target system by prefix and suffix and returns a short description."""

    target_os_info = {  'unknown': 'Yeay, an update. I do not know what exactly it is.',
			'win.client.32': 'Windows binary, both client and server (32 bit).',
			'win.client.32.sig': 'Signature to verify Windows binary, both client and server (32 bit).',
			'win.client.64': 'Windows binary, both client and server (64 bit).',
			'win.client.64.sig': 'Signature to verify Windows binary, both client and server (64 bit).',
			'mac.client': 'Mac OS X binary for the client.',
			'mac.client.sig': 'Signature to verify Mac OS X binary for the client.',
			'mac.client.universal': 'Mac OS X binary for the client (universal).',
			'mac.client.universal.sig': 'Signature to verify Mac OS X binary for the client (universal).',
			'source': 'Full source code for both client and server',
			'source.sig': 'Signature to verify the full source code package.',
			'mac.server.xip': 'Mac OS X binary for the server (static), as xip.',
			'mac.server.tar.bz2': 'Mac OS X binary for the server (static), as tar.bz2.',
			'mac.server.tar.bz2.sig': 'Signature to verify the Mac OS X binary package for the server.',
			'linux.server.static': 'Linux binary for the server (static).',
			'linux.server.static.sig': 'Signature to verify the Linux binary for the server (static).' }

    if filename.startswith('mumble') and filename.endswith('.msi'):
        if "winx64" in filename:
		target_os = 'win.client.64'
	else:
		target_os = 'win.client.32'
    elif filename.startswith('mumble') and filename.endswith('.msi.sig'):
        if "winx64" in filename:
		target_os = 'win.client.64.sig'
	else:
		target_os = 'win.client.32.sig'
    elif filename.startswith('Mumble') and filename.endswith('.dmg'):
        if "Universal" in filename:
		target_os = 'mac.client.universal'
	else:
		target_os = 'mac.client'
    elif filename.startswith('Mumble') and filename.endswith('.dmg.sig'):
        if "Universal" in filename:
		target_os = 'mac.client.universal.sig'
	else:
		target_os = 'mac.client.sig'
    elif filename.startswith('mumble') and filename.endswith('.tar.gz'):
        target_os = 'source'
    elif filename.startswith('mumble') and filename.endswith('.tar.gz.sig'):
        target_os = 'source.sig'
    elif filename.startswith('Murmur-OSX-Static') and filename.endswith('.xip'):
        target_os = 'mac.server.xip'
    elif filename.startswith('Murmur-OSX-Static') and filename.endswith('.tar.bz2'):
        target_os = 'mac.server.tar.bz2'
    elif filename.startswith('Murmur-OSX-Static') and filename.endswith('.tar.bz2.sig'):
        target_os = 'mac.server.tar.bz2.sig'
    elif filename.startswith('murmur-static') and filename.endswith('.tar.bz2'):
        target_os = 'linux.server.static'
    elif filename.startswith('murmur-static') and filename.endswith('.tar.bz2.sig'):
        target_os = 'linux.server.static.sig'
    else:
        target_os = 'unknown'

    return target_os_info[target_os]

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print_help()
    else:
        rssfilename = sys.argv[1]
        webpage=urllib.urlopen("https://dl.mumble.info/").read()
        baseurl = "https://dl.mumble.info/"

        parser = NewHTMLParser()
        parser.feed(webpage)
        pagecontent = parser.get_data()

        rssfile = open(rssfilename, 'w')
        rssfile.write('<?xml version="1.0" encoding="utf-8"?>\n')
        rssfile.write('<feed xmlns="http://www.w3.org/2005/Atom">\n')
        rssfile.write('<author>\n')
        rssfile.write('<name>I like Mumble</name>\n')
        rssfile.write('</author>\n')
        rssfile.write('<title>Mumble Downloads (inofficial feed)</title>\n')
        rssfile.write('<id>urn:uuid:%s</id>\n' % uuid.uuid3(uuid.NAMESPACE_DNS, 'Mumble Downloads'))
        rssfile.write('<updated>%s</updated>\n'% strftime("%Y-%m-%dT%H:%M:%SZ", localtime()))

        counter = 0
        for line in pagecontent.strip().split('\n'):
            if counter == 30: # We want the last xx packages.
                break

            found = False
            filename=""
            timestamp=""

            match = re.search(r'^ ([^ ]*).*([0-9]{1,4}-[0-9]{1,2}-[0-9]{1,2} [0-9]{2}:[0-9]{2})', line)
            # This works on " mumble-1.2.16.msi.sig                                               2016-05-05 22:30  836"

            try:
                filename = match.group(1).strip()
                timestamp = match.group(2)
                found = True
                counter += 1
            except:
                pass

            if found == True:
                rssfile.write('<entry>\n')
                rssfile.write('<title>%s</title>\n' % filename)
                rssfile.write('<link href="%s"/>\n' % (baseurl + filename))
                rssfile.write('<id>urn:uuid:%s</id>\n' % uuid.uuid3(uuid.NAMESPACE_DNS, filename))
                rssfile.write('<updated>%s</updated>\n' % timestamp)
                rssfile.write('<summary>%s</summary>\n' % filename)
                rssfile.write('<content>%s</content>\n' % get_target_os_info(filename))
                rssfile.write('<link rel="enclosure" href="%s" />\n' % (baseurl + filename))
                rssfile.write('</entry>\n')

        rssfile.write('</feed>')
        rssfile.close()
        parser.close()
