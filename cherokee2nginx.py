#!/usr/bin/env python
# vim: set fileencoding=utf-8 :

# Copyright © 2014 - Stefan Talpalaru <stefantalpalaru@yahoo.com>

# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

import argparse
import sys
import os
from pprint import pprint
import datetime
import multiprocessing


### args
parser = argparse.ArgumentParser(description='Convert a Cherokee configuration file to its Nginx equivalent.', formatter_class=argparse.ArgumentDefaultsHelpFormatter)
parser.add_argument('infile', help='cherokee.conf', default=argparse.SUPPRESS, metavar='<in_file>')
parser.add_argument('outfile', help='nginx.conf (will be overwritten)', default=argparse.SUPPRESS, metavar='<out_file>', type=argparse.FileType('w'))
parser.add_argument('--cherokee-admin-path', help='path to the Cherokee admin directory', default='/usr/share/cherokee/admin', metavar='<dir>')
parser.add_argument('-v', '--verbose', help='increase output verbosity', action='store_true')
args = parser.parse_args()

sys.path.insert(0, os.path.join(args.cherokee_admin_path, 'CTK'))
from CTK import Config

cfg = Config(args.infile)

class DictNoNone(dict):
    def __init__(self, iterable=(), **kwargs):
        for k, v in iterable:
            if v is not None: self[k] = v
        for k, v in kwargs.iteritems():
            if v is not None: self[k] = v
    def __setitem__(self, key, value):
        if key in self or value is not None:
            dict.__setitem__(self, key, value)

data = DictNoNone([
    ['ports', []],
    ['vservers', DictNoNone()],
    ['sources', DictNoNone()],
    ['user', cfg.get_val('server!user')],
    ['group', cfg.get_val('server!group')],
])

for n in cfg.keys('server!bind'):
    data['ports'].append(DictNoNone([
        ['port', int(cfg.get_val('server!bind!%s!port' % n))],
        ['tls', int(cfg.get_val('server!bind!%s!tls' % n))],
    ]))

server_tokens = cfg.get_val('server!server_tokens')
if server_tokens == 'product':
    data['server_tokens'] = 'off'

for vserver_n in cfg.keys('vserver'):
    data['vservers'][int(vserver_n)] = DictNoNone([
        ['nick', cfg.get_val('vserver!%s!nick' % vserver_n)],
        ['match', cfg.get_val('vserver!%s!match' % vserver_n)],
        ['match_domain_1', cfg.get_val('vserver!%s!match!domain!1' % vserver_n)],
        ['directory_index', cfg.get_val('vserver!%s!directory_index' % vserver_n)],
        ['document_root', cfg.get_val('vserver!%s!document_root' % vserver_n)],
        ['ssl_certificate_file', cfg.get_val('vserver!%s!ssl_certificate_file' % vserver_n)],
        ['ssl_certificate_key_file', cfg.get_val('vserver!%s!ssl_certificate_key_file' % vserver_n)],
        ['disabled', cfg.get_val('vserver!%s!disabled' % vserver_n)],
        ['rules', DictNoNone()],
    ])
    for rule_n in cfg.keys('vserver!%s!rule' % vserver_n):
        data['vservers'][int(vserver_n)]['rules'][int(rule_n)] = DictNoNone([
            ['disabled', cfg.get_val('vserver!%s!rule!%s!disabled' % (vserver_n, rule_n))],
            ['expiration', cfg.get_val('vserver!%s!rule!%s!expiration' % (vserver_n, rule_n))],
            ['expiration_time', cfg.get_val('vserver!%s!rule!%s!expiration!time' % (vserver_n, rule_n))],
            ['handler', cfg.get_val('vserver!%s!rule!%s!handler' % (vserver_n, rule_n))],
            ['handler_error', cfg.get_val('vserver!%s!rule!%s!handler!error' % (vserver_n, rule_n))],
            ['document_root', cfg.get_val('vserver!%s!rule!%s!document_root' % (vserver_n, rule_n))],
            ['match', cfg.get_val('vserver!%s!rule!%s!match' % (vserver_n, rule_n))],
            ['match_directory', cfg.get_val('vserver!%s!rule!%s!match!directory' % (vserver_n, rule_n))],
            ['match_extensions', cfg.get_val('vserver!%s!rule!%s!match!extensions' % (vserver_n, rule_n))],
            ['match_request', cfg.get_val('vserver!%s!rule!%s!match!request' % (vserver_n, rule_n))],
            ['match_fullpath_1', cfg.get_val('vserver!%s!rule!%s!match!fullpath!1' % (vserver_n, rule_n))],
            ['match_left', cfg.get_val('vserver!%s!rule!%s!match!left' % (vserver_n, rule_n))],
            ['match_left_directory', cfg.get_val('vserver!%s!rule!%s!match!left!directory' % (vserver_n, rule_n))],
            ['match_left_extensions', cfg.get_val('vserver!%s!rule!%s!match!left!extensions' % (vserver_n, rule_n))],
            ['match_right', cfg.get_val('vserver!%s!rule!%s!match!right' % (vserver_n, rule_n))],
            ['match_right_directory', cfg.get_val('vserver!%s!rule!%s!match!right!directory' % (vserver_n, rule_n))],
            ['match_right_extensions', cfg.get_val('vserver!%s!rule!%s!match!right!extensions' % (vserver_n, rule_n))],
        ])
        sources = cfg.keys('vserver!%s!rule!%s!handler!balancer!source' % (vserver_n, rule_n))
        if sources:
            data['vservers'][int(vserver_n)]['rules'][int(rule_n)]['sources'] = DictNoNone()
            for source_n in sources:
                data['vservers'][int(vserver_n)]['rules'][int(rule_n)]['sources'][int(source_n)] = int(cfg.get_val('vserver!%s!rule!%s!handler!balancer!source!%s' % (vserver_n, rule_n, source_n)))
        rewrites = cfg.keys('vserver!%s!rule!%s!handler!rewrite' % (vserver_n, rule_n))
        if rewrites:
            data['vservers'][int(vserver_n)]['rules'][int(rule_n)]['rewrites'] = DictNoNone()
            for rewrite_n in rewrites:
                data['vservers'][int(vserver_n)]['rules'][int(rule_n)]['rewrites'][int(rewrite_n)] = DictNoNone([
                    ['regex', cfg.get_val('vserver!%s!rule!%s!handler!rewrite!%s!regex' % (vserver_n, rule_n, rewrite_n))],
                    ['substring', cfg.get_val('vserver!%s!rule!%s!handler!rewrite!%s!substring' % (vserver_n, rule_n, rewrite_n))],
                ])

        # remove rules we don't need
        if data['vservers'][int(vserver_n)]['rules'][int(rule_n)].get('match_directory') in ['/cherokee_icons', '/cherokee_themes'] or \
           data['vservers'][int(vserver_n)]['rules'][int(rule_n)].get('disabled') == '1' or \
           data['vservers'][int(vserver_n)]['rules'][int(rule_n)].get('handler') == 'server_info':
            del data['vservers'][int(vserver_n)]['rules'][int(rule_n)]
    # remove vservers we don't need
    if data['vservers'][int(vserver_n)].get('disabled') == '1':
        del data['vservers'][int(vserver_n)]

