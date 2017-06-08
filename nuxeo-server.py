import argparse
import os
import sys
import urllib2
import zipfile

parser = argparse.ArgumentParser()
parser.add_argument('command', nargs='?')
parser.add_argument('args', nargs='*')
args = parser.parse_args()


def download(url, path):
    response = urllib2.urlopen(url)
    file_object = open(path, 'wb')
    meta = response.info()
    file_size = int(meta.getheaders('Content-Length')[0])
    message = 'Downloading (%s MB) ' % (file_size / 1024 / 1024)
    file_size_downloaded = 0
    block_size = 8192
    while True:
        read_buffer = response.read(block_size)
        status = message
        if not read_buffer:
            print status
            break
        file_size_downloaded += len(read_buffer)
        file_object.write(read_buffer)
        status += '%3.2f%%' % (file_size_downloaded * 100. / file_size)
        status += chr(8) * (len(status) + 1)
        sys.stdout.write(status)
    file_object.close()


def unzip(path_zip, path_content):
    print('Extracting...')
    zip_object = zipfile.ZipFile(os.path.abspath(path_zip), 'r')
    zip_object.extractall()
    zip_object.close()
    original_path = os.path.abspath(zip_object.namelist()[0])
    os.rename(original_path, path_content)
    print('  ' + os.path.abspath(path_content))


def delete_file(path):
    os.remove(path)


def make_executable(path):
    nuxeoctl_path = path + '/bin/nuxeoctl'
    print('Making nuxeoctl executable...')
    os.system('chmod a+x ' + nuxeoctl_path)
    print('  ' + os.path.abspath(nuxeoctl_path))


def setup_cors(path):
    file_directory_path = path + '/nxserver/config/'
    file_path = file_directory_path + 'cors-config.xml'
    print('Setting up CORS configuration...')
    if not os.path.exists(file_directory_path):
        os.makedirs(file_directory_path)
    s = '<component name="org.nuxeo.corsi.demo">\n'
    s += '  <extension target="org.nuxeo.ecm.platform.web.common.requestcontroller.service.RequestControllerService"'
    s += ' point="corsConfig">\n'
    s += '    <corsConfig name="foobar" supportedMethods="GET,POST,HEAD,OPTIONS,DELETE,PUT"'
    s += ' exposedHeaders="Accept-Ranges,Content-Range,Content-Encoding,Content-Length">\n'
    s += '      <pattern>/nuxeo/.*</pattern>\n'
    s += '    </corsConfig>\n'
    s += '  </extension>\n'
    s += '</component>\n'
    file_object = open(file_path, 'a')
    file_object.write(s)
    file_object.close()
    print('  ' + os.path.abspath(file_path))


def register(path):
    if os.path.isfile('instance.clid'):
        print('Registering instance with the provided instance.clid file...')
        os.system('cp instance.clid ' + path + '/nxserver/data/')
        print('  ' + os.path.abspath('instance.clid'))
    else:
        print('No instance.clid file found')
        print('Registering instance using nuxeoctl')
        os.system('./' + path + '/bin/nuxeoctl register')


def enable_debug(path):
    print('Enabling debug flags...')
    conf_path = path + '/bin/nuxeo.conf'
    conf = open(conf_path, 'r')
    ls = []
    for line in conf.readlines():
        if line == '#org.nuxeo.dev=true\n':
            ls.append('org.nuxeo.dev=true\n')
        elif line == '#JAVA_OPTS=$JAVA_OPTS -Xdebug -Xrunjdwp:transport=dt_socket,address=8787,server=y,suspend=n\n':
            ls.append('JAVA_OPTS=$JAVA_OPTS -Xdebug -Xrunjdwp:transport=dt_socket,address=8787,server=y,suspend=n\n')
        else:
            ls.append(line)
    conf.close()
    conf = open(conf_path, 'w')
    conf.writelines(ls)
    conf.close()
    print('  ' + os.path.abspath(conf_path))


def install_package(path, package):
    print('Installing %s marketplace package...' % package)
    os.system('./' + path + '/bin/nuxeoctl mp-install ' + package)


def user_accepts(message):
    response = raw_input(message)
    return response == '' or response.lower() == 'y'

if args.command == 'download':
    download(args.args[0], args.args[1])

if args.command == 'unzip':
    unzip(args.args[0], args.args[1])

if args.command == 'delete-file':
    delete_file(args.args[0])

if args.command == 'make-executable':
    make_executable(args.args[0])

if args.command == 'setup-cors':
    setup_cors(args.args[0])

if args.command == 'register':
    register(args.args[0])

if args.command == 'enable-debug':
    enable_debug(args.args[0])

if args.command == 'install-package':
    install_package(args.args[0], args.args[1])

if args.command is None:

    server_path = raw_input('Server directory name (or full path): ')
    if server_path == '':
        print('Invalid value')
        sys.exit(0)
    print('[1] Download server zip from URL')
    print('[2] Use a local server zip file')
    answer = int(raw_input('Select the server file source: '))
    if answer == 2:
        answer = raw_input('Path to the local server zip file: ')
        unzip(answer, server_path)
    else:
        answer = raw_input('Server zip URL: ')
        download(answer, 'tmp')
        unzip('tmp', server_path)
        delete_file('tmp')
    make_executable(server_path)
    if user_accepts('Setup CORS? [y] '):
        setup_cors(server_path)
    if user_accepts('Register instance? [y] '):
        register(server_path)
    if user_accepts('Enable debug flags? [y] '):
        enable_debug(server_path)
    if user_accepts('Install nuxeo-jsf-ui marketplace package? [y] '):
        install_package(server_path, 'nuxeo-jsf-ui')
    if user_accepts('Install nuxeo-web-ui marketplace package? [y] '):
        install_package(server_path, 'nuxeo-web-ui')
