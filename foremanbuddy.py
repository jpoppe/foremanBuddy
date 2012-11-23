#!/usr/bin/env python

# Copyright 2012 Jasper Poppe <jgpoppe@gmail.com>
# Copyright 2012 eBuddy (http://www.eBuddy.com)
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#    http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


__author__ = 'Jasper Poppe <jgpoppe@gmail.com>'
__copyright__ = 'Copyright (c) 2012 Jasper Poppe/eBuddy'
__credits__ = ''
__license__ = 'Apache License, Version 2.0'
__version__ = '0.8.0 beta'
__maintainer__ = 'Jasper Poppe'
__email__ = 'jgpoppe@gmail.com'
__status__ = 'beta'

import argparse
import base64
import ConfigParser
import operator
import os
import pprint
import sys
import json
import urllib2

from argparse import RawTextHelpFormatter
from itertools import imap

config_file_home = os.path.join(os.path.expanduser('~'), '.foremanbuddy.cfg')
if os.path.isfile(config_file_home):
    config_file = config_file_home
elif os.path.isfile('/etc/foremanbuddy/foremanbuddy.cfg'):
    config_file = '/etc/foremanbuddy/foremanbuddy.cfg'
else:
    config_file = 'foremanbuddy.cfg'

config = ConfigParser.RawConfigParser()
config.read(config_file)
FOREMAN_URL = config.get('Foreman', 'url')
FOREMAN_USER = config.get('Foreman', 'user')
FOREMAN_PASSWORD = config.get('Foreman', 'password')
IGNORE_SYSTEM_PROXY = config.getboolean('System', 'ignore_proxy')
DEBUG = config.getboolean('System', 'debug')


class HostObject:

    def __init__(self):
        """initialize object variables"""
        self.architecture_id = None
        self.build = None
        self.comment = None
        self.disk = None
        self.domain_id = None
        self.enabled = None
        self.environment = None
        self.environment_id = None
        self.hostgroup_id = None
        self.installed_at = None
        self.ip = None
        self.last_compile = None
        self.last_freshcheck = None
        self.last_report = None
        self.mac = None
        self.medium_id = None
        self.model_id = None
        self.name = None
        self.operatingsystem_id = None
        self.owner_id = None
        self.owner_type = None
        self.ptable_id = None
        self.puppet_status = None
        self.puppet_proxy_id = None
        self.puppet_ca_proxy_id = None
        self.root_pass = None
        self.serial = None
        self.source_file_id = None
        self.sp_ip = None
        self.sp_mac = None
        self.sp_name = None
        self.sp_subnet_id = None
        self.subnet_id = None
        self.compute_resource_id = None


class HostComputeObject:
    
    def __init__(self):
        """initialize object variables"""
        self.cpus = None
        self.capacity = None
        self.memory = None
        self.start = None
        self.pool_name = None
        self.format_type = None
        self.bridge = None


class HostMergedObject(HostObject, HostComputeObject):

    def __init__(self):
        """initialize object variables"""
        HostObject.__init__(self)
        HostComputeObject.__init__(self)


class DomainObject:

    def __init__(self):
        """initialize object variables"""
        self.name = None
        self.fullname = None
        self.dns_id = None


class PTableObject:

    def __init__(self):
        """initialize object variables"""
        self.name = None
        self.layout = None
        self.os_family = None


class TemplateObject:

    def __init__(self):
        """initialize object variables"""
        self.name = None
        self.architecture_id = None
        self.hostgroup_id = None
        self.template = None
        self.file_name = None
        self.template_kind_id = None
        self.snippet = None
        self.operatingsystem_ids = None


class SubnetObject:

    def __init__(self):
        """initialize object variables"""
        self.dhcp_id = None
        self.dns_id = None
        self.dns_primary = None
        self.dns_secondary = None
        self.ip_from = None
        self.ip_to = None
        self.gateway = None
        self.mask = None
        self.name = None
        self.network = None
        self.priority = None
        self.ranges = None
        self.tftp_id = None
        self.vlanid = None
        self.domain_ids = None


class HostGroupObject: 

    def __init__(self):
        """initialize object variables"""
        self.architecture_id = None
        self.environment_id = None
        self.medium_id = None
        self.subnet_id = None
        self.name = None
        self.operatingsystem_id = None
        self.ptable_id = None
        self.puppet_proxy_id = None
        self.root_pass = None
        self.domain_id = None
        self.hypervisor_id = None
        self.parent_id = None
        self.puppetclass_ids = None


class UserObject:

    def __init__(self):
        """initialize object variables"""
        self.admin = None
        self.auth_source_id = None
        self.domains_andor = None
        self.facts_andor = None
        self.filter_on_owner = None
        self.firstname = None
        self.hostgroups_andor = None
        self.last_login_on = None
        self.lastname = None
        self.login = None
        self.mail = None
        self.password = None
        self.role_id = None


class OperatingSystemObject:

    def __init__(self):
        """initialize object variables"""
        self.major = None
        self.minor = None
        self.name = None
        self.nameindicator = None
        self.release_name = None
        self.type = None
        self.architecture_ids = None
        self.ptable_ids = None
        self.medium_ids = None
        self.family = None
        self.pxelinux_template_id = None
        self.provision_template_id = None
        self.finish_template_id = None


class ComputeResourceObject:

    def __init__(self):
        """initialize object variables"""
        self.name = None
        self.url = None
        self.description = None
        self.provider = None


class MediaObject:

    def __init__(self):
        """initialize object variables"""
        self.name = None
        self.path = None
        self.os_family = None


class ArchitectureObject:

    def __init__(self):
        """initialize object variables"""
        self.name = None
        self.operatingsystem_ids = None


class SmartProxyObject:

    def __init__(self):
        """initialize object variables"""
        self.name = None
        self.url = None


class FormatData:

    def __clean_output(self, data):
        """convert unicode to string"""
        if len(data) == 0:
            return data
        else:
            data = data.values()[0]
            try:
                return dict([(str(key), str(value))
                    for key, value in data.items()])
            except AttributeError:
                return data

    def __indent(self, data, indent):
        """indent items in a list"""
        if indent != 0:
            indent += 2
        spaces = indent * ' '
        data = [spaces + entry for entry in data]
        return data

    def __omit_data(self, data):
        """omit less usefull data to keep output clean"""
        values = ('created_at', 'updated_at', 'template')
        for value in values:
            if value in data:
                del(data[value])
        return data

    def __print_parameters(self, key, value, align):
        """print and format foreman parameters"""
        if value:
            entry = value.pop(0)
            print('{0:{1}}: {2}').format(key, align, entry)
            value = self.__indent(value, align)
            if value:
                print('\n'.join(value))
        else:
            print('{0:{1}}:').format(key, align)

    def prettify_dict(self, data):
        """format a dictionary"""
        result = []
        if data:
            align = max(imap(len, data)) + 1
            for key, value in data.items():
                if type(value) == dict:
                    value =  self.__dict_to_line(value)
                result.append('{0:{1}}: {2}'.format(key, align, value))
        return result

    def __format(self, data):
        data = [data[item] for item in data]
        for item in data:
            if type(item) == list:
                item = {item[0]['puppetclass']['name']: item}
                #FIXME: make alignment dynamic for puppet classes
                align = 20
            else:
                align = max(imap(len, item)) + 1

            for key, value in item.items():
                if type(value) == list:
                    value = [entry.values()[0] for entry in value]
                    value = [self.__omit_data(entry) for entry in value]
                    value = [self.__dict_to_line(entry) for entry in value]
                    self.__print_parameters(key, value, align)
                elif type(value) == dict:
                    value = [entry for entry in self.prettify_dict(value)]
                    self.__print_parameters(key, value, align)
                else:
                    if type(value) == unicode and '\n' in value:
                        value = self.__indent(value.split('\n'), align)
                        value = '\n'.join(value).strip()
                        print('{0:{1}}: {2}').format(key, align, value)
                    else:
                        print('{0:{1}}: {2}').format(key, align, value)

    def pretty(self, data):
        if type(data) == list:
            for index, result in enumerate(data):
                self.__format(result)
                if index != len(data) - 1:
                    print('')
        else:
            self.__format(data)


    def __dict_to_line(self, data):
        """convert dictionary to one line string"""
        result = []
        for key, value in data.items():
            if type(value) == dict:
                result.append('%s: %s' % (key, self.__dict_to_line(value)))
            else:
                result.append('%s: %s' % (key, value))
        result = ', '.join(result)
        return result

    def __format_value(self, data):
        values = []
        for item in data:
            if type(item) == list:
                values.append(','.join(item))
            elif type(item) == dict:
                values.append(self.__dict_to_line(item))
        return values

    def pretty_list(self, data):
        align = max(imap(len, data))
        for index, result in enumerate(data):
            for key, value in result.items():
                if type(value) == list:
                    value = self.__format_value(value)
                    self.__print_parameters(key, value, align)
                elif type(value) == dict:
                    value = self.__dict_to_line(value)
                    print('{0:{1}}: {2}').format(key, align, value)
                else:
                    print('{0:{1}}: {2}').format(key, align, value)
            if index != len(data) - 1:
                print('')

    def uuids(self, data):
        names = [item['name'] for item in data]
        align = max(imap(len, names))
        for item in data:
            print('{0:{1}}: {2}').format(item['name'], align, item['uuid'])