for source_n in cfg.keys('source'):
    data['sources'][int(source_n)] = DictNoNone([
        ['nick', cfg.get_val('source!%s!nick' % source_n)],
        ['type', cfg.get_val('source!%s!type' % source_n)],
        ['host', cfg.get_val('source!%s!host' % source_n)],
        ['interpreter', cfg.get_val('source!%s!interpreter' % source_n)],
    ])

if args.verbose:
    pprint(data)

prog_name = sys.argv[0].split('/')[-1]
args.outfile.write('# automatically generated by %s on %s\n\n' % (prog_name, datetime.datetime.now()))

if 'user' in data:
    args.outfile.write('user %s' % data['user'])
if 'group' in data:
    args.outfile.write(' %s' % data['group'])
args.outfile.write(';\n')

args.outfile.write('worker_processes %d;\n' % multiprocessing.cpu_count())

args.outfile.write('error_log /var/log/nginx/error_log notice;\n')

args.outfile.write("""
worker_rlimit_nofile 4096;
events {
    worker_connections 2048;
}
""")

args.outfile.write("""
http {
    include /etc/nginx/mime.types;
    default_type application/octet-stream;

    client_header_timeout 10m;
    client_body_timeout 10m;
    send_timeout 10m;

    connection_pool_size 256;
    client_header_buffer_size 1k;
    large_client_header_buffers 4 2k;
    client_body_buffer_size 1m;
    request_pool_size 4k;
    client_max_body_size 200m;
    fastcgi_buffers 256 16k;
    proxy_buffers 256 16k;

    gzip on;
    gzip_min_length 1100;
    gzip_buffers 4 8k;
    gzip_types text/plain text/css application/x-javascript text/xml application/xml application/xml+rss text/javascript application/json text/csv;

    output_buffers 1 32k;
    postpone_output 1460;

    sendfile on;
    tcp_nopush on;
    tcp_nodelay on;

    keepalive_timeout 75 20;

    ignore_invalid_headers on;

    index index.php index.htm index.html;

""")

source_groups = []
for vserver_n, vserver in data['vservers'].items():
    if 'rules' in vserver:
        for rule_n in vserver['rules']:
            if 'sources' in vserver['rules'][rule_n]:
                source_group = sorted(vserver['rules'][rule_n]['sources'].values())
                if source_group not in source_groups:
                    source_groups.append(source_group)
