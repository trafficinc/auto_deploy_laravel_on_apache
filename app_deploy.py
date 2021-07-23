'''
Deploy Laravel/Other Apps to Apache
By: Ron Bailey
'''
import json
import os
import sys
import deploylib
import datetime
import optparse

# settings
TEST = False
repo = 'git@bitbucket.org:yourgituseraccount/reponame.git'
project_name = 'reponame'
keep_releases = 5
shared_dirs = ['storage']
shared_files = ['.env']
link_storage_public = True
writable_dirs = []
writable_use_sudo = False
deploy_path = '/var/www'
cwd = os.getcwd()


# deploylib.cleanup_releases(cwd, keep_releases)
parser = optparse.OptionParser("App Deploy")

parser.add_option('-b', '--rollback', action="store", dest="rollback", help="rollback release", default=False)
parser.add_option('-v', '--releases', action="store_true", dest="releases", help="show releases", default=False)
parser.add_option('-d', '--deploy', action="store_true", dest="deploy", help="deploy release", default=False)
#parser.add_option('-h', '--help', action="store_true", dest="help", help="help", default=False)

options, args = parser.parse_args()

if options.rollback is not False:
    # rollback
    deploylib.rollback_release(cwd, options.rollback)

if options.releases is not False:
    deploylib.get_all_versions(cwd)

# if options.deploy is not False:
if options.deploy is not True:
    print("Not deployed.")
    print("Must add flag `--deploy` or `-d` flag to deploy.")
    sys.exit()

dep_dir = os.path.isdir(cwd + '/.dep')
releases_dir = os.path.isdir(cwd + '/releases')
shared_dir = os.path.isdir(cwd + '/shared')

if dep_dir and releases_dir and shared_dir:
    print("[+] Directories Set Up OK")
else:
    sys.exit("[x] Directories missing, run `inst_php_deploy.sh` to set them up.")

if not TEST:
    if os.path.isfile(cwd + '/.dep/deploy.lock'):
        sys.exit("[x] Stopped: Can only have one deployment at a time.")
    else:
        deploylib.create_deploy_lock(cwd + '/.dep/deploy.lock')
        print("[+] Lock created.")

# release step
run_first_time = False

if os.path.isfile(cwd + '/.dep/releases.json'):
    release_collection = []
    release_count = 0
    with open(cwd + '/.dep/releases.json') as json_file:
        data = json.load(json_file)
        for r in data['releases']:
            release_count += 1
            release_collection.append(r['name'])

        release_collection.sort()
        latest_release = release_collection[-1]
        new_release = latest_release + 1
        data['releases'].append({
            'name': int(new_release)
        })

        with open(cwd + '/.dep/releases.json', "w") as outfile:
            json.dump(data, outfile)

    print("latest_release: " + str(latest_release))
    print("new_release: " + str(new_release))
    print('[+] New release added out of {} releases'.format(release_count))
    if TEST:
        print('release_collection:')
        print(release_collection)

else:
    run_first_time = True
    rel_config = {'releases': []}
    rel_config['releases'].append({
        'name': 0
    })

    with open(cwd + '/.dep/releases.json', "w") as outfile:
        json.dump(rel_config, outfile)

    print('New releases file created')


if run_first_time:
    deploylib.create_directory(cwd, cwd + '/releases', '0')
    deploylib.create_directory(cwd, cwd + '/releases', '1')
    print('Release Folder created. [0]')
    print('Release Folder created. [1]')
    last_release = 0
    new_release = 1
    latest_release = new_release
    print(latest_release)
    print(new_release)
else:
    last_release = latest_release - 1
    latest_release = new_release


deploylib.create_directory(cwd, cwd + '/releases', str(new_release))
# copy to shared. shared_dirs, shared_files
shared_copy_logs = deploylib.copy_to_shared(cwd, str(last_release), shared_dirs, shared_files)
print(shared_copy_logs)

# git download code, run deploy script.
deploylib.run_scripts_deploy(cwd, str(latest_release), repo, project_name, shared_dirs, shared_files, str(last_release), link_storage_public)
deploylib.cleanup_releases(cwd, keep_releases)

deploylib.run_command("rm -f " + cwd + "/.dep/deploy.lock")
print("Deploy lock file released.")

