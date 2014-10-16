def cut( html, left_token, right_token ):
    left_find = html.find( left_token )
    right_find = html.find( right_token, left_find + len( left_token ) )
    if( left_find == -1 or right_find == -1 ):
        return -1
    else:
        return html[left_find + len(left_token):right_find]