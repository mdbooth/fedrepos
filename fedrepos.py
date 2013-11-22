#!/usr/bin/python

# Copyright 2013 Red Hat, Inc.

DEFAULT_METALINK = 'https://mirrors.fedoraproject.org/metalink'

'''A tool to consistently update all fedora yum repositories to use a single
source'''

DEVEL=u'devel'
RAWHIDE=u'rawhide'

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

    # Proxy arguments
    parser.add_argument('--proxy', '-p',
                        help='URL of a proxy to be used by all repos')
    parser.add_argument('--proxy_username',
                        help='Username for proxy authentication')
    parser.add_argument('--proxy_password',
                        help='Password for proxy authentication')

    # Development or rawhide
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument('--devel',
                      action='store_true',
                      help='Specify that the current release is in development')
    mode.add_argument('--rawhide',
                      action='store_true',
                      help='Use the rawhide repositories')

    # Actions
    subparsers = parser.add_subparsers(title=u'actions')

    parser_baseurl = subparsers.add_parser(u'baseurl',
                                           help=u'Use a specific baseurl')
    parser_baseurl.add_argument(u'url')
    parser_baseurl.set_defaults(handler=baseurl)

    parser_mirrorlist = subparsers.add_parser(u'mirrorlist',
                                              help=u'Use a specific mirrorlist')
    parser_mirrorlist.add_argument(u'url')
    parser_mirrorlist.set_defaults(handler=mirrorlist)

    parser_metalink = subparsers.add_parser(u'metalink',
                                            help=u'Use a specific metalink')
    parser_metalink.add_argument(u'url')
    parser_metalink.set_defaults(handler=metalink)

    parser_default = subparsers.add_parser(u'default',
                                           help=u'Reset repos to the default.')
    parser_default.set_defaults(handler=default)

    args = parser.parse_args()
    sys.exit(args.handler(args))

def marshal_proxy(args):
    if args.proxy is None:
        return None

    return {
        u'url': args.proxy,
        u'username': args.proxy_username,
        u'password': args.proxy_password
    }

def marshal_mode(args):
    if args.devel:
        return DEVEL
    if args.rawhide:
        return RAWHIDE
    return None

# Argument handlers
def baseurl(args):
    return update_repos(u'baseurl', args.url,
                        marshal_mode(args), marshal_proxy(args))

def mirrorlist(args):
    return update_repos(u'mirrorlist', args.url,
                        marshal_mode(args), marshal_proxy(args))

def metalink(args):
    return update_repos(u'metalink', args.url,
                        marshal_mode(args), marshal_proxy(args))

def default(args):
    return update_repos(u'metalink', DEFAULT_METALINK,
                        marshal_mode(args), marshal_proxy(args))

def update_repos(method, url, mode, proxy):
    from itertools import imap, product

    import augeas
    import re

    # Consistency? We've heard of it
    # The first entry is the location of repo relative to a Fedora mirror.
    #   It contains urls for released, development and rawhide
    # The second entry is the name of the repo to be passed to a metalink
    #   It contains names for released and rawhide
    repos = {
        u'fedora': (
            (
                'releases/$releasever/Everything/$basearch/os/',
                'development/$releasever/$basearch/os/',
                'development/rawhide/$basearch/os/'
            ),
            (
                'fedora-$releasever',
                'rawhide'
            )
        ),
        u'fedora-debuginfo': (
            (
                'releases/$releasever/Everything/$basearch/debug/',
                'development/$releasever/$basearch/debug/',
                'development/rawhide/$basearch/debug/'
            ),
            (
                'fedora-debug-$releasever',
                'rawhide-debug'
            )
        ),
        u'fedora-source': (
            (
                'releases/$releasever/Everything/source/SRPMS/',
                'development/$releasever/source/SRPMS/',
                'development/rawhide/source/SRPMS/',
            ),
            (
                'fedora-source-$releasever',
                'rawhide-source'
            )
        ),
        u'updates': (
            ('updates/$releasever/$basearch/',),
            ('updates-released-f$releasever',)
        ),
        u'updates-debuginfo': (
            ('updates/$releasever/$basearch/debug/',),
            ('updates-released-debug-f$releasever',)
        ),
        u'updates-source': (
            ('updates/$releasever/SRPMS/',),
            ('updates-released-source-f$releasever',)
        ),
        u'updates-testing': (
            ('updates/testing/$releasever/$basearch/',),
            ('updates-testing-f$releasever',)
        ),
        u'updates-testing-debuginfo': (
            ('updates/testing/$releasever/$basearch/debug/',),
            ('updates-testing-debug-f$releasever',)
        ),
        u'updates-testing-source': (
            ('updates/testing/$releasever/SRPMS/',),
            ('updates-testing-source-f$releasever',)
        )
    }

    aug = augeas.Augeas()

    if method == u'baseurl' and not url.endswith('/'):
        url = url + '/'

    for repo in aug.match('/files/etc/yum.repos.d/*/*'):
        def reponame(x):
            m = re.search('\/([^/]+)$', x)
            return m.group(1)

        # Only touch Fedora repos
        name = reponame(repo)
        if name not in repos:
            continue

        if proxy is None:
            aug.remove(repo + '/proxy')
            aug.remove(repo + '/proxy_username')
            aug.remove(repo + '/proxy_password')
        else:
            aug.set(repo + '/proxy', proxy[u'url'])
            if proxy[u'username'] is not None:
                aug.set(repo + '/proxy_username', proxy[u'username'])
            else:
                aug.remove(repo + '/proxy_username')
            if proxy[u'password'] is not None:
                aug.set(repo + '/proxy_password', proxy[u'password'])
            else:
                aug.remove(repo + '/proxy_password')

        if method == u'baseurl':
            urls = repos[name][0]
            if mode is None or len(urls) == 1:
                baseurl = urls[0]
            elif mode == DEVEL:
                baseurl = urls[1]
            else:
                baseurl = urls[2]

            aug.set(repo + '/baseurl', url + baseurl)
            aug.remove(repo + '/mirrorlist')
            aug.remove(repo + '/metalink')
        else:
            names = repos[name][1]
            if mode is None or len(names) == 1 or mode == DEVEL:
                name = names[0]
            else:
                name = names[1]

            query = '?repo={name}&arch=$basearch'.format(name=name)

            aug.remove(repo + '/baseurl')
            if method == u'mirrorlist':
                aug.set(repo + '/mirrorlink', url + query)
                aug.remove(repo + '/metalink')
            else:
                aug.remove(repo + '/mirrorlist')
                aug.set(repo + '/metalink', url + query)

    aug.save()

    return 0

if __name__ == '__main__':
    main()
