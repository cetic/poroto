#!/usr/bin/env python
'''
Created on 8 oct. 2012

@author: ld
'''

import os
import argparse
import shutil
from poroto.common import mkdir_safe
from poroto.common import get_path_for, root_path
from poroto.config import src_path, lib_path, ipcore_path, vhdl_path, roccc_path, c_path, c_tb_path
from poroto import config
from poroto.plan_ahead import PlanAhead
from poroto.ghdl import Ghdl

designer = None

def tree_copy(project_name, level_path, src_path, dest_path):
    src_full_path = os.path.join(level_path, src_path)
    if os.path.exists(src_full_path):
        print "Copy", src_full_path
        shutil.copytree(src_full_path, os.path.join(project_name, dest_path))

def dir_copy(project_name, level_path, src_path, dest_path):
    src_full_path = os.path.join(level_path, src_path)
    if os.path.exists(src_full_path):
        mkdir_safe(os.path.join(project_name, dest_path))
        for entry in os.listdir(src_full_path):
            if entry != '.svn':
                shutil.copy(os.path.join(src_full_path, entry), os.path.join(project_name, dest_path))

def copy_vhdl_level(level_path, project_name):
    design_dest = designer.dest_path
    tree_copy(project_name, level_path, lib_path, design_dest[lib_path])
    dir_copy(project_name, level_path, src_path, design_dest[src_path])
    tree_copy(project_name, level_path, ipcore_path, design_dest[ipcore_path])

def generate_vhdl_project(project_name):
    design_path = get_path_for(config.design_tool, config.design_version)
    if design_path == None:
        print "ERROR: Design tool '%s' or version '%s' unknown" % (config.design_tool, config.design_version)
        exit(1)
    shutil.copytree(design_path, project_name)
    top_path=os.path.join(root_path, vhdl_path)
    copy_vhdl_level(top_path, project_name)
    #Check if the platform vendor is the same as the sdk provider
    if config.sdk != config.platform_vendor:
        path=top_path
        for sub_path in [config.sdk, config.platform, config.target]:
            path=os.path.join(path, sub_path)
            copy_vhdl_level(path, project_name)
    path=top_path
    for sub_path in [config.platform_vendor, config.platform, config.target]:
        if not sub_path: break
        path=os.path.join(path, sub_path)
        copy_vhdl_level(path, project_name)
    path=top_path
    for sub_path in [config.device_vendor, config.device]:
        if not sub_path: break
        path=os.path.join(path, sub_path)
        print "Check", path
        copy_vhdl_level(path, project_name)
    path=os.path.join(root_path, vhdl_path, roccc_path)
    copy_vhdl_level(path, project_name)

def generate_c_project(project_name):
    mkdir_safe(os.path.join(project_name, c_tb_path))
    path=os.path.join(root_path, c_path)
    dir_copy(project_name, path, src_path, c_tb_path)
    path=os.path.join(path, config.sdk)
    dir_copy(project_name, path, src_path, c_tb_path)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='C->VHDL converter')
    parser.add_argument('project_name', metavar='<project name>',
                       help='Project name')
    parser.add_argument('--sdk', metavar='<sdk name>', dest='sdk', default=config.sdk,
                       help='SDK name (default: %s)' % config.sdk)
    parser.add_argument('--platform-vendor', metavar='<platform vendor name>', dest='platform_vendor',
                       help='Platform vendor name')
    parser.add_argument('--platform', metavar='<platform name>', dest='platform',
                       help='Platform name')
    parser.add_argument('--target', metavar='<target name>', dest='target',
                       help='Target name')
    parser.add_argument('--device-vendor', metavar='<device vendor name>', dest='device_vendor',
                       help='Device vendor name')
    parser.add_argument('--device', metavar='<device name>', dest='device',
                       help='Device name')
    parser.add_argument('--design-tool', metavar='<design tool name>', dest='design_tool',
                       help='Design tool name')
    parser.add_argument('--design-version', metavar='<design tool version>', dest='design_version',
                       help='Design tool version')

    args = parser.parse_args()
    config.sdk=args.sdk
    config.platform_vendor=args.platform_vendor
    config.platform=args.platform
    config.target=args.target
    config.device_vendor=args.device_vendor
    config.device=args.device
    config.design_tool=args.design_tool
    config.design_version=args.design_version or ''

    if config.design_tool == 'pa':
        designer = PlanAhead()
    elif config.design_tool == 'ghdl':
        designer = Ghdl()
    else:
        print "ERROR: design tool '%s' unknown" % config.design_tool
        exit(1)

    if os.path.exists(args.project_name):
        print "ERROR: Project already exists"
        exit(1)

    generate_vhdl_project(args.project_name)
    generate_c_project(args.project_name)
