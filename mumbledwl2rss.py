#!/usr/bin/env python
#
# Converts http://mumble.info/snapshot directory listing to an rss file.
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
    
    target_os_info = ['Yeay, an update. I do not know what exactly it is.',
                      'Windows binary, both client and server (32 bit).',
                      'Windows binary, both client and server (64 bit).',
                      'Mac OS X binary for the client.',
                      'Full source code for both client and server',
                      'Signature to verify the full source code package.',
                      'Mac OS X binary for the server (static), as xip.',
                      'Mac OS X binary for the server (static), as tar.bz2.',
                      'Signature to verify the Mac OS X binary package for the server.',                     
                      'Linux binary for the server (static).']
    
    if filename.startswith('mumble') and filename.endswith('.msi'):
        if "winx64" in filename:
		target_os = 2
	else:
		target_os = 1
    elif filename.startswith('Mumble') and filename.endswith('.dmg'):
        target_os = 3
    elif filename.startswith('mumble') and filename.endswith('.tar.gz'):
        target_os = 4
    elif filename.startswith('mumble') and filename.endswith('.tar.gz.sig'):
        target_os = 5
    elif filename.startswith('Murmur-OSX-Static') and filename.endswith('.xip'):
        target_os = 6
    elif filename.startswith('Murmur-OSX-Static') and filename.endswith('.tar.bz2'):
        target_os = 7
    elif filename.startswith('Murmur-OSX-Static') and filename.endswith('.tar.bz2.sig'):
        target_os = 8
    elif filename.startswith('murmur-static') and filename.endswith('.tar.bz2'):
        target_os = 9
    else:
        target_os = 0
    
    return target_os_info[target_os]

if __name__ == "__main__":    
    if len(sys.argv) < 2:
        print_help()
    else:
        rssfilename = sys.argv[1]
        webpage=urllib.urlopen("http://mumble.info:8080/snapshot/").read()
        baseurl = "http://mumble.info/snapshot/"
        
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
            
            match = re.search(r'^ ([^ ]*).*([0-9]{1,2}-[a-zA-Z]{3}-[0-9]{4} [0-9]{2}:[0-9]{2})', line)
                
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
