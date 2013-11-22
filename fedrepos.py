#!/usr/bin/python

# Copyright 2013 Red Hat, Inc.

DEFAULT_MIRRORLIST = 'https://mirrors.fedoraproject.org/metalink'

'''A tool to consistently update all fedora yum repositories to use a single
source'''

def main():
    # Parse the command line
    import argparse
    import sys

    parser = argparse.ArgumentParser(
        prog=u'fedrepos',
        description=u'''
A tool to update all Fedora yum repositories to use a single source.
'''
    )
    subparsers = parser.add_subparsers(title=u'actions')

    parser_baseurl = subparsers.add_parser(u'baseurl',
                                           help=u'Use a specific baseurl')
    parser_baseurl.add_argument(u'url')
    parser_baseurl.set_defaults(handler=baseurl)

    parser_mirrorlist = subparsers.add_parser(u'mirrorlist',
                                              help=u'Use a specific mirrorlist')
    parser_mirrorlist.add_argument(u'url')
    parser_mirrorlist.set_defaults(handler=mirrorlist)

    parser_default = subparsers.add_parser(u'default',
                                           help=u'Reset repos to the default')
    parser_default.set_defaults(handler=default)

    args = parser.parse_args()
    sys.exit(args.handler(args))

# Argument handlers
def baseurl(args):
    return update_repos(u'baseurl', args.url)

def mirrorlist(args):
    return update_repos(u'mirrorlist', args.url)

def default(args):
    return update_repos(u'mirrorlist', DEFAULT_MIRRORLIST)

def update_repos(method, url):
    from itertools import imap, product

    import augeas
    import re

    # Consistency? We've heard of it
    # The first entry is the location of repo relative to a Fedora mirror
    # The second entry is the name of the repo to be passed to a mirrorlist
    repos = {
        u'fedora': (
            'releases/$releasever/Everything/$basearch/os/',
            'fedora-$releasever'
        ),
        u'fedora-debuginfo': (
            'releases/$releasever/Everything/$basearch/debug/',
            'fedora-debug-$releasever'
        ),
        u'fedora-source': (
            'releases/$releasever/Everything/source/SRPMS/',
            'fedora-source-$releasever'
        ),
        u'updates': (
            'updates/$releasever/$basearch/',
            'updates-released-f$releasever'
        ),
        u'updates-debuginfo': (
            'updates/$releasever/$basearch/debug/',
            'updates-released-debug-f$releasever'
        ),
        u'updates-source': (
            'fedora/updates/$releasever/SRPMS/',
            'updates-released-source-f$releasever'
        ),
        u'updates-testing': (
            'updates/testing/$releasever/$basearch/',
            'updates-testing-f$releasever'
        ),
        u'updates-testing-debuginfo': (
            'updates/testing/$releasever/$basearch/debug/',
            'updates-testing-debug-f$releasever'
        ),
        u'updates-testing-source': (
            'updates/testing/$releasever/SRPMS/',
            'updates-testing-source-f$releasever'
        )
    }

    aug = augeas.Augeas()

    if method == u'baseurl' and not url.endswith('/'):
        url = url + '/'

    for repo in aug.match('/files/etc/yum.repos.d/*/*'):
        def reponame(x):
            m = re.search('\/([^/]+)$', x)
            return m.group(1)

        name = reponame(repo)
        if name not in repos:
            continue

        if method == u'baseurl':
            aug.set(repo + '/baseurl', url + repos[name][0])
            aug.remove(repo + '/mirrorlist')
        else:
            mirrorlist = url + '?repo={name}&arch=$basearch'.format(name=repos[name][1])

            aug.remove(repo + '/baseurl')
            aug.set(repo + '/mirrorlist', mirrorlist)

    aug.save()

    return 0

if __name__ == '__main__':
    main()
