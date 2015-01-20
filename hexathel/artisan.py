import sys
import os

working_path = os.getcwd()
engine_path = os.path.dirname( os.path.abspath(__file__) )

def init():
	conf()
	env()

def conf():
	source = open( os.path.join( engine_path, 'template' , 'config.conf' ), 'r' )
	target = open( os.path.join( working_path, 'config.conf' ), 'w' )
	for line in source:
		target.write(line)
	source.close()
	target.close()

def env():
	source = open( os.path.join( engine_path, 'template' , 'environment.py' ), 'r' )
	target = open( os.path.join( working_path, 'environment.py' ), 'w' )
	for line in source:
		target.write(line)
	source.close()
	target.close()

def createParser( name ):
	source = open( os.path.join( engine_path, 'template' , 'parser.py' ), 'r' )
	target = open( os.path.join( working_path, 'parser_{name}.py'.format(name=name) ), 'w' )
	for line in source:
		target.write(line.replace('{name}', name))
	source.close()
	target.close()

def main():
	argv = sys.argv
	if 'init' in argv:
		init()
	elif 'config' in argv:
		conf()
	elif 'environment' in argv:
		env()
	elif 'parser' in argv:
		f = argv.index('parser')
		if ( (f + 1) < len(argv) ):
			createParser(argv[f+1])
		else:
			print 'Missing Parser Name'
	else:
		print 'Nothing...'

if __name__ == '__main__':
	main()