def json_request(path, method='GET', data='', output='bare'):
    """do a json request, modify urllib2 request since it does not support
    PUT and DELETE by default"""
    url = os.path.join(FOREMAN_URL, path) + '?format=json'
    base64string = base64.encodestring('%s:%s' % (FOREMAN_USER,
        FOREMAN_PASSWORD))[:-1]

    if IGNORE_SYSTEM_PROXY:
        proxy = urllib2.ProxyHandler({})
        opener = urllib2.build_opener(urllib2.HTTPHandler, proxy)
    else:
        opener = urllib2.build_opener(urllib2.HTTPHandler)
    urllib2.install_opener(opener)
    json_data = json.dumps(data)
    if json_data:
        request = urllib2.Request(url, data=json_data)
    request.add_header('Authorization', "Basic %s" % base64string)
    request.add_header('Content-Type', 'application/json')
    request.get_method = lambda: method

    if DEBUG:
        print('debug: url "%s"' % url)
        print('debug: method "%s"' % method)
        if json_data and json_data != '""':
            print('debug: json data "%s"' % json_data)
    
    try:
        response = urllib2.urlopen(request)
    except urllib2.HTTPError as err:
        try:
            error = json.loads(err.read())
            pprint.pprint(error)
        except:
            if err.msg == 'Found':
                print('info: request has been executed successfully')
            else:
                print(err)
        sys.exit(1)
    except urllib2.URLError as err:
        print('error: could not connect to %s (%s)' % (url, err))
        sys.exit(1)

    data = response.read()
    if data == ' ':
        print('info: request has been executed successfully')
    else:
        try:
            data = json.loads(data)
        except ValueError as err:
            print('%s for URL: %s' % (err, url))
            sys.exit(1)
        else:
            return outputs(output, data)

def outputs(output, data):
    """various output formatting options"""
    if output == 'bare':
        pprint.pprint(data)
    elif output == 'object':
        return data
    elif output == 'pretty':
        format_data = FormatData()
        if not data:
            pass
        elif type(data) == dict:
            if type(data.values()[0]) == dict:
                format_data.pretty(data)
            elif 'puppetclass' in data.values()[0][0]:
                format_data.pretty(data)
            else:
                print('\n'.join(format_data.prettify_dict(data)))
        else:
            format_data.pretty(data)
    elif output == 'pretty_list':
        format_data = FormatData()
        format_data.pretty_list(data)
    elif output == 'uuids':
        format_data = FormatData()
        format_data.uuids(data)
    elif output == 'ids':
        data = [item.values()[0] for item in data]
        data.sort(key=operator.itemgetter('id'))
        indent = len(str(len(data)))
        for item in data:
            if 'login' in item:
                field = 'login'
            else:
                field = 'name'
            print('{0:{1}}: {2}'.format(item['id'], indent, item[field]))

def file_read(file_name):
    """return the contents of a file"""
    try:
        result = open(file_name, 'r').read()
    except IOError as err:
        print ('failed to read "%s" (%s)' % (file_name, err))
        sys.exit(1)
    else:
        return result

def args_to_dict(args, attrs):
    """convert argparse arguments to a python dictionary"""
    for key, value in vars(args).iteritems():
        if not key in ('func'):
            setattr(attrs, key, value)

    data = {}
    data.update((key, value[0]) for key, value in 
        attrs.__dict__.iteritems() if value)

    for key, value in data.items():
        if key.endswith('_ids'):
            data[key] = value.split(',')
    return data


class Info:
    """query various information"""

    def _query(self, args, output):
        """query information"""
        for key, value in args.__dict__.items():
            if value and key is not 'func':
                json_request(key, output=output)

    def info(self, args):
        """print resources"""
        if args.bare_output:
            output = 'bare'
            del(args.bare_output)
        else:
            output = 'pretty'
        self._query(args, output)

    def ids(self,args):
        """print ids"""
        self._query(args, 'ids')


class PTable:
    """manage partition tables"""

    def __add_modify(self, args):
        """prepare json data"""
        data = PTableObject()

        if args.string and args.file_name:
            print('error: you can not use the --string and --file_name '
                'simultaneously')
            sys.exit(1)

        if args.name:
            data.name = args.name[0]

        if args.string:
            data.layout = args.string[0]
        elif args.file_name:
            string = file_read(args.file_name[0])
            data.layout = string

        if args.os_family:
            data.os_family = args.os_family[0]
        
        json_data = {}
        json_data.update((key, value) for key, value in 
            vars(data).iteritems() if value)
        return json_data

    def add(self, args):
        """add a partition table"""
        json_data = self.__add_modify(args)
        json_request('ptables', 'POST', {'ptable': json_data})

    def modify(self, args):
        """modify a partition table"""
        json_data = self.__add_modify(args)
        path = os.path.join('ptables', args.id[0])
        json_request(path, 'PUT', {'ptable': json_data})

    def delete(self, args):
        """delete a partition table"""
        path = os.path.join('ptables', args.delete[0])
        json_request(path, 'DELETE')


class PuppetClass:
    """manage puppet classes"""

    def __add_modify(self, args):
        """prepare json data"""
        json_data = {}

        if args.name:
            json_data['name'] = args.name[0]

        if args.nameindicator:
            json_data['nameindicator'] = args.nameindicator[0]

        if args.operatingsystem_id:
            json_data['operatingsystem_id'] = args.operatingsystem_id[0]
        
        return json_data

    def modify(self, args):
        """modify a partition table"""
        json_data = self.__add_modify(args)
        path = os.path.join('puppetclasses', args.id[0])
        json_request(path, 'PUT', {'puppetclass': json_data})

    def delete(self, args):
        """delete a partition table"""
        path = os.path.join('puppetclasses', args.delete[0])
        json_request(path, 'DELETE')

    def import_env(self, args):
        """FIXME: make it work"""
        print('error: this function has not been implemented...')
        #path = 'puppetclasses/import_environments?proxy=' + args.proxy_id[0]
        #path = 'puppetclasses/obsolete_and_new?proxy=' + args.proxy_id[0]
        #json_request(path, 'GET')
        #http://overlord001.b.c.m.e:3000/puppetclasses/import_environments?proxy=1-overlord001-b-c-m-e


