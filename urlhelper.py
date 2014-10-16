def urlParamParse( url ):
    param = dict()
    url_query = url[url.find('?')+1:]
    query_param = url_query.split('&')
    for i in query_param:
        tmp = i.split('=')
        param[tmp[0]] = tmp[1]
    return param

def urlParamBuilder( param ):
    tmp = ''
    for k, d in param.items():
        tmp += str(k) + '=' + str(d) + '&'
    return tmp[:-1]