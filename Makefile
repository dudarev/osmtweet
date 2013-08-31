update:
	appcfg.py update src/

shell:
	echo "Use full email!"
	cd src && remote_api_shell.py -s osmdonetsk.appspot.com