class Template:
    """manage templates"""

    def __add_modify(self, args):
        """prepare json data"""
        data = TemplateObject()

        if args.string and args.file_name:
            print('error: you can not use the --string and --file_name '
                'simultaneously')
            sys.exit(1)

        if args.name:
            data.name = args.name[0]

        if args.string:
            data.template = args.string[0]
        elif args.file_name:
            string = file_read(args.file_name[0])
            data.template = string

        if args.hostgroup_id:
            data.hostgroup_id = args.hostgroup_id[0]

        if args.template_kind_id:
            data.template_kind_id = args.template_kind_id[0]

        if args.snippet:
            data.snippet = True
        else:
            data.snippet = False

        if args.operatingsystem_ids:
            operatingsystem_ids = args.operatingsystem_ids[0].split(',')
            data.operatingsystem_ids = operatingsystem_ids
        
        json_data = {}
        json_data.update((key, value) for key, value in 
            vars(data).iteritems() if value)
        return json_data

    def add(self, args):
        """add a template"""
        json_data = self.__add_modify(args)
        json_request('config_templates', 'POST', {'config_template': json_data})

    def modify(self, args):
        """modify a template"""
        json_data = self.__add_modify(args)
        path = os.path.join('config_templates', args.id[0])
        json_request(path, 'PUT', {'config_template': json_data})

    def delete(self, args):
        """delete a template"""
        path = os.path.join('config_templates', args.delete[0])
        json_request(path, 'DELETE')

    def build_pxe_default(self, args):
        path = os.path.join('config_templates', 'build_pxe_default')
        json_request(path, 'GET')

class Host:
    """manage hosts"""

    def __delete_attributes(self, source, target):
        """delete overlapping class attributes"""
        for attribute in dir(source):
            if not attribute.startswith('__'):
                if attribute in target:
                    del(target[attribute])
        return target

    def info(self, args):
        """query host information"""
        if args.query:
            path = os.path.join('hosts', args.query[0])
            json_request(path, output='pretty')
        elif args.facts:
            path = os.path.join('hosts', args.facts[0], 'facts')
            json_request(path, output='pretty')
        elif args.errors:
            path = os.path.join('hosts', 'errors')
            json_request(path, output='pretty')
        elif args.active:
            path = os.path.join('hosts', 'active')
            json_request(path, output='pretty')
        elif args.out_of_sync:
            path = os.path.join('hosts', 'out_of_sync')
            json_request(path, output='pretty')
        elif args.disabled:
            path = os.path.join('hosts', 'disabled')
            json_request(path, output='pretty')
        elif args.puppetclasses:
            path = os.path.join('hosts', args.puppetclasses[0], 'puppetclasses')
            json_request(path, output='pretty')
        elif args.reports:
            path = os.path.join('hosts', args.reports[0], 'reports')
            json_request(path, output='pretty')
        elif args.report_last:
            path = os.path.join('hosts', args.report_last[0], 'reports', 'last')
            json_request(path, output='pretty')
        elif args.pxe_config:
            path = os.path.join('hosts', args.pxe_config[0], 'pxe_config')
            json_request(path, output='pretty')

    def action(self, args):
        """various host actions"""
        if args.set_build:
            path = os.path.join('hosts', args.set_build[0], 'setBuild')
            json_request(path)
        elif args.cancel_build:
            path = os.path.join('hosts', args.cancel_build[0], 'cancelBuild')
            json_request(path)

    def add(self, args):
        """add a new host"""
        data = args_to_dict(args, HostObject())
        json_request('hosts', 'POST', {'host': data})

    def compute_add(self, args):
        """add a new host"""
        data = args_to_dict(args, HostObject())
        data_compute = args_to_dict(args, HostComputeObject())

        data = self.__delete_attributes(HostComputeObject(), data)
        data_compute = self.__delete_attributes(HostObject(), data_compute)

        nics_attributes = {
            'new_nics': {
                '_delete': '', 'bridge': ''
            }, 
            '': {
                '_delete': '',
                'bridge': data_compute['bridge']
            }
        }

        volumes_attributes = {
            'new_volumes': {
                '_delete': '',
                'pool_name': 'default',
                'format_type': data_compute['format_type'],
                'capacity': data_compute['capacity']
            },
            '': {
                '_delete': '',
                'pool_name': data_compute['pool_name'],
                'format_type': data_compute['format_type'],
                'capacity': data_compute['capacity']
            }
        }

        data['compute_attributes'] = {
            'cpus': data_compute['cpus'],
            'memory': data_compute['memory'],
            'start': data_compute['start'],
            'nics_attributes': nics_attributes,
            'volumes_attributes': volumes_attributes
        }

        json_request('hosts', 'POST', {'host': data})

    def modify(self, args):
        """modify a host"""
        data = args_to_dict(args, HostObject())
        del(data['current_fqdn'])
        path = os.path.join('hosts', args.current_fqdn[0])
        json_request(path, 'PUT', {'host': data})

    def delete(self, args):
        """delete a host"""
        path = os.path.join('hosts', args.delete[0])
        json_request(path, 'DELETE')

    def add_parameter(self, args):
        """add a host parameter"""
        add_parameter(args, 'hosts', 'host', HostObject(),
            'host_parameters_attributes')

    def delete_parameter(self, args):
        """delete a host parameter"""
        delete_parameter(args, 'hosts', 'host', HostObject(),
            'host_parameters_attributes', 'host_parameter', 'host_parameters')

    def modify_parameter(self, args):
        """modify a host parameter"""
        modify_parameter(args, 'hosts', 'host', HostObject(),
            'host_parameters_attributes', 'host_parameter', 'host_parameters')


class HostGroup: 
    """manage host groups"""

    def add(self, args):
        """add a new host group"""
        data = args_to_dict(args, HostGroupObject())
        json_request('hostgroups', 'POST', {'hostgroup': data})

    def modify(self, args):
        """modify a host group"""
        data = args_to_dict(args, HostGroupObject())
        del(data['id_hostgroup'])
        path = os.path.join('hostgroups', args.id_hostgroup[0])
        json_request(path, 'PUT', {'hostgroup': data})

    def delete(self, args):
        """delete a host group"""
        path = os.path.join('hostgroups', args.delete[0])
        json_request(path, 'DELETE')

    def info(self, args):
        """show info about a host group"""
        path = os.path.join('hostgroups', args.hostgroup[0])
        json_request(path, 'GET', output='pretty')

    def add_parameter(self, args):
        """add a host group parameter"""
        add_parameter(args, 'hostgroups', 'hostgroup', HostGroupObject(),
            'group_parameters_attributes')

    def delete_parameter(self, args):
        """delete a host group parameter"""
        delete_parameter(args, 'hostgroups', 'hostgroup', HostGroupObject(),
            'group_parameters_attributes', 'group_parameter', 'group_parameters')

    def modify_parameter(self, args):
        """modify a host group parameter"""
        modify_parameter(args, 'hostgroups', 'hostgroup', HostGroupObject(),
            'group_parameters_attributes', 'group_parameter', 'group_parameters')

def _query(resource, target):
    """query resource data"""
    path = os.path.join(resource, target)
    data = json_request(path, output='object')
    return data.values()

def add_parameter(args, resource, target, class_object, attributes):
    """add a parameter"""
    if not args.key or not args.value:
        print('error: you need to specify a key and a value')
        sys.exit(1)

    data = args_to_dict(args, class_object)
    del(data['key'])
    del(data['value'])
    del(data['target'])
    data[attributes] = {'': {'name': args.key[0],
        'value': args.value[0]}}
    path = os.path.join(resource, args.target[0])
    json_request(path, 'PUT', {target: data})

