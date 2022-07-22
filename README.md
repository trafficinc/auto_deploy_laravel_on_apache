# PHP Deployment Script
Deploy Laravel or Other PHP Apps Easily on Apache from your Git Repos. *Proof of concept right now.

## To Use:
Place these files in your */var/www* on the server once Apache is set-up, just before your "project folder". For example, if I had a Laravel project in "myshop" directory, and it had a path of */var/www/myshop* with web root being */var/www/myshop/public*, then the deployment library would sit at */var/www/app_deploy.py*. This runs using Python 3.  Make sure you read the source code and make sure it is configured for your project correctly.

**First make sure the virtual hosts are pointing to the '*/var/www/current*' folder, as this is where your live site will be sitting via virtual link. Of course this can be configured to where ever you want it to be, just be sure to align the virutal hosts entry.**

Then run the *./inst_php_deploy.sh* to set up the directory structure, and if using laravel, then copy your .env and storage folder over to the *shared* folder that the *./inst_php_deploy.sh* just created.

> To Deploy a release (Commit code to Git locally, then run the deploy below on server or you can trigger this script from outside of the server via ssh.)

*youruser@localhost:/var/www$ python3 app_deploy.py -d*

*Permission issues can be solved by correcting your permissions on folders/files.

> To show releases

*youruser@localhost:/var/www$ python3 app_deploy.py --releases*

> To rollback a release to a release number, check show releases

*youruser@localhost:/var/www$ python3 app_deploy.py --rollback=3*

