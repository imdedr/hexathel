#!/bin/bash
if [ "$(id -u)" == "0" ]; then
	/bin/cp -f -a hexathel /usr/local/
	/bin/cp -f wrapper/hexathel /usr/bin/
	/bin/cp -f wrapper/hexathel-artisan /usr/bin/
    /bin/cp -f wrapper/hexathel-shell /usr/bin/
	chmod +x /usr/bin/hexathel
	chmod +x /usr/bin/hexathel-artisan
    chmod +x /usr/bin/hexathel-shell
	echo 'Finish'
else
	echo 'Please use root'
fi