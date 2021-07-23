import datetime
import os
import shutil
import stat
import subprocess
import sys
import json
import time


def create_deploy_lock(deploy_file):
    f = open(deploy_file, "x")


def get_folders_cnt(dir_search):
    total_dirs = 0
    my_dirs = []
    for base, dirs, files in os.walk(dir_search):
        for directories in dirs:
            total_dirs += 1
            my_dirs.append(int(directories))

    my_dirs.sort()
    return {'total_dirs': total_dirs, 'dirs': my_dirs}


def create_directory(cwd, my_path, release):
    run_command("mkdir " + cwd + '/releases/' + release)


def clear_folder(directory):
    for root, dirs, files in os.walk(directory):
        for f in files:
            os.unlink(os.path.join(root, f))
        for d in dirs:
            shutil.rmtree(os.path.join(root, d))


def clean_dir(location):
    fileList = os.listdir(location)

    for fileName in fileList:
        fullpath=os.path.join(location, fileName)
        if os.path.isfile(fullpath):
            os.chmod(fullpath, stat.S_IRWXU | stat.S_IRWXG | stat.S_IRWXO)
            os.remove(os.path.join(location, fileName))
        elif os.path.islink(fullpath):
            os.unlink(fullpath)
        elif os.path.isdir(fullpath):
            if len(os.listdir(fullpath)) > 0:
                clean_dir(fullpath)
            shutil.rmtree(os.path.join(location, fileName))

    return


def copy_to_shared(cwd, release, shared_dirs, shared_files):
    logs = []
    for directory in shared_dirs:
        dir_src = cwd + '/releases/' + release + '/' + directory
        dir_dest = cwd + '/shared/' + directory
        if os.path.isdir(dir_dest):
            logs.append('Dir Exists already: {}'.format(dir_dest))
        else:
            result_dir = shutil.copytree(dir_src, dir_dest)
            logs.append('Dir Added: {}'.format(result_dir))

    for shared_file in shared_files:
        file_src = cwd + '/releases/' + release + '/' + shared_file
        file_dest = cwd + '/shared/' + shared_file
        if os.path.isfile(file_dest):
            logs.append('File Exists: {}'.format(file_dest))
        else:
            result_file = shutil.copy(file_src, file_dest)
            logs.append('File Added: {}'.format(result_file))

    return logs


# DONT USE!! - todo remove
def remove_resources_from_release(cwd, release, shared_dirs, shared_files):
    # for directory in shared_dirs:
    #     dir_src = cwd + '/releases/' + release + '/' + directory
    #     if os.path.isdir(dir_src):
    #         # clear_folder(dir_src)
    #         run_command("rm -f " + dir_src)
    #     else:
    #         print("Directory does not exist to remove: {}".format(dir_src))

    for shared_file in shared_files:
        file_src = cwd + '/releases/' + release + '/' + shared_file
        if os.path.isfile(file_src):
            run_command("rm -f " + file_src)
            # os.remove(file_src)
        else:
            print("File does not exist to remove: {}".format(file_src))


def run_command(my_commands):
    subprocess.call(my_commands, shell=True)


def write_to_releases_file(cwd, release_file):
    file1 = open(cwd + "/.dep/releases.txt", "a")
    file1.write(release_file + "\n")
    file1.close()


# run after deploy, post scripts here.
def run_deploy_check(cwd, new_release):
    pass


def run_vendors(cwd, new_release):
    # Can edit this section for Laravel specific cmds
    os.chdir(cwd + '/releases/' + new_release)
    which_composer = subprocess.run("which composer", shell=True, stdout=subprocess.PIPE)
    composer = which_composer.stdout.decode('utf-8').rstrip()
    which_php = subprocess.run("which php", shell=True, stdout=subprocess.PIPE)
    php = which_php.stdout.decode('utf-8').rstrip()
    # Install Composer libs
    print("Install Composer Libs")
    run_command(composer + " install --optimize-autoloader")
    # Install NPM
    print("Install NPM Libs")
    run_command("npm install")
    run_command("npm run production")
    # Update Laravel
    print("Update Laravel")
    run_command(php + " artisan cache:clear")
    run_command(php + " artisan route:cache")
    run_command(php + " artisan config:cache")
    run_command(php + " artisan view:clear")
    run_command(php + " artisan queue:restart")
    os.chdir(cwd)


