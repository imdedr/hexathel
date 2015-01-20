#-*-coding:utf8 -*-
import pika
from pymongo import Connection as MongoClient
import datetime
import re
import urllib
import urllib2
import os
import ConfigParser
import sys
import traceback

class Engine(object):
    
    test_flag = False

    config = dict()

    mongo_connect = None

    channel = None

    parser_rule =[]
    parser_list = dict()

    working_path = os.getcwd()
    engine_path = os.path.dirname( os.path.abspath(__file__) )

    sentry = None

    def __init__(self):
        # Read the Config
        self.configLoader()
        self.setLogger()

    def configLoader(self):

        # ToDo: Make Env Function, Make develop more easy.

        self.config['env'] = dict()

        # Read Path
        config_path = os.path.join( self.engine_path , 'template' ,'config.conf' )
        config = ConfigParser.ConfigParser()
        config.read( config_path )

        for sec in config.sections():
            tmp = dict()
            for item in config.items(sec):
                tmp[item[0]] = item[1]
            self.config[sec] = tmp

        # Check the user config file
        if( os.path.exists( os.path.join( self.working_path , 'config.conf' ) ) ):
            config_path = os.path.join( self.working_path , 'config.conf' )
            config = ConfigParser.ConfigParser()
            config.read( config_path )
            for sec in config.sections():
                tmp = dict()
                for item in config.items(sec):
                    tmp[item[0]] = item[1]
                self.config[sec] = tmp

    def setLogger(self):
        if( self.config['logger']['use'] == '1' ):
            from raven import Client
            self.sentry = Client( 
                'http://%s:%s@%s:%s/%s' % ( 
                    self.config['logger']['public_key'],
                    self.config['logger']['private_key'],
                    self.config['logger']['host'],
                    self.config['logger']['port'],
                    self.config['logger']['project']
                      ) 
                )
            self.sentry.tags_context({'spider': self.config['basic']['name']})

    def log(self, t, msg):
        print str(datetime.datetime.utcnow()) + " [" + self.config['basic']['name'] + "]: [" + t + "]" + msg
        if( t == 'E' and self.config['logger']['use'] == '1' ):
            self.sentry.captureMessage(msg)

    def getUrl( self, url, vals, headers ):
        data = urllib.urlencode(vals)
        req = urllib2.Request(url, data, headers)
        response = urllib2.urlopen(req, timeout=5)
        return response.read()

    def rabbitMQ_create( self, ip, username, password, virtual_host, tqueue ):
        credentials = pika.PlainCredentials( username, password )
        connection = pika.BlockingConnection(pika.ConnectionParameters(host=ip, credentials=credentials, virtual_host=virtual_host))
        connection.channel().queue_declare(queue=tqueue, durable=True)
        return connection.channel()

    def rabbitMQ_send( self, channel, message, queue ):
        channel.basic_publish(exchange='', routing_key=queue, body=message, properties=pika.BasicProperties(delivery_mode = 2))
        self.log( 'N', 'Send Jobs:' + message)

    def register_parser(self, filename, exp):
        self.log( "R", "Register Parser:" + filename)

        #將 Regular Express 先 Compile 起來
        precompile_regexp = dict()
        for regexp in exp:
            precompile_regexp[regexp] = re.compile(regexp)

        self.parser_rule.append([precompile_regexp, filename, filename])

        # Load Parser And Make Instance
        parser_loader = __import__( filename, globals(), locals() )
        self.parser_list[filename] = getattr( parser_loader, filename )()

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

    def parser_assign(self):
        for p in self.parser_list:
            self.parser_list[p].db = self.mongo_connect
            self.parser_list[p].test_flag = self.test_flag
            self.parser_list[p].config = self.config['env']
            self.parser_list[p].log = self.log

    def setEnvironment(self):
        sys.path.append( self.working_path )
        loader = __import__( 'environment', globals(), locals() )

        for i in loader.env.parser_list:
            self.register_parser( i, loader.env.parser_list[i] )

    def consumer(self , ch, method, properties, body):
        self.log( 'N', 'Processing:' + body )
        if ( self.config['logger']['use'] == '1' ):
            self.sentry.tags_context({'Url': str(body.encode('utf-8')) })

        # URL Payload 處理
        # 若網址有 # 則截斷
        target_url = str(body.encode('utf-8'))
        if( target_url.find('#') != -1 ):
            target_url = target_url[:target_url.find('#')]
        # 取得網址 Match
        parser_name = self.parser_match( target_url )
        if ( parser_name != 0 ):
            # 取得對應的 Parser

            # 呼叫 init (帶入當前網址)
            self.parser_list[parser_name].init( str(body.encode('utf-8')) )

            # 呼叫 setBrowser (設定瀏覽器參數)
            browser_headers = self.parser_list[parser_name].setBrowser( str(body.encode('utf-8')) )
            # 下載網頁資訊
            try:
                page_html = self.getUrl( target_url, {}, browser_headers)
            except:
                self.log( "E", "Network Error:" + body )
                ch.basic_ack(delivery_tag = method.delivery_tag)
                return

            # 呼叫 Parser 方法
            try:
                state, new_url = self.parser_list[parser_name].parse( str(body.encode('utf-8')), page_html )
            
                # 接收回傳結構 ( 成功或失敗, 有無要進入Queue的)
                if ( state == True ):
                    self.log( 'N', 'Finish:' + str( body.encode('utf-8') ) )
                    if ( type( new_url ) == type( [] ) ):
                        if new_url:
                            for n in new_url:
                                self.rabbitMQ_send( ch, n.encode('utf-8'), self.config['broker']['queue'] )
                    else:
                        self.log( "E", "Return is not List - " + new_url )
                else:
                    self.log( 'E', 'Error:' + str( body ) )

            except Exception, e:
                if( self.config['logger']['use'] == '1' ):
                    self.sentry.captureException()
                traceback.print_exc()
                raise e
            
        else:
            self.log( "U", "Unmatch rule:" + body )

        ch.basic_ack(delivery_tag = method.delivery_tag)

    def run(self):

        try:
            from setproctitle import setproctitle
            setproctitle( "Hexathel - " + self.config['basic']['name'] )
        except Exception, e:
            print 'Can\'t set proc title.'

        self.log( "N", "Start Spider")

        if( self.test_flag ):
            self.log( "N", "Running in Test Mode")

        self.setEnvironment()

        if( self.config['backend']['use'] == '1' ):
            self.log( 'N', 'Connect to backend')
            try:
                self.mongo_connect = MongoClient(self.config['backend']['host'])
                self.mongo_connect.admin.authenticate(self.config['backend']['username'], self.config['backend']['password'])
                self.parser_assign()
            except Exception, e:
                self.log( 'E', 'Mongodb connect refuse' )
                self.quit()

        self.log( "N", "Connect to broker")
        try:
            self.channel = self.rabbitMQ_create( 
                    self.config['broker']['host'],
                    self.config['broker']['username'],
                    self.config['broker']['password'],
                    self.config['broker']['virtual_host'],
                    self.config['broker']['queue']
                    )
            self.channel.basic_qos(prefetch_count=1)
            self.channel.basic_consume(self.consumer, queue=self.config['broker']['queue'])
            self.log( 'N' , 'Ready to Start')
            self.channel.start_consuming()
        except Exception, e:
            if ( self.config['logger']['use'] == '1' ):
                self.sentry.captureException()
            else:
                traceback.print_exc()
            self.log( 'E', 'RabbitMQ connect refuse' )
            self.quit()

    def quit(self):
        print '\n  *** Terminal ***'
        exit()
