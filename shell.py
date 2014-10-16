import code
import urllib
import urllib2
import argparse

def execute():
    parser = argparse.ArgumentParser()
    parser.add_argument('-u', dest='url', type=str)
    args = parser.parse_args()
    url = args.url
    if( url == None ):
        print '[Help] -u "Target Url"'
        return -1

    def getUrl( url, vals = {} ):
        data = urllib.urlencode(vals)
        headers = { 'User-Agent' : 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/34.0.1847.131 Safari/537.36' }
        req = urllib2.Request(url, data, headers)
        response = urllib2.urlopen(req)
        return response.read()

    from hexathel.selector import Selector
    sel = Selector(getUrl(url))
    code.interact(banner= "Hexathel Spider Interact Tool\n[Object] sel : XPath Tool", local=locals())

if __name__ == "__main__":
    execute()