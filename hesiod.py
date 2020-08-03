"""
Present both functional and object-oriented interfaces for executing
lookups in Hesiod, Project Athena's service name resolution protocol.
"""

from _hesiod import bind, resolve

from pwd import struct_passwd
from grp import struct_group

class HesiodParseError(Exception):
    pass

class Lookup(object):
    """
    A Generic Hesiod lookup
    """
    def __init__(self, hes_name, hes_type):
        self.results = resolve(hes_name, hes_type)
        self.parseRecords()
    
    def parseRecords(self):
        pass

class FilsysLookup(Lookup):
    def __init__(self, name, **kwargs):
        self.parseTypes = True
        if 'parseFilsysTypes' in kwargs:
            self.parseTypes = kwargs['parseFilsysTypes']
        Lookup.__init__(self, name, 'filsys')
    
    def parseRecords(self):
        Lookup.parseRecords(self)
        
        self.filsys = []
        # An FSGROUP need not contain multiple members.
        # We are defining an FSGROUP as "Something for which all
        # returned records have an integer as the last field"

        self.isFSGroup = True
        for result in self.results:
            try:
                if int(result.rsplit(" ", 1)[1]) < 1:
                    self.isFSGroup = False
                    break
            except ValueError:
                self.isFSGroup = False
                break
            except IndexError:
                raise HesiodParseError("No fields found in result '%s'; shouldn't happen" % (result,))
        
        for result in self.results:
            priority = 0
            if self.isFSGroup:
                result, priority = result.rsplit(" ", 1)
                priority = int(priority)
            
            parts = result.split(" ")
            if len(parts) < 2:
                raise HesiodParseError("Invalid filsys record: %s" % (result))
            if not self.parseTypes:
                self.filsys.append(dict(type=parts[0],
                                        data=" ".join(parts[1::]),
                                        priority=priority))
                continue
            type = parts[0]
            if type == 'AFS':
                self.filsys.append(dict(type=type,
                                        location=parts[1],
                                        mode=parts[2],
                                        mountpoint=parts[3],
                                        priority=priority))
            elif type == 'NFS':
                self.filsys.append(dict(type=type,
                                        remote_location=parts[1],
                                        server=parts[2],
                                        mode=parts[3],
                                        mountpoint=parts[4],
                                        priority=priority))
            elif type == 'ERR':
                self.filsys.append(dict(type=type,
                                        message=" ".join(parts[1::]),
                                        priority=priority))
            elif type == 'UFS':
                self.filsys.append(dict(type=type,
                                        device=parts[1],
                                        mode=parts[2],
                                        mountpoint=parts[3],
                                        priority=priority))
            elif type == 'LOC':
                self.filsys.append(dict(type=type,
                                        location=parts[1],
                                        mode=parts[2],
                                        mountpoint=parts[3],
                                        priority=priority))
            else:
                raise HesiodParseError('Unknown filsys type: %s' % type)
        
        self.filsys.sort(key=(lambda x: x['priority']))

class PasswdLookup(Lookup):
    def __init__(self, name):
        Lookup.__init__(self, name, 'passwd')
    
    def parseRecords(self):
        passwd_info = self.results[0].split(':')
        passwd_info[2] = int(passwd_info[2])
        passwd_info[3] = int(passwd_info[3])
        self.passwd = struct_passwd(passwd_info)

class UidLookup(PasswdLookup):
    def __init__(self, uid):
        Lookup.__init__(self, b'%d' % (uid,), 'uid')

class GroupLookup(Lookup):
    def __init__(self, group):
        Lookup.__init__(self, group, 'group')
    
    def parseRecords(self):
        group_info = self.results[0].split(':')
        group_info[2] = int(group_info[2])
        members = group_info[3]
        if members != '':
            members = members.split(',')
        else:
            members = []
        group_info[3] = members
        
        self.group = struct_group(group_info)

class GidLookup(GroupLookup):
    def __init__(self, gid):
        Lookup.__init__(self, b'%d' % (gid,), 'gid')

__all__ = ['bind', 'resolve',
           'Lookup', 'FilsysLookup', 'PasswdLookup', 'UidLookup',
           'GroupLookup', 'GidLookup',
           'HesiodParseError']