def modify_parameter(args, resource, target, class_object, attributes,
    description, query):
    """modify a parameter"""
    if not args.key or not args.value:
        print('error: you need to specify a key and a value')
        sys.exit(1)

    result = _query(resource, args.target[0])
    parameters = result[0][query]
    data_attributes = {}

    for index, data in enumerate(parameters):
        del parameters[index][description]['created_at']
        del parameters[index][description]['updated_at']
        if data[description]['name'] == args.key[0]:
            parameters[index][description]['value'] = args.value[0]
        data_attributes[index] = parameters[index][description]
    
    data_attributes = {attributes: data_attributes}
    path = os.path.join(resource, args.target[0])
    json_request(path, 'PUT', {target: data_attributes})

def delete_parameter(args, resource, target, class_object, attributes,
    description, query):
    """delete a parameter"""
    if not args.key:
        print('error: you need to specify a key')
        sys.exit(1)

    data = args_to_dict(args, class_object)
    del(data['key'])
    del(data['target'])
    parameters = _query(resource, args.target[0])[0][query]
    for index, entry in enumerate(parameters):
        if entry.values()[0]['name'] == args.key[0]:
            parameters[index][description][u'_destroy'] = '1'
            data[attributes] = parameters[index]
            path = os.path.join(resource, args.target[0])
            json_request(path, 'PUT', {target: data})
            return
    print ('warning: parameter "%s" not found' % args.key[0])


class Domain:
    """manage domains"""

    def add(self, args):
        """add a domain"""
        data = args_to_dict(args, DomainObject())
        json_request('domains', 'POST', {'domain': data})

    def modify(self, args):
        """modify a domain"""
        data = args_to_dict(args, DomainObject())
        del(data['current_name'])
        path = os.path.join('domains', args.current_name[0])
        json_request(path, 'PUT', {'domain': data})

    def delete(self, args):
        """delete a domain"""
        path = os.path.join('domains', args.delete[0])
        json_request(path, 'DELETE')

    def info(self, args):
        """show info about a domain"""
        path = os.path.join('domains', args.domain[0])
        json_request(path, 'GET', output='pretty')

    def add_parameter(self, args):
        """add a domain parameter"""
        add_parameter(args, 'domains', 'domain', DomainObject(),
            'domain_parameters_attributes')

    def delete_parameter(self, args):
        """delete a domain parameter"""
        delete_parameter(args, 'domains', 'domain', DomainObject(),
            'domain_parameters_attributes', 'domain_parameter',
            'domain_parameters')

    def modify_parameter(self, args):
        """modify a domain parameter"""
        modify_parameter(args, 'domains', 'domain', DomainObject(),
            'domain_parameters_attributes', 'domain_parameter',
            'domain_parameters')


class Subnet:
    """manage subnets"""

    def __add_modify(self, args):
        """prepare json data"""
        data = args_to_dict(args, SubnetObject())
        # rename ip_from and ip_to since from is a reserved Python keyword
        if 'ip_from' in data:
            data['from'] = data['ip_from']
            del(data['ip_from'])
        if 'ip_to' in data:
            data['to'] = data['ip_to']
            del(data['ip_to'])
        return data

    def add(self, args):
        """add a new subnet"""
        data = self.__add_modify(args)
        json_request('subnets', 'POST', {'subnet': data})

    def modify(self, args):
        """modify a subnet"""
        data = self.__add_modify(args)
        path = os.path.join('subnets', args.id[0])
        json_request(path, 'PUT', {'subnet': data})


    def delete(self, args):
        """delete a subnet"""
        path = os.path.join('subnets', args.delete[0])
        json_request(path, 'DELETE')


class User:
    """manage users"""

    def __add_modify(self, args):
        """prepare json data"""
        data = args_to_dict(args, UserObject())
        if 'admin' in data:
            if data['admin'] == 'True':
                data['admin'] = True
        return data

    def add(self, args):
        """add a user"""
        data = self.__add_modify(args)
        json_request('users', 'POST', {'user': data})

    def modify(self, args):
        """modify a user"""
        data = self.__add_modify(args)
        del(data['id'])
        path = os.path.join('users', args.id[0])
        json_request(path, 'PUT', {'user': data})

    def delete(self, args):
        """delete a user"""
        path = os.path.join('users', args.delete[0])
        json_request(path, 'DELETE')


class OperatingSystem:
    """manage operating systems"""

    def __query(self, operatingsystem_id):
        """get the operatingsystem object"""
        path = os.path.join('operatingsystems', operatingsystem_id)
        data = json_request(path, output='object')
        return data.values()[0]

    def __templates(self, id_template, id_kind, count, current, attributes):
        """generate template attributes"""
        count += 1
        id_attr = ''
        if not current:
            pass
        else:
            for item in current:
                if item['os_default_template']['template_kind_id'] == id_kind:
                    id_attr = item['os_default_template']['id']
        data = {
            'template_kind_id': id_kind,
            'config_template_id': id_template,
            'id': id_attr
        }

        attributes[count] = data
        return count, attributes

    def __add_modify(self, args):
        """prepare json data"""
        data = args_to_dict(args, OperatingSystemObject())

        attributes = {}
        current = self.__query(args.id[0])['os_default_templates']
        count = -1
        if args.pxelinux_template_id:
            count, attributes = self.__templates(args.pxelinux_template_id[0],
                1, count, current, attributes)
        if args.provision_template_id:
            count, attributes = self.__templates(args.provision_template_id[0],
                3, count, current, attributes)
        if args.finish_template_id:
            count, attributes = self.__templates(args.finish_template_id[0], 4,
                count, current, attributes)
        data['os_default_templates_attributes'] = attributes

        if 'pxelinux_template_id' in data:
            del(data['pxelinux_template_id'])
        if 'provision_template_id' in data:
            del(data['provision_template_id'])
        if 'finish_template_id' in data:
            del(data['finish_template_id'])

        return data

    def add(self, args):
        """add a new operating system"""
        data = self.__add_modify(args)
        json_request('operatingsystems', 'POST', {'operatingsystem': data})

    def modify(self, args):
        """modify an operating system"""
        data = self.__add_modify(args)
        path = os.path.join('operatingsystems', args.id[0])
        json_request(path, 'PUT', {'operatingsystem': data})

    def delete(self, args):
        """delete an operating system"""
        path = os.path.join('operatingsystems', args.delete[0])
        json_request(path, 'DELETE')

    def info(self, args):
        """info about operating systems"""
        path = os.path.join('operatingsystems', args.operatingsystem[0])
        json_request(path, output='pretty')


class ComputeResource:
    """manage compute resources"""

    def power_state(self, args, uuid):
        path = os.path.join('compute_resources', args.target[0], 'vms', uuid)
        data = json_request(path, method='GET', output='object')
        if data['state'] != 'shutoff':
            return True

    def info(self, args):
        """query information"""
        if args.query:
            path = os.path.join('compute_resources', args.query[0], 'vms')
            json_request(path, output='pretty_list')
        elif args.uuids:
            path = os.path.join('compute_resources', args.uuids[0], 'vms')
            json_request(path, output='uuids')

    def action(self, args):
        """perform various actions"""
        if args.power_toggle:
            path = os.path.join('compute_resources', args.target[0], 'vms',
                args.power_toggle[0], 'power')
            json_request(path, method='PUT')
        elif args.power_on:
            if self.power_state(args, args.power_on[0]):
                print('warning: node "%s" is already running' %
                    args.power_on[0])
            else:
                path = os.path.join('compute_resources', args.target[0], 'vms',
                    args.power_on[0], 'power')
                json_request(path, method='PUT')
        elif args.power_off:
            if self.power_state(args, args.power_off[0]):
                path = os.path.join('compute_resources', args.target[0], 'vms',
                    args.power_off[0], 'power')
                json_request(path, method='PUT')
            else:
                print('warning: node "%s" is not running' % args.power_off[0])
        elif args.destroy:
            path = os.path.join('compute_resources', args.target[0], 'vms',
                args.destroy[0])
            json_request(path, method='DELETE')

    def add(self, args):
        """add a compute resource"""
        data = args_to_dict(args, ComputeResourceObject())
        json_request('compute_resources', 'POST', {'compute_resource': data})

    def modify(self, args):
        """modify a compute resource"""
        data = args_to_dict(args, ComputeResourceObject())
        del(data['id'])
        path = os.path.join('compute_resources', args.id[0])
        json_request(path, 'PUT', {'compute_resource': data})

    def delete(self, args):
        """delete a compute resource"""
        path = os.path.join('compute_resources', args.delete[0])
        json_request(path, 'DELETE')


