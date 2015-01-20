#-*- coding:utf-8 -*-
from webparser import WebParser
from selector import Selector
from helper import urlhelper
import datetime
import urllib
import time

class parser_vc(WebParser):

    def __init__(self):
        super(parser_vc, self).__init__()

    def parse( self, url, html ):
        sel = Selector( html )

        tmp = []

        # If Catalog 是 點數專區則直接拋棄
        param  = urlhelper.urlParamParse( url )
        if( param['sid'] == '14' ):
            return True, []

        #Key Word : 更多商品 請由左側目錄點選
        if( html.find('更多商品 請由左側目錄點選') != -1 ):

            #取的左側連接
            link = sel.xpath('//*[@id="block_left"]/div[1]/ul/li/a/@href')
            for i in link:
                if( i.find('www.gohappy.com.tw') != -1 ):
                    tmp.append(i)
                else:
                    tmp.append('http://www.gohappy.com.tw' + i)

        else:
            
            # Get Product Item
            product_list = sel.xpath('//ul[@class="product_list"]/li')

            #crumb
            path = sel.xpath('//ul[@id="path"]/li')

            print len(path)

            crumb = []
            
            for i in xrange( 1, len(path) ):


                href = path[i].xpath('span/a/@href')
                if( href == [] ):
                    href = path[i].xpath('a/@href')[0]
                else:
                    href = path[i].xpath('span/a/@href')[0]


                title = path[i].xpath('span/a/text()')
                if( title == [] ):
                    title = path[i].xpath('a/text()')[0]
                else:
                    title = path[i].xpath('span/a/text()')[0]


                if( href != '#' ):
                    id_list = urlhelper.urlParamParse( href )

                    cid = -1

                    if( 'cid' in id_list ):
                        cid = id_list['cid']
                    else:
                        cid = id_list['sid']

                    crumb.append( { 'id':cid, 'name':title } )

            data = dict()
            data['website_code'] = 'gohappy'
            data['1st_price_name'] = '特惠價'
            data['timestamp'] = datetime.datetime.utcnow()
            data['catalog'] = crumb

            for item in product_list:
                data['pic_url'] = item.xpath('p[1]/a/img/@src')[0].encode('utf-8')
                data['goods_name']  = item.xpath('p[1]/a/img/@title')[0]
                data['1st_price'] = item.xpath('p//span[@class="price"]/text()')[0]
                data['goods_url'] = 'http://www.gohappy.com.tw' + item.xpath('p[1]/a/@href')[0]
                data['goods_original_id'] = urlhelper.urlParamParse( data['goods_url'] )['pid']
                
                print "Download %s" % data['goods_original_id']
                try:
                    urllib.urlretrieve( data['pic_url'].replace('_2', '_4'), '/root/crawler/gohappy/img/%s.jpg' % data['goods_original_id'] )
                except:
                    try:
                        urllib.urlretrieve( data['pic_url'].replace('_2', '_3_1'), '/root/crawler/gohappy/img/%s.jpg' % data['goods_original_id'] )
                    except:
                        try:
                            urllib.urlretrieve( data['pic_url'], '/root/crawler/gohappy/img/%s.jpg' % data['goods_original_id'] )
                        except:
                            print 'Reset by Peer'

                data['local_pic'] = 'img/%s.jpg' % data['goods_original_id']
                
                # Write back to MongoDB
                data.pop('_id', None)
                self.db.gohappy.goods.insert(data)

            # Check Next Page
            current_page = 1
            param = urlhelper.urlParamParse( url )
            if( 'cp' in param ):
                current_page = int( param['cp'] )
            else:
                url += '&cp=1'

            #Get Last Page Url
            next_page = sel.xpath('//p[@class="page_number"]/a/@href')
            if( len(next_page) != 0 ):
                next_page = urlhelper.urlParamParse( next_page[len(next_page) -1 ] )['cp']
                next_page = int( next_page )
            else:
                next_page = 1

            if( next_page > current_page ):
                print 'Next Page'
                tmp.append( url.replace('cp=' + str(current_page), 'cp=' + str(next_page) ) )

        time.sleep(1)

        return True, tmp
