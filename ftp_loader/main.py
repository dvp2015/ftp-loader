# -*- coding: utf-8 -*-

import argparse
import getpass
from pysftp import Connection

from . import loader


def read_config(config_file):
    url, path, files = loader.load_config(config_file)
    file_trans = loader.create_file_transfers(path, files)
    return url, file_trans

def auth(url):
    print('Please, enter your login and password to access FTP server. \n')
    user = input('Username: ')
    passwd = getpass.getpass('Password: ')
    return user, passwd


def download_data(url, file_trans, skip_existing):
    print('Start downloading project data from {0}'.format(url))
    user, passwd = auth(url)

    downloaded = []
    with Connection(url, user, password=passwd) as conn:
        for ft in file_trans:
            try:
                ft.download(conn, skip_existing)
                downloaded.append(ft)
            except loader.LoaderException as e:
                print(e.message)
        print('Finished. {0} files were loaded.\n'.format(len(downloaded)))
    return downloaded


def upload_data(url, file_trans, skip_existing):
    print('Start uploading project data to {0}'.format(url))
    user, passwd = auth(url)

    with Connection(url, user, password=passwd) as conn:
        count = 0
        for ft in file_trans:
            try: 
                ft.upload(conn, skip_existing)
                count += 1
            except loader.LoaderException as e:
                print(e.message)
        print('Finished. {0} files were uploaded.\n'.format(count))


def decompress_data(file_trans, skip_existing):
    for ft in file_trans:
        try:
            ft.decompress(skip_existing)
        except loader.LoaderException as e:
            print(e.message)


def compress_data(file_trans, skip_existing):
    for ft in file_trans:
        try:
            ft.compress(skip_existing)
        except loader.LoaderException as e:
            print(e.message)            


def clear_data(file_trans):
    confirm = input('Are you sure to remove all files? Y or N: ')
    if confirm.upper() == 'Y':
        for ft in file_trans:
            ft.clear()
    else:
        print('Aborting ...')


def arg_parser():
    parser = argparse.ArgumentParser(prog='FTP Loader')

    parser.add_argument(
        'config', type=str, nargs='?', default='ftp-config.toml',
        help='configuration file name.'
    )

    parser.add_argument(
        '--upload', action='store_true', help='Upload files to FTP.'
    )
    parser.add_argument(
        '--overwrite', action='store_true', help='To overwrite files.'
    )
    parser.add_argument(
        '--clear', action='store_true', help='Removes local data files'
    )

    args = parser.parse_args()
    return dict(vars(args))


def main():
    args = arg_parser()
    try:
        url, file_trans = read_config(args['config'])
    except FileNotFoundError:
        print('There is no configuration file {0}. Aborting...'.format(args['config']))

    skip_existing = not args['overwrite']
    if args['clear']:
        clear_data(file_trans)
    elif args['upload']:
        compress_data(file_trans, skip_existing)
        upload_data(url, file_trans, skip_existing)
    else:
        downloaded = download_data(url, file_trans, skip_existing)
        decompress_data(downloaded, skip_existing)
    print('Done. \n')
