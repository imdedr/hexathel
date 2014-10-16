#-*-coding:utf8 -*-
import pika
from pymongo import Connection as MongoClient
import datetime
import re
import urllib
import urllib2

class Spider(object):
    
    config = dict()
    mongo_connect = None
    channel = None
    parser_rule =[]
    parser = dict()

    def __init__(self):
        self.config['basic'] = {
            "name":"spider"
            }

        self.config['syslogd'] = { 
            "ip" : "127.0.0.1", 
            "port" : "80" 
            }

        self.config['broker'] = { 
            "ip":"127.0.0.1",
            "port":"5672",
            "queue":"jobs",
            "user":"keniver",
            "pass":"keniver"
            }
        
        self.config['database'] = { 
            "ip":"127.0.0.1",
            "port":"23762",
            "user":"keniver",
            "pass":"keniver",
            "db":"test",
            "auth":"admin"
            }

    def debug(self):
        print "Debug Message:"
        print "Config:"
        for config_tag in self.config:
            print "    [", config_tag,"]:"
            for k in self.config[config_tag]:
                print "       ", k, "-", self.config[config_tag][k]

        print "Parser:"
        for p in self.parser_rule:
            print "    [" + p[1] + "/" + p[2] + "]:"
            for re in p[0]:
                print "        " + re

    def log(self, t, msg):
        print str(datetime.datetime.utcnow()) + " [" + self.config['basic']['name'] + "]: [" + t + "]" + msg

    def set(self, tag, key, val):
        self.config[tag][key] = val

    def getUrl( self, url, vals, headers ):
        data = urllib.urlencode(vals)
        req = urllib2.Request(url, data, headers)
        response = urllib2.urlopen(req, timeout=5)
        return response.read()

    def rabbitMQ_create( self, ip, username, password, tqueue ):
        credentials = pika.PlainCredentials( username, password )
        connection = pika.BlockingConnection(pika.ConnectionParameters(host=ip, credentials=credentials))
        connection.channel().queue_declare(queue=tqueue, durable=True)
        return connection.channel()

    def rabbitMQ_send( self, channel, message, queue ):
        channel.basic_publish(exchange='', routing_key=queue, body=message, properties=pika.BasicProperties(delivery_mode = 2))
        self.log( 'N', 'Send Jobs:' + message)

    def register_parser(self, exp, filename, classname):
        self.log( "R", "Register Parser:" + filename + ":" + classname)

        #將 Regular Express 先 Compile 起來
        precompile_regexp = dict()
        for regexp in exp:
            precompile_regexp[regexp] = re.compile(regexp)

        self.parser_rule.append([precompile_regexp, filename, classname])

        # Load Parser And Make Instance
        parser_loader = __import__( filename, globals(), locals() )
        self.parser[filename] = getattr( parser_loader, classname )()

    def parser_match(self, url):
        find_tag = 0
        for item in self.parser_rule:
            for exp in item[0]:
                if( item[0][exp].match(url) ):
                    return item[1]
                    find_tag = 1
                    break
            if( find_tag ):
                break

        if ( not find_tag ):
            return 0

    def parser_db_assign(self):
        for p in self.parser:
            self.parser[p].db = self.mongo_connect

    def consumer(self , ch, method, properties, body):
        self.log( 'N', 'Processing:' + body )
        # 取得網址 Match
        parser_name = self.parser_match( str(body.encode('utf-8')) )
        if ( parser_name != 0 ):
            # 取得對應的 Parser
            # 呼叫 init (帶入當前網址)
            self.parser[parser_name].init( str(body.encode('utf-8')) )
            # 呼叫 setBrowser (設定瀏覽器參數)
            browser_headers = self.parser[parser_name].setBrowser( str(body.encode('utf-8')) )
            # 下載網頁資訊
            try:
                page_html = self.getUrl( str( body ), {}, browser_headers)
            except:
                self.log( "E", "Network Error:" + body )
                ch.basic_ack(delivery_tag = method.delivery_tag)
                return
            # 呼叫 Parser 方法
            state, new_url = self.parser[parser_name].parse( str(body.encode('utf-8')), page_html )
            # 接收回傳結構 ( 成功或失敗, 有無要進入Queue的)
            if ( state == True ):
                self.log( 'N', 'Finish:' + str( body ) )
                if ( type( new_url ) == type( [] ) ):
                    if new_url:
                        for n in new_url:
                            self.rabbitMQ_send( ch, n.encode('utf-8'), self.config['broker']['queue'] )
                else:
                    self.log( "E", "Return is not List - " + new_url )
            else:
                self.log( 'E', 'Error:' + str( body ) )
        else:
            self.log( "E", "Unmatch rule:" + body )
        ch.basic_ack(delivery_tag = method.delivery_tag)

    def run(self):
        self.log( "N", "Start Spider")

        self.log( 'N', 'Connect to database')
        self.mongo_connect = MongoClient(self.config['database']['ip'])
        self.mongo_connect.admin.authenticate(self.config['database']['user'], self.config['database']['pass'])
        self.parser_db_assign()

        self.log( "N", "Connect to broker")
        self.channel = self.rabbitMQ_create( 
                self.config['broker']['ip'],
                self.config['broker']['user'],
                self.config['broker']['pass'],
                self.config['broker']['queue']
                )
        self.channel.basic_qos(prefetch_count=1)
        self.channel.basic_consume(self.consumer, queue=self.config['broker']['queue'])
        self.channel.start_consuming()
