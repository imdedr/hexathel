from env import Env
env = Env()

env.addParser( 
	"parser_home",
	[ 
	  "^http://www.gohappy.com.tw/$", 
	  "^http://www.gohappy.com.tw/intro/sitemap.html$"
	]
)