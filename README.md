# Auto Deploy Laravel on Apache
Deploy Laravel or Other Apps Easily on Apache from your Git Repos

## To Use:
Place these files in your /var/www on the server once Apache is set-up, just before your "project folder". For example, if I had a Laravel project in "myshop" directory, and it had a path of /var/www/myshop with web root being /var/www/myshop/public, then the deployment library would sit at /var/www/app_deploy.py. This runs using Python 3.  Make sure you read the source code and make sure it is configured for your project correctly.

> To Deploy a release (Commit code to Git locally, then run the deploy below on server or trigger this script.)

*youruser@localhost:/var/www$ python3 app_deploy.py -d*

*Permission issues can be solved by correcting your permissions on folders/files.

> To show releases

*youruser@localhost:/var/www$ python3 app_deploy.py --releases*

> To rollback a release to a release number, check show releases

*youruser@localhost:/var/www$ python3 app_deploy.py --rollback=3*