def symlink_project_resources(cwd, shared_dirs, shared_files, new_release, link_storage_public):
    os.chdir(cwd)
    current_release_dir = cwd + "/releases/" + new_release
    shared_dir = cwd + "/shared"
    print("Current release DIR: " + cwd)
    print("symlink_project_resources START")

    # remove release /storage folder
    run_command("rm -rf " + current_release_dir + "/storage")

    if link_storage_public:
        run_command("rm -f " + current_release_dir + "/public/storage")
        #  symbolic link from public/storage to storage/app/public
        run_command("ln -s " + cwd + "/shared/storage/app/public " + current_release_dir + "/public/storage")
        print("[php artisan storage:link]... complete.")

    for keep_directory in shared_dirs:
        run_command("ln -s {} {}".format(shared_dir + "/" + keep_directory, current_release_dir + "/" + keep_directory))

    # time.sleep(3)

    for keep_file in shared_files:
        run_command("ln -s {} {}".format(shared_dir + "/" + keep_file, current_release_dir + "/" + keep_file))

    print("symlink_project_resources END")


def run_symlinks(cwd, new_release):
    os.chdir(cwd)
    print("Going live with deploy...")
    run_command("rm -f " + cwd + "/current")
    run_command("ln -s " + cwd + "/releases/" + new_release + " " + cwd + "/current")
    print("Deploy is live!")


def run_post_deploy(cwd, new_release):
    current_release_dir = cwd + "/releases/" + new_release
    os.chdir(cwd + "/current")
    run_command("php artisan config:clear")
    os.chdir(cwd)
    # run_command("sudo chown -R $USER:www-data shared")
    # run_command("chmod -R 775 shared/storage")


def run_scripts_deploy(cwd, new_release, repo, project_name, shared_dirs, shared_files, last_release,
                       link_storage_public):
    which_git = subprocess.run("which git", shell=True, stdout=subprocess.PIPE)
    git = which_git.stdout.decode('utf-8').rstrip()
    repo_dir = cwd + '/.dep/repo'
    release_path = cwd + '/releases/' + new_release
    shutil.rmtree(repo_dir)
    os.mkdir(repo_dir)
    os.chdir(repo_dir)
    run_command("git clone " + repo)
    os.chdir(project_name)
    run_command(git + " archive HEAD | tar -x -f - -C  " + release_path + " 2>&1")
    revision_list = subprocess.run(git + " rev-list HEAD -1", shell=True, stdout=subprocess.PIPE)
    revision_id = revision_list.stdout.decode('utf-8')
    write_to_releases_file(cwd, 's/revision/{}/{}'.format(revision_id.rstrip(), datetime.datetime.now()))
    storage_dir_src = cwd + '/releases/' + str(new_release) + '/storage'
    #run_command("chown -R youruser:www-data " + cwd + '/releases/' + str(new_release))
    run_command("rm -rf " + storage_dir_src)

    run_vendors(cwd, new_release)
    run_deploy_check(cwd, new_release)
    symlink_project_resources(cwd, shared_dirs, shared_files, new_release, link_storage_public)
    run_symlinks(cwd, new_release)
    run_post_deploy(cwd, new_release)


def get_all_versions(cwd):
    with open(cwd + '/.dep/releases.json') as json_file:
        data = json.load(json_file)
        for r in data['releases']:
            print("Release #: {}".format(r['name']))


def rollback_release(cwd, release_version):
    with open(cwd + '/.dep/releases.json') as json_file:
        data = json.load(json_file)
        rollback_found = False
        for r in data['releases']:
            if int(release_version) == r['name']:
                rollback_found = True

        if rollback_found:
            run_symlinks(cwd, release_version)
            print("Release rolled back to {}.".format(str(release_version)))


def cleanup_releases(cwd, keep_releases):
    print("Releases cleanup...")
    releases = []
    with open(cwd + '/.dep/releases.json') as json_file:
        data = json.load(json_file)
        for r in data['releases']:
            releases.append(int(r['name']))

    keep_releases = releases[-keep_releases:]
    take_first = len(releases) - len(keep_releases)
    delete_releases = releases[0:take_first]
    data['releases'] = []
    for new_r in keep_releases:
        data['releases'].append({
            'name': int(new_r)
        })

    with open(cwd + '/.dep/releases.json', "w") as outfile:
        json.dump(data, outfile)

    for delete_release in delete_releases:
        release_path = cwd + '/releases/' + str(delete_release)
        clean_dir(release_path)
        run_command("rm -rf " + release_path)
        print("Release {} removed.".format(release_path))



