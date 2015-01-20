#-*-coding:utf8 -*-
import argparse
import engine

def buildArgs():
    parser = argparse.ArgumentParser()

    #Default daemon mode
    parser.add_argument('-d', dest='daemon_mode', action='store_const', const=1)

    #Test mode (It will set the test flag)
    parser.add_argument('-t', dest='test_mode', action='store_const', const=1)

    return parser.parse_args()

def main():
    args = buildArgs()
    engine_instance = engine.Engine()
    
    if( args.test_mode == 1):
    	engine_instance.test_flag = True

    if( args.daemon_mode == 1):
        try:
            import daemon
            with daemon.DaemonContext():
                engine_instance.run()
        except Exception, e:
            print 'Python-Daemon is necessary.'
    else:
        engine_instance.run()

if __name__ == '__main__':
    main()