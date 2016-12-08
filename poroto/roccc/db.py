'''
Created on 11 oct. 2012

@author: ld
'''
import sqlite3
import time

import config
from ..port import Port

def update_module(name):
    print "Looking for module %s" % name
    conn = sqlite3.connect(config.roccc_db)
    c=conn.cursor()
    c.execute("SELECT id FROM ComponentInfo WHERE componentName='%s';" % name)
    row = c.fetchone() 
    if row is not None:
        id = row[0]
        print "Module exists => %d" % id
        c.execute("DELETE FROM CompileInfo WHERE id=%d;" % id)
    c.execute("INSERT INTO CompileInfo VALUES (NULL, NULL, %d, 'NA', NULL, NULL, NULL, NULL, NULL, 1);" % int(time.time()))
    c.execute("SELECT MAX(id) FROM CompileInfo;")
    id = c.fetchone()[0]
    conn.commit()
    conn.close()
    return id

def add_module(name, latency, in_ports, out_ports):
    print "Adding module %s" % name
    conn = sqlite3.connect(config.roccc_db)
    c=conn.cursor()
    c.execute("SELECT id FROM ComponentInfo WHERE componentName='%s';" % name)
    row = c.fetchone() 
    if row is not None:
        print "Module already added (%d)" % row[0]
        conn.close()
        return
    c.execute("INSERT INTO CompileInfo VALUES (NULL, NULL, %d, 'NA', NULL, NULL, NULL, NULL, NULL, 1);" % int(time.time()))
    c.execute("SELECT MAX(id) FROM CompileInfo;")
    id = c.fetchone()[0]
    print "Id => %d" % id
    ports = ''
    c.execute("INSERT INTO ComponentInfo VALUES ('%s', %d, 'MODULE', NULL, NULL, '%s', NULL, %s, 1, NULL);" % (name, id, ports, latency))
    index = 0
    for port in in_ports:
        (name, size, data_type) = port
        index += 1
        c.execute("INSERT INTO Ports VALUES (%d, '%s', 'REGISTER', %d, '%s', 'IN', %d, '%s');" % (id, name, index, name, size, data_type))
    for port in out_ports:
        (name, size, data_type) = port
        index += 1
        c.execute("INSERT INTO Ports VALUES (%d, '%s', 'REGISTER', %d, '%s', 'OUT', %d, '%s');" % (id, name, index, name, size, data_type))
    conn.commit()
    conn.close()

def get_module_in_ports(name):
    conn = sqlite3.connect(config.roccc_db)
    c=conn.cursor()
    c.execute("SELECT id FROM ComponentInfo WHERE componentName='%s';" % name)
    row = c.fetchone() 
    if row is None:
        print "Module '%s' does not exist" % name
        return []
    id = row[0]
    result = []
    for row in c.execute("SELECT vhdlName, type, bitwidth, dataType FROM Ports WHERE id=%d AND direction='IN';" % id):
        port_name = row[0]
        internal=False
        if port_name.endswith('_in'):
            internal=port_name.endswith('_init_in')
            port_name = port_name.rpartition('_in')[0]
        port = Port(port_name, row[1] == 'REGISTER', row[0], row[2], row[3], internal)
        result.append(port)
    return result
    
def get_module_out_ports(name):
    conn = sqlite3.connect(config.roccc_db)
    c=conn.cursor()
    c.execute("SELECT id FROM ComponentInfo WHERE componentName='%s';" % name)
    row = c.fetchone() 
    if row is  None:
        print "Module '%s' does not exist" % name
        return []
    id = row[0]
    result = []
    for row in c.execute("SELECT vhdlName, type, bitwidth, dataType FROM Ports WHERE id=%d AND direction='OUT';" % id):
        port_name = row[0]        
        if port_name.endswith('_out'):
            port_name = port_name.rpartition('_out')[0]
            port_name = port_name.partition('_out')[0]
        port = Port(port_name, row[1] == 'REGISTER', row[0], row[2], row[3])
        result.append(port)
    return result

def get_module_in_streams(name):
    conn = sqlite3.connect(config.roccc_db)
    c=conn.cursor()
    c.execute("SELECT id FROM ComponentInfo WHERE componentName='%s';" % name)
    row = c.fetchone() 
    if row is None:
        print "Module '%s' does not exist" % name
        return []
    id = row[0]
    result = []
    for row in c.execute("SELECT readableName FROM Ports WHERE id=%d AND direction='IN' and type='STREAM_CHANNEL';" % id):
        result.append(row[0])
    return result
    
def get_module_out_streams(name):
    conn = sqlite3.connect(config.roccc_db)
    c=conn.cursor()
    c.execute("SELECT id FROM ComponentInfo WHERE componentName='%s';" % name)
    row = c.fetchone() 
    if row is None:
        print "Module '%s' does not exist" % name
        return []
    id = row[0]
    result = []
    for row in c.execute("SELECT readableName FROM Ports WHERE id=%d AND direction='OUT' and type='STREAM_CHANNEL';" % id):
        result.append(row[0])
    return result

def removeIntrinsics():
    conn = sqlite3.connect(config.roccc_db)
    c=conn.cursor()
    for row in c.execute("SELECT id FROM ComponentInfo WHERE type!='SYSTEM' AND type!='MODULE';"):
        id=row[0]
        c.execute("DELETE FROM Ports WHERE id='%d';" % id)
        c.execute("DELETE FROM CompileInfo WHERE id='%d';" % id)
    c.execute("DELETE FROM ComponentInfo WHERE type !='SYSTEM' AND type !='MODULE';")
    conn.commit()
    conn.close()

def add_intrinsic(name, type, latency, in_ports, out_ports):
    print "Adding intrinsic %s (%s)" % (name, type)
    conn = sqlite3.connect(config.roccc_db)
    c=conn.cursor()
    c.execute("INSERT INTO CompileInfo VALUES (NULL, NULL, %d, 'NA', NULL, NULL, NULL, NULL, NULL, 1);" % int(time.time()))
    c.execute("SELECT MAX(id) FROM CompileInfo;")
    id = c.fetchone()[0]
    print "Id => %d" % id
    ports = ''
    c.execute("INSERT INTO ComponentInfo VALUES ('%s', %d, '%s', NULL, NULL, '%s', NULL, %s, 1, NULL);" % (name, id, type, ports, latency))
    index = 0
    for port in in_ports:
        (name, size, data_type) = port
        index += 1
        c.execute("INSERT INTO Ports VALUES (%d, '', 'REGISTER', %d, '%s', 'IN', %d, '%s');" % (id, index, name, size, data_type))
    for port in out_ports:
        (name, size, data_type) = port
        index += 1
        c.execute("INSERT INTO Ports VALUES (%d, '', 'REGISTER', %d, '%s', 'OUT', %d, '%s');" % (id, index, name, size, data_type))
    conn.commit()
    conn.close()

def get_roccc_version():
    return "0.7.6.0"