for i, source_group in enumerate(source_groups):
    args.outfile.write("""
    upstream upstream-%d {
""" % i)
    for source_n in source_group:
        host = data['sources'][source_n]['host']
        if host.startswith('/'):
            host = 'unix:' + host
        args.outfile.write('        # %s;\n' % data['sources'][source_n]['nick'])
        args.outfile.write('        server %s;\n' % host)
    args.outfile.write('    }\n') # end 'upstream' section

for vserver_n in sorted(data['vservers'].keys(), reverse=True):
    vserver = data['vservers'][vserver_n]
    args.outfile.write('\n    server {\n')
    
    # listen
    nick = vserver['nick']
    for port in data['ports']:
        writing_it = False
        if not port['tls']:
            writing_it = True
            args.outfile.write('        listen %d' % port['port'])
        elif 'ssl_certificate_file' in vserver:
            writing_it = True
            args.outfile.write('        listen %d ssl' % port['port'])
        if writing_it:
            if nick == 'default':
                args.outfile.write(' default_server')
            args.outfile.write(';\n')
    
    # server_name
    if nick == 'default':
        args.outfile.write('        server_name _;\n')
    else:
        args.outfile.write('        server_name %s;\n' % nick)

    # SSL certificate
    if 'ssl_certificate_file' in vserver:
        args.outfile.write('\n        ssl_certificate %s;\n' % vserver['ssl_certificate_file'])
    if 'ssl_certificate_key_file' in vserver:
        args.outfile.write('        ssl_certificate_key %s;\n' % vserver['ssl_certificate_key_file'])

    # logs
    args.outfile.write("""
        access_log /var/log/nginx/%s.access_log combined;
        error_log /var/log/nginx/%s.error_log notice;
""" % (nick, nick))

    # root
    args.outfile.write('\n        root %s;\n' % vserver['document_root'])

    # location
    for rule_n, rule in sorted(vserver['rules'].items(), key=lambda x: x[0], reverse=True):
        location = ''
        if rule['match'] == 'default' and rule['handler'] != 'common':
            location = '/'
        elif rule['match'] == 'directory':
            location = rule['match_directory']
        elif rule['match'] == 'fullpath':
            location = rule['match_fullpath_1']
        elif rule['match'] == 'request':
            location = '~* %s' % rule['match_request']
        elif rule['match'] == 'extensions':
            location = '~* \.%s$' % rule['match_extensions']
        elif rule['match'] == 'and':
            directory = ''
            extensions = ''
            for term in ['left', 'right']:
                key = 'match_%s_directory' % term
                if key in rule:
                    directory = rule[key]
                key = 'match_%s_extensions' % term
                if key in rule:
                    extensions = rule[key]
            if len(directory) and len(extensions):
                location = '~* ^%s.*\.%s$' % (directory, extensions)
        elif rule['match'] == 'or':
            if 'match_left_directory' in rule and 'match_right_directory' in rule:
                location = '~* (%s|%s)' % (rule['match_left_directory'], rule['match_right_directory'])
        
        if len(location):
            args.outfile.write("""
        location %s {
""" % location)

            if 'expiration_time' in rule:
                args.outfile.write('            expires %s;\n' % rule['expiration_time'])

            if 'document_root' in rule:
                args.outfile.write('            root %s;\n' % rule['document_root'])
            
            # handler
            if rule['handler'] == 'fcgi':
                source_group = sorted(rule['sources'].values())
                upstream = 'upstream-%d' % source_groups.index(source_group)
                args.outfile.write('            include fastcgi_params;\n')
                args.outfile.write('            fastcgi_pass %s;\n' % upstream)
            elif rule['handler'] == 'proxy':
                source_group = sorted(rule['sources'].values())
                upstream = 'upstream-%d' % source_groups.index(source_group)
                args.outfile.write('            proxy_set_header Host $http_host;\n')
                args.outfile.write('            proxy_read_timeout 5m;\n')
                args.outfile.write('            proxy_pass http://%s;\n' % upstream)
            elif rule['handler'] == 'redir':
                for rewrite_n in sorted(rule['rewrites'].keys(), reverse=True):
                    rewrite = rule['rewrites'][rewrite_n]
                    if rule['match'] == 'fullpath':
                        rewrite['regex'] = '^%s$' % rule['match_fullpath_1']
                    args.outfile.write('            rewrite %s %s last;\n' % (rewrite['regex'], rewrite['substring']))
            elif rule['handler'] == 'custom_error':
                args.outfile.write('            return %s;\n' % rule['handler_error'])
            
            args.outfile.write('        }\n') # end 'location' section

    args.outfile.write('    }\n') # end 'server' section


args.outfile.write('}\n\n') # end 'http' section

