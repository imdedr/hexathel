
class Env(object):

	parser_list = dict()
	
	def __init__(self):
		super(Env, self).__init__()

	def addParser( self, name, rule ):
		self.parser_list[name] = rule