class Media:
    """manage installation media"""

    def add(self, args):
        """add new installation media"""
        data = args_to_dict(args, MediaObject())
        json_request('media', 'POST', {'medium': data})

    def modify(self, args):
        """modify installation media"""
        data = args_to_dict(args, MediaObject())
        del(data['id'])
        path = os.path.join('media', args.id[0])
        json_request(path, 'PUT', {'medium': data})

    def delete(self, args):
        """delete installation media"""
        path = os.path.join('media', args.delete[0])
        json_request(path, 'DELETE')


class Architecture:
    """manage architectures"""

    def add(self, args):
        """add an architecture"""
        data = args_to_dict(args, ArchitectureObject())
        json_request('architectures', 'POST', {'architecture': data})

    def modify(self, args):
        """modify an architecture"""
        data = args_to_dict(args, ArchitectureObject())
        del(data['current_name'])
        path = os.path.join('architectures', args.current_name[0])
        json_request(path, 'PUT', {'architecture': data})

    def delete(self, args):
        """delete an architecture"""
        path = os.path.join('architectures', args.delete[0])
        json_request(path, 'DELETE')


class SmartProxy:
    """manage a smart_proxy"""

    def add(self, args):
        """add a smart proxy"""
        data = args_to_dict(args, SmartProxyObject())
        json_request('smart_proxies', 'POST', {'smart_proxy': data})

    def modify(self, args):
        """modify a smart proxy"""
        data = args_to_dict(args, SmartProxyObject())
        path = os.path.join('smart_proxies', args.id[0])
        json_request(path, 'PUT', {'smart_proxy': data})

    def delete(self, args):
        """delete a smart proxy"""
        path = os.path.join('smart_proxies', args.delete[0])
        json_request(path, 'DELETE')


def dynamic_args(parser, attrs):
    """generate arguments based on resource object"""
    attributes = attrs.__dict__.keys()
    for attribute in attributes:
        parser.add_argument('--' + attribute, nargs=1, help=attribute)
    return parser

def argument_parser():
    """process the arguments"""
    parser = argparse.ArgumentParser(description='foremanBuddy - Manage '
        'Foreman via the CLI (c) 2012 Jasper Poppe/eBuddy',
        epilog='for more tools written by me '
        'visit: http://www.infrastructureanywhere.com',
        fromfile_prefix_chars='@')
    parser.add_argument('--version', action='version', version=__version__)
    parser.add_argument('-u', '--foreman_user', nargs=1, metavar='USER',
        help='foreman user')
    parser.add_argument('-p', '--foreman_password', nargs=1,
        metavar='PASSWORD', help='foreman password')
    parser.add_argument('-f', '--foreman_url', nargs=1, metavar='URL',
        help='foreman url')
    parser.add_argument('-i', '--ignore_proxy', action='store_true',
        help='ignore the system proxy')
    parser.add_argument('-d', '--debug', action='store_true',
        help='enable debug mode')

    subparsers = parser.add_subparsers()

    # info
    parse_info = Info()
    
    parser_info = subparsers.add_parser('info',
        help='list info about resources', formatter_class=RawTextHelpFormatter)
    parser_info.add_argument('-b', '--bare_output', action='store_true',
        help='use bare instead of prettyfied output')
    parser_info.add_argument('-a', '--architectures', action='store_true',
        help='list all defined architectures')
    parser_info.add_argument('-d', '--domains', action='store_true',
        help='list all defined domains')
    parser_info.add_argument('-s', '--subnets', action='store_true',
        help='list all defined subnets')
    parser_info.add_argument('-e', '--environments', action='store_true',
        help='list all defined environments')
    parser_info.add_argument('-f', '--facts', action='store_true',
        help='list all defined facts')
    parser_info.add_argument('-g', '--hostgroups', action='store_true',
        help='list all defined hostgroups')
    parser_info.add_argument('-n', '--hosts', action='store_true',
        help='list all defined hosts')
    parser_info.add_argument('-o', '--operatingsystems', action='store_true',
        help='list all defined operating systems')
    parser_info.add_argument('-S', '--smart_proxies', action='store_true',
        help='list all defined smart proxies')
    parser_info.add_argument('-p', '--puppetclasses', action='store_true',
        help='list all known puppet classes')
    parser_info.add_argument('-m', '--media', action='store_true',
        help='list configured installation media')
    parser_info.add_argument('-t', '--config_templates', action='store_true',
        help='list all defined provisioning templates')
    parser_info.add_argument('-P', '--ptables', action='store_true',
        help='list all defined partition tables')
    parser_info.add_argument('-u', '--users', action='store_true',
        help='list all defined users')
    parser_info.add_argument('-U', '--usergroups', action='store_true',
        help='list all defined user groups')
    parser_info.add_argument('-c', '--compute_resources', action='store_true',
        help='list all compute resources')
    parser_info.add_argument('--status', action='store_true',
        help='foreman system status')
    parser_info.add_argument('--dashboard', action='store_true',
        help='summary of Foreman statistics')
    parser_info.set_defaults(func=parse_info.info)

    # ids
    parser_ids = subparsers.add_parser('ids',
        help='list ids of objects', formatter_class=RawTextHelpFormatter)
    parser_ids.add_argument('-a', '--architectures', action='store_true',
        help='list all defined architectures')
    parser_ids.add_argument('-d', '--domains', action='store_true',
        help='list all defined domains')
    parser_ids.add_argument('-s', '--subnets', action='store_true',
        help='list all defined subnets')
    parser_ids.add_argument('-e', '--environments', action='store_true',
        help='list all defined environments')
    parser_ids.add_argument('-g', '--hostgroups', action='store_true',
        help='list all defined hostgroups')
    parser_ids.add_argument('-n', '--hosts', action='store_true',
        help='list all defined hosts')
    parser_ids.add_argument('-o', '--operatingsystems', action='store_true',
        help='list all defined operating systems')
    parser_ids.add_argument('-S', '--smart_proxies', action='store_true',
        help='list all defined smart proxies')
    parser_ids.add_argument('-m', '--media', action='store_true',
        help='list configured installation media')
    parser_ids.add_argument('-t', '--config_templates', action='store_true',
        help='list all defined provisioning templates')
    parser_ids.add_argument('-P', '--ptables', action='store_true',
        help='list all defined partition tables')
    parser_ids.add_argument('-u', '--users', action='store_true',
        help='list all defined users')
    parser_ids.add_argument('-U', '--usergroups', action='store_true',
        help='list all defined user groups')
    parser_ids.add_argument('-c', '--compute_resources', action='store_true',
        help='list all compute resources')
    parser_ids.set_defaults(func=parse_info.ids)

    # host
    parse_host = Host()
    host_group = subparsers.add_parser('host', help='manage hosts')
    host_subparser = host_group.add_subparsers()

    host_info = host_subparser.add_parser('info', help='query information')
    host_info.add_argument('-q', '--query', nargs=1, metavar='FQDN',
        help='list the details of a host')
    host_info.add_argument('-f', '--facts', nargs=1, metavar='FQDN',
        help='list the facts of a host')
    host_info.add_argument('-e', '--errors', action='store_true',
        help='list of hosts in error state')
    host_info.add_argument('-a', '--active', action='store_true',
        help='list of active hosts')
    host_info.add_argument('-o', '--out_of_sync', action='store_true',
        help='list of out of sync hosts')
    host_info.add_argument('-d', '--disabled', action='store_true',
        help='list of disabled hosts')
    host_info.add_argument('-p', '--puppetclasses', nargs=1, metavar='FQDN',
        help='list of host puppet classes')
    host_info.add_argument('-r', '--reports', nargs=1, metavar='FQDN',
        help='list reports for host')
    host_info.add_argument('-l', '--report_last', nargs=1, metavar='FQDN',
        help='list last report for host')
    host_info.add_argument('-c', '--pxe_config', nargs=1, metavar='FQDN',
        help='list syslinux configuration for host')
    host_info.set_defaults(func=parse_host.info)

    host_action = host_subparser.add_parser('action', help='perform host '
        'actions')
    host_action.add_argument('-s', '--set_build', nargs=1, metavar='FQDN',
        help='enable (re)installation of a host')
    host_action.add_argument('-c', '--cancel_build', nargs=1, metavar='FQDN',
        help='disable installation of a host')
    host_action.set_defaults(func=parse_host.action)

    host_add = host_subparser.add_parser('add', help='add a new host')
    host_add = dynamic_args(host_add, HostObject())
    host_add.set_defaults(func=parse_host.add)

    host_compute_add = host_subparser.add_parser('compute_add',
        help='add a new virtual host')
    host_compute_add = dynamic_args(host_compute_add, HostMergedObject())
    host_compute_add.set_defaults(func=parse_host.compute_add)

    host_modify = host_subparser.add_parser('modify', parents=[host_add],
        help='modify a host', add_help=False)
    host_modify.add_argument('current_fqdn', nargs=1, metavar='FQDN',
        help='host fully qualified domain name')
    host_modify.set_defaults(func=parse_host.modify)

    host_delete = host_subparser.add_parser('delete', help='delete a host')
    host_delete.add_argument('delete', nargs=1, metavar='FQDN',
        help='fully qualified domain name')
    host_delete.set_defaults(func=parse_host.delete)

    host_add_parameter = host_subparser.add_parser('add_parameter',
        help='add a host parameter')
    host_add_parameter.add_argument('target', nargs=1, metavar='NAME',
        help='host name')
    host_add_parameter.add_argument('-k', '--key', nargs=1,
        help='parameter key')
    host_add_parameter.add_argument('-v', '--value', nargs=1,
        help='parameter value')
    host_add_parameter.set_defaults(func=parse_host.add_parameter)

    host_delete_parameter = host_subparser.add_parser('delete_parameter',
        help='delete a host parameter')
    host_delete_parameter.add_argument('target', nargs=1, metavar='NAME',
        help='host name')
    host_delete_parameter.add_argument('-k', '--key', nargs=1,
        help='parameter key')
    host_delete_parameter.set_defaults(func=parse_host.delete_parameter)

    host_modify_parameter = host_subparser.add_parser('modify_parameter',
        help='modify a host group parameter')
    host_modify_parameter.add_argument('target', nargs=1, metavar='ID',
        help='host group name')
    host_modify_parameter.add_argument('-k', '--key', nargs=1,
        help='parameter key')
    host_modify_parameter.add_argument('-v', '--value', nargs=1,
        help='parameter value')
    host_modify_parameter.set_defaults(func=parse_host.modify_parameter)

    # hostgroup
    parse_hostgroup = HostGroup()
    hostgroup_group = subparsers.add_parser('hostgroup',
        help='manage host groups')
    hostgroup_subparser = hostgroup_group.add_subparsers()

    hostgroup_add = hostgroup_subparser.add_parser('add',
        help='add a new host group')
    hostgroup_add = dynamic_args(hostgroup_add, HostGroupObject())
    hostgroup_add.set_defaults(func=parse_hostgroup.add)

    hostgroup_modify = hostgroup_subparser.add_parser('modify',
        parents=[hostgroup_add], help='modify a host group', add_help=False)
    hostgroup_modify.add_argument('id_hostgroup', nargs=1, metavar='ID',
        help='host group ID')
    hostgroup_modify.set_defaults(func=parse_hostgroup.modify)

    hostgroup_delete = hostgroup_subparser.add_parser('delete',
        help='delete a host group')
    hostgroup_delete.add_argument('delete', nargs=1, metavar='ID',
        help='host group ID')
    hostgroup_delete.set_defaults(func=parse_hostgroup.delete)

    hostgroup_info = hostgroup_subparser.add_parser('info',
        help='info about a host group')
    hostgroup_info.add_argument('hostgroup', nargs=1, metavar='ID',
        help='list host group details')
    hostgroup_info.set_defaults(func=parse_hostgroup.info)

    hostgroup_add_parameter = hostgroup_subparser.add_parser('add_parameter',
        help='add a host group parameter')
    hostgroup_add_parameter.add_argument('target', nargs=1, metavar='ID',
        help='host group name')
    hostgroup_add_parameter.add_argument('-k', '--key', nargs=1,
        help='parameter key')
    hostgroup_add_parameter.add_argument('-v', '--value', nargs=1,
        help='parameter value')
    hostgroup_add_parameter.set_defaults(func=parse_hostgroup.add_parameter)

    hostgroup_delete_parameter = hostgroup_subparser.add_parser(
        'delete_parameter', help='delete a host group parameter')
    hostgroup_delete_parameter.add_argument('target', nargs=1,
        metavar='ID', help='host group ID')
    hostgroup_delete_parameter.add_argument('-k', '--key', nargs=1,
        help='parameter key')
    hostgroup_delete_parameter.set_defaults(
        func=parse_hostgroup.delete_parameter)

    hostgroup_modify_parameter = hostgroup_subparser.add_parser(
        'modify_parameter', help='modify a host group parameter')
    hostgroup_modify_parameter.add_argument('target', nargs=1, metavar='ID',
        help='host group name')
    hostgroup_modify_parameter.add_argument('-k', '--key', nargs=1,
        help='parameter key')
    hostgroup_modify_parameter.add_argument('-v', '--value', nargs=1,
        help='parameter value')
    hostgroup_modify_parameter.set_defaults(
        func=parse_hostgroup.modify_parameter)

    # architecture
    parse_architecture = Architecture()
    architecture_group = subparsers.add_parser('architecture',
        help='manage architectures')
    architecture_subparser = architecture_group.add_subparsers()

    architecture_add = architecture_subparser.add_parser('add',
        help='add a new architecture')
    architecture_add = dynamic_args(architecture_add, ArchitectureObject())
    architecture_add.set_defaults(func=parse_architecture.add)

    architecture_modify = architecture_subparser.add_parser('modify',
        help='modify a architecture', parents=[architecture_add],
        add_help=False)
    architecture_modify.add_argument('current_name', nargs=1,
        metavar='CURRENT_NAME', help='architecture name')
    architecture_modify.set_defaults(func=parse_architecture.modify)

    architecture_delete = architecture_subparser.add_parser('delete',
        help='delete a architecture')
    architecture_delete.add_argument('delete', nargs=1, metavar='NAME',
        help='architecture name')
    architecture_delete.set_defaults(func=parse_architecture.delete)

    # installation media
    parse_media = Media()
    media_group = subparsers.add_parser('media',
        help='manage installation media')
    media_subparser = media_group.add_subparsers()

    media_add = media_subparser.add_parser('add',
        help='add new installation media')
    media_add = dynamic_args(media_add, MediaObject())
    media_add.set_defaults(func=parse_media.add)

    media_modify = media_subparser.add_parser('modify',
        help='modify installation media', parents=[media_add], add_help=False)
    media_modify.add_argument('id', nargs=1, metavar='ID',
        help='installation media ID')
    media_modify.set_defaults(func=parse_media.modify)

    media_delete = media_subparser.add_parser('delete',
        help='delete installation media')
    media_delete.add_argument('delete', nargs=1, metavar='ID',
        help='installation media ID')
    media_delete.set_defaults(func=parse_media.delete)

    # domain
    parse_domain = Domain()
    domain_group = subparsers.add_parser('domain', help='manage domains')
    domain_subparser = domain_group.add_subparsers()

    domain_add = domain_subparser.add_parser('add',
        help='add a new domain')
    domain_add = dynamic_args(domain_add, DomainObject())
    domain_add.set_defaults(func=parse_domain.add)

    domain_modify = domain_subparser.add_parser('modify',
        help='modify a domain', parents=[domain_add], add_help=False)
    domain_modify.add_argument('current_name', nargs=1, metavar='CURRENT_NAME',
        help='domain name')
    domain_modify.set_defaults(func=parse_domain.modify)

    domain_delete = domain_subparser.add_parser('delete',
        help='delete a domain')
    domain_delete.add_argument('delete', nargs=1, metavar='NAME',
        help='domain name')
    domain_delete.set_defaults(func=parse_domain.delete)

    domain_info = domain_subparser.add_parser('info',
        help='info about a domain')
    domain_info.add_argument('domain', nargs=1, metavar='NAME',
        help='list domain details')
    domain_info.set_defaults(func=parse_domain.info)

    domain_add_parameter = domain_subparser.add_parser('add_parameter',
        help='add a domain parameter')
    domain_add_parameter.add_argument('target', nargs=1, metavar='NAME',
        help='domain name')
    domain_add_parameter.add_argument('-k', '--key', nargs=1,
        help='parameter key')
    domain_add_parameter.add_argument('-v', '--value', nargs=1,
        help='parameter value')
    domain_add_parameter.set_defaults(func=parse_domain.add_parameter)

    domain_delete_parameter = domain_subparser.add_parser('delete_parameter',
        help='delete a domain parameter')
    domain_delete_parameter.add_argument('target', nargs=1, metavar='NAME',
        help='domain name')
    domain_delete_parameter.add_argument('-k', '--key', nargs=1,
        help='parameter key')
    domain_delete_parameter.set_defaults(func=parse_domain.delete_parameter)

    domain_modify_parameter = domain_subparser.add_parser('modify_parameter',
        help='modify a host group parameter')
    domain_modify_parameter.add_argument('target', nargs=1, metavar='ID',
        help='host group name')
    domain_modify_parameter.add_argument('-k', '--key', nargs=1,
        help='parameter key')
    domain_modify_parameter.add_argument('-v', '--value', nargs=1,
        help='parameter value')
    domain_modify_parameter.set_defaults(func=parse_domain.modify_parameter)

    # operating system
    parse_operatingsystem = OperatingSystem()
    operatingsystem_group = subparsers.add_parser('operatingsystem',
        help='manage operating systems')
    operatingsystem_subparser = operatingsystem_group.add_subparsers()

    operatingsystem_add = operatingsystem_subparser.add_parser('add',
        help='add a new operating system')
    operatingsystem_add = dynamic_args(operatingsystem_add,
        OperatingSystemObject())
    operatingsystem_add.set_defaults(func=parse_operatingsystem.add)

    operatingsystem_modify = operatingsystem_subparser.add_parser('modify',
        help='modify an operating system', parents=[operatingsystem_add],
        add_help=False)
    operatingsystem_modify.add_argument('id', nargs=1, metavar='ID',
        help='operating system id')
    operatingsystem_modify.set_defaults(func=parse_operatingsystem.modify)

    operatingsystem_delete = operatingsystem_subparser.add_parser('delete',
        help='delete an operating system')
    operatingsystem_delete.add_argument('delete', nargs=1, metavar='ID',
        help='operatingsystem id')
    operatingsystem_delete.set_defaults(func=parse_operatingsystem.delete)

    operatingsystem_info = operatingsystem_subparser.add_parser('info',
        help='info about an operating system')
    operatingsystem_info.add_argument('operatingsystem', nargs=1, metavar='ID',
        help='list operating system details')
    operatingsystem_info.set_defaults(func=parse_operatingsystem.info)

    # template
    parse_template = Template()

    template_group = subparsers.add_parser('template',
        help='manage provisioning templates')
    template_subparser = template_group.add_subparsers()

    template_add = template_subparser.add_parser('add',
        help='add a new provisioning template')
    template_add.add_argument('--name', nargs=1, metavar='NAME',
        help='name of the template')
    template_add.add_argument('--hostgroup_id', nargs=1, metavar='ID',
        help='ID of the hostgroup to bind the template')
    template_add.add_argument('--string', nargs=1, metavar='STRING',
        help='the template data (can not be used with --file)')
    template_add.add_argument('--file_name', nargs=1, metavar='FILE_NAME',
        help='read template data from a file (can not be used with --string)')
    template_add.add_argument('--template_kind_id', nargs=1, metavar='ID',
        help='the ID of the template kind')
    template_add.add_argument('--snippet', action='store_true',
        help='specify this parameter if the template is a snippet')
    template_add.add_argument('--operatingsystem_ids', nargs=1,
        metavar='OPERATINGSYSTEM_IDS', help='the ID of the template kind')
    template_add.set_defaults(func=parse_template.add)

    template_modify = template_subparser.add_parser('modify',
        help='modify a provisioning template', parents=[template_add],
        add_help=False)
    template_modify.add_argument('id', nargs=1, metavar='ID',
        help='template id')
    template_modify.set_defaults(func=parse_template.modify)

    template_delete = template_subparser.add_parser('delete',
        help='delete a provisioning template')
    template_delete.add_argument('delete', nargs=1, metavar='ID',
        help='template id')
    template_delete.set_defaults(func=parse_template.delete)

    template_build = template_subparser.add_parser('build',
        help='deploy the default pxe template to all smart proxies')
    template_build.set_defaults(func=parse_template.build_pxe_default)

    # partition tables
    parse_ptable = PTable()
    ptable_group = subparsers.add_parser('ptable',
        help='manage partition tables')
    ptable_subparser = ptable_group.add_subparsers()

    ptable_add = ptable_subparser.add_parser('add',
        help='add a new ptable')
    ptable_add.add_argument('--name', nargs=1, metavar='NAME',
        help='name of the partition table')
    ptable_add.add_argument('--file_name', nargs=1, metavar='FILE_NAME',
        help='read layout from a file (can not be used with --string)')
    ptable_add.add_argument('--string', nargs=1, metavar='STRING',
        help='read layout from a string (can not be used with --file_name)')
    ptable_add.add_argument('--os_family', nargs=1, metavar='OS_FAMILY',
        help='operating system family (e.g. Debian)')
    ptable_add.set_defaults(func=parse_ptable.add)

    ptable_modify = ptable_subparser.add_parser('modify',
        help='modify partition table', parents=[ptable_add], add_help=False)
    ptable_modify.add_argument('id', nargs=1, metavar='ID',
        help='partition table ID')
    ptable_modify.set_defaults(func=parse_ptable.modify)

    ptable_delete = ptable_subparser.add_parser('delete',
        help='delete partition table')
    ptable_delete.add_argument('delete', nargs=1, metavar='ID',
        help='partition table id')
    ptable_delete.set_defaults(func=parse_ptable.delete)

    # puppet classes
    parse_puppetclass = PuppetClass()
    puppetclass_group = subparsers.add_parser('puppetclass',
        help='manage puppet classes')
    puppetclass_subparser = puppetclass_group.add_subparsers()

    puppetclass_modify = puppetclass_subparser.add_parser('modify',
        help='modify a puppet class')
    puppetclass_modify.add_argument('id', nargs=1, metavar='ID',
        help='puppet class ID')
    puppetclass_modify.add_argument('--name', nargs=1, metavar='NAME',
        help='name of the puppet class')
    puppetclass_modify.add_argument('--nameindicator', nargs=1,
        metavar='NAMEINDICATOR', help='name indicator')
    puppetclass_modify.add_argument('--operatingsystem_id', nargs=1,
        metavar='OS_ID', help='operating system ID')
    puppetclass_modify.set_defaults(func=parse_puppetclass.modify)

    puppetclass_delete = puppetclass_subparser.add_parser('delete',
        help='delete a puppet class')
    puppetclass_delete.add_argument('delete', nargs=1, metavar='ID',
        help='puppet class ID')
    puppetclass_delete.set_defaults(func=parse_puppetclass.delete)

    #FIXME: find a way to import puppet classes via the api
    #puppetclass_import = puppetclass_subparser.add_parser('import',
    #    help='import puppet classes and environments')
    #puppetclass_import.add_argument('proxy_id', nargs=1, metavar='PROXY_ID',
    #    help='smart proxy ID')
    #puppetclass_import.set_defaults(func=parse_puppetclass.import_env)

    # subnet
    parse_subnet = Subnet()
    subnet_group = subparsers.add_parser('subnet', help='manage subnets')
    subnet_subparser = subnet_group.add_subparsers()

    subnet_add = subnet_subparser.add_parser('add',
        help='add a new subnet')
    subnet_add = dynamic_args(subnet_add, SubnetObject())
    subnet_add.set_defaults(func=parse_subnet.add)

    subnet_modify = subnet_subparser.add_parser('modify',
        help='modify a subnet', parents=[subnet_add], add_help=False)
    subnet_modify.add_argument('id', nargs=1, metavar='ID', help='subnet ID')
    subnet_modify.set_defaults(func=parse_subnet.modify)

    subnet_delete = subnet_subparser.add_parser('delete',
        help='delete a subnet')
    subnet_delete.add_argument('delete', nargs=1, metavar='ID',
        help='subnet ID')
    subnet_delete.set_defaults(func=parse_subnet.delete)

    # smart proxy
    smart_proxy = SmartProxyObject()
    smart_proxy_attributes = smart_proxy.__dict__.keys()

    parse_smart_proxy = SmartProxy()
    smart_proxy_group = subparsers.add_parser('smart_proxy',
        help='manage smart proxies')
    smart_proxy_subparser = smart_proxy_group.add_subparsers()

    smart_proxy_add = smart_proxy_subparser.add_parser('add',
        help='add a new smart_proxy')
    for attribute in smart_proxy_attributes:
        smart_proxy_add.add_argument('--' + attribute, nargs=1, help=attribute)
    smart_proxy_add.set_defaults(func=parse_smart_proxy.add)

    smart_proxy_modify = smart_proxy_subparser.add_parser('modify',
        help='modify a smart_proxy', parents=[smart_proxy_add], add_help=False)
    smart_proxy_modify.add_argument('id', nargs=1, metavar='ID',
        help='smart proxy ID')
    smart_proxy_modify.set_defaults(func=parse_smart_proxy.modify)

    smart_proxy_delete = smart_proxy_subparser.add_parser('delete',
        help='delete a smart_proxy')
    smart_proxy_delete.add_argument('delete', nargs=1, metavar='ID',
        help='smart proxy ID')
    smart_proxy_delete.set_defaults(func=parse_smart_proxy.delete)

    # users
    parse_user = User()
    user_group = subparsers.add_parser('user', help='manage users')
    user_subparser = user_group.add_subparsers()

    user_add = user_subparser.add_parser('add', help='add a new user')
    user_add = dynamic_args(user_add, UserObject())
    user_add.set_defaults(func=parse_user.add)

    user_modify = user_subparser.add_parser('modify',
        help='modify a user', parents=[user_add], add_help=False)
    user_modify.add_argument('id', nargs=1, metavar='ID',
        help='user ID')
    user_modify.set_defaults(func=parse_user.modify)

    user_delete = user_subparser.add_parser('delete', help='delete a user')
    user_delete.add_argument('delete', nargs=1, metavar='ID', help='user ID')
    user_delete.set_defaults(func=parse_user.delete)

    # compute resources
    parse_compute_resource = ComputeResource()
    compute_resource_group = subparsers.add_parser('compute_resource',
        help='manage compute resources')
    compute_resource_subparser = compute_resource_group.add_subparsers()

    compute_resource_info = compute_resource_subparser.add_parser('info',
        help='query information')
    compute_resource_info.add_argument('-q', '--query', nargs=1, metavar='ID',
        help='list the nodes from a compute resource')
    compute_resource_info.add_argument('-u', '--uuids', nargs=1, metavar='ID',
        help='list host names + UUIDs')
    compute_resource_info.set_defaults(func=parse_compute_resource.info)

    compute_resource_action = compute_resource_subparser.add_parser('action',
        help='perform various actions')
    compute_resource_action.add_argument('target', metavar='ID',
        help='ID of the compute resource')
    compute_resource_action.add_argument('-t', '--power_toggle', nargs=1,
        metavar='UUID', help='toggle power')
    compute_resource_action.add_argument('-p', '--power_on', nargs=1,
        metavar='UUID', help='turn power on')
    compute_resource_action.add_argument('-o', '--power_off', nargs=1,
        metavar='UUID', help='turn power off')
    compute_resource_action.add_argument('-d', '--destroy', nargs=1,
        metavar='UUID', help='destroy (delete) a virtual node + data')
    compute_resource_action.set_defaults(func=parse_compute_resource.action)

    compute_resource_add = compute_resource_subparser.add_parser('add',
        help='add a new compute resource')
    compute_resource_add = dynamic_args(compute_resource_add,
        ComputeResourceObject())
    compute_resource_add.set_defaults(func=parse_compute_resource.add)

    compute_resource_modify = compute_resource_subparser.add_parser('modify',
        help='modify a compute resource', parents=[compute_resource_add],
        add_help=False)
    compute_resource_modify.add_argument('id', nargs=1, metavar='ID',
        help='compute resource ID')
    compute_resource_modify.set_defaults(func=parse_compute_resource.modify)

    compute_resource_delete = compute_resource_subparser.add_parser('delete',
        help='delete a compute resource')
    compute_resource_delete.add_argument('delete', nargs=1, metavar='ID',
        help='compute resources ID')
    compute_resource_delete.set_defaults(func=parse_compute_resource.delete)

    # process globals
    args = parser.parse_args()
    if args.foreman_password:
        global FOREMAN_PASSWORD
        FOREMAN_PASSWORD = args.foreman_password[0]
    if args.foreman_user:
        global FOREMAN_USER
        FOREMAN_USER = args.foreman_user[0]
    if args.foreman_url:
        global FOREMAN_URL
        FOREMAN_URL = args.foreman_url[0]
    if args.ignore_proxy:
        global IGNORE_SYSTEM_PROXY
        IGNORE_SYSTEM_PROXY = True
    if args.debug:
        global DEBUG
        DEBUG = True
    
    delattr(args, 'foreman_password')
    delattr(args, 'foreman_user')
    delattr(args, 'foreman_url')
    delattr(args, 'ignore_proxy')
    delattr(args, 'debug')

    args.func(args)

def main():
    """the main application"""
    try:
        argument_parser()
    except Exception as err:
        print(err)
        raise
        sys.exit(1)

if __name__ == '__main__':
    """catch keyboard interruption"""
    try:
        main()
    except SystemExit as err:
        sys.exit(err.code)
    except KeyboardInterrupt:
        sys.stderr.write('info: cancelled by user\n')
        sys.exit(1)
