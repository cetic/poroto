#!/usr/bin/env python
'''
Created on 8 oct. 2012

@author: ld
'''
import os
import shutil
import argparse
import config
from common import mkdir_safe
from pycparser import parse_file, c_generator
from modules import FunctionsRegistry
from template import FileTemplate
from simplifier import CompoundSimplifier
from registers import RegisterMap
from pragma import PragmaRegistry, ParsePorotoPragma
from memory import MemoryMap, MemoryPragmaHandler
from stream import StreamMap, StreamPragmaHandler
from ip import IPInstance, FilePragmaHandler, LatencyPragmaHandler
import array
from array import ArrayPragmaHandler
from function import FunctionParser, FunctionInstance
from roccc.roccc import ROCCC
import roccc.config
import re
from poroto.xilinx import XilinxPlatform

class Poroto:
    def __init__(self, test_vectors_file=None, debug=False):
        self.debug = debug
        
        self.test_vectors_file = test_vectors_file
        mkdir_safe(config.gen_path)
        mkdir_safe(os.path.join(config.gen_path, config.vhdl_path))
        mkdir_safe(os.path.join(config.gen_path, 'c'))
        mkdir_safe(os.path.join(config.gen_path, config.ipcore_path))

        if self.test_vectors_file:
            global_symb = {}
            execfile(self.test_vectors_file, global_symb)
            self.test_vectors = global_symb['test_vectors']
        else:
            self.test_vectors = None

        self.ast_list = []
        if config.design_tool == 'pa':
            from poroto.plan_ahead import PlanAhead
            self.designer = PlanAhead()
        elif config.design_tool == 'ghdl':
            from poroto.ghdl import Ghdl
            self.designer = Ghdl()
        else:
            raise Exception("Unknown design tool '%s'" % config.design_tool)
        FunctionInstance.designer=self.designer
        self.registers_map = RegisterMap(self.debug)
        self.mems_map = MemoryMap(self.debug)
        self.functions = FunctionsRegistry(self.designer, self.mems_map, self.debug)
        self.streams_map = StreamMap(self.mems_map, self.functions, self.debug)
        self.pragma_registry=PragmaRegistry(self.debug)
        if config.converter == 'roccc':
            self.converter=ROCCC(self.debug)
        else:
            raise Exception("Unknown converter '%s'" % config.converter)
        self.converter.init(self.pragma_registry)
        if config.device_vendor == "xilinx":
            from poroto.xilinx import XilinxPlatform
            self.platform = XilinxPlatform(self.designer, self.debug)
        elif config.device_vendor == "sim":
            from poroto.sim import SimPlatform
            self.platform = SimPlatform(self.designer, self.debug)
        else:
            raise Exception("Unknown device vendor '%s'" % config.platform_vendor)
        if config.sdk == "alphadata":
            from poroto.alphadata import AlphaDataSDK
            self.sdk = AlphaDataSDK(self.platform, self.designer, self.functions.functions, self.registers_map, self.mems_map, self.streams_map, self.test_vectors, self.debug)
        elif config.sdk == "none":
            from poroto.none import NoneSDK
            self.sdk = NoneSDK(self.platform, self.designer, self.functions.functions, self.registers_map, self.mems_map, self.streams_map, self.test_vectors, self.debug)
        elif config.sdk == "riffa":
            from poroto.riffa import RiffaSDK
            self.sdk = RiffaSDK(self.platform, self.designer, self.functions.functions, self.registers_map, self.mems_map, self.streams_map, self.test_vectors, self.debug)
        else:
            raise Exception("Unknown sdk '%s'" % config.sdk)
        self.pragma_registry.add_pragma_type('file', FilePragmaHandler(self.designer, self.debug))
        self.pragma_registry.add_pragma_type('memory', MemoryPragmaHandler(self.functions, self.mems_map, self.sdk, self.debug))
        self.pragma_registry.add_pragma_type('stream', StreamPragmaHandler(self.streams_map, self.debug))
        self.pragma_registry.add_pragma_type('latency', LatencyPragmaHandler(self.debug))
        self.pragma_registry.add_pragma_type('array', ArrayPragmaHandler(self.debug))
        array.init(self.platform, self.converter, self.functions, self.mems_map, self.streams_map)
        IPInstance.converter = self.converter
        FileTemplate.platform = self.platform

    def parse(self, in_file, createAST=True):
        ast = parse_file(in_file, use_cpp=True, cpp_path='gcc', cpp_args=['-E', '-I' + roccc.config.roccc_root])
        if createAST: ast.show()
        self.ast_list.append((in_file, ast))
        
    def convert(self, createAST=True):
        for validator in self.converter.first_pass_validators():
            for (in_file, ast) in self.ast_list:
                a = validator(self.debug)
                a.visit(ast)
        for (in_file, ast) in self.ast_list:
            a = ParsePorotoPragma(self.pragma_registry, self.debug)
            a.visit(ast)
        for (in_file, ast) in self.ast_list:
            a = CompoundSimplifier()
            a.visit(ast)
        for converter in array.converters:
            for (in_file, ast) in self.ast_list:
                a = converter(self.debug)
                a.visit(ast)
        for converter in self.converter.converters():
            for (in_file, ast) in self.ast_list:
                a = converter(self.debug)
                a.visit(ast)
        for validator in self.converter.second_pass_validators():
            for (in_file, ast) in self.ast_list:
                a = validator(self.debug)
                a.visit(ast)
        for (in_file, ast) in self.ast_list:
            a=FunctionParser(self.functions, self.platform, self.debug)
            a.visit(ast)
        self.streams_map.consolidate()
        self.functions.consolidate()
        for (in_file, ast) in self.ast_list:
            if createAST: ast.show()
            if config.create_converted:
                m = re.match( r'(.*)\.(.*)', os.path.basename(in_file))
                if m is None:
                    out_file = in_file + '-poroto.c'
                else:
                    out_file = m.group(1)+'-poroto.'+m.group(2)
                generator = c_generator.CGenerator()
                generated = generator.visit(ast)
                out = open(os.path.join(config.gen_path, out_file), 'w' )
                print >> out, generated
                out.close()

    def definePorts(self):
        for instance in self.functions.functions:
            instance.define_ports(self.sdk)

    def defineMmap(self):
        for instance in self.functions.functions:
            self.registers_map.add_function(instance)

    def writeWrappers(self):
        self.sdk.generate_wrappers()

    def done(self):
        pass

    def update_project(self, project_path):
        src=os.path.join(config.gen_path, config.vhdl_path)
        dest=os.path.join(project_path, self.designer.dest_path[config.gen_path])
        mkdir_safe(dest)
        for entry in os.listdir(src):
            if not entry.endswith('_orig.vhdl'):
                shutil.copy(os.path.join(src, entry), dest)
        src=os.path.join(config.gen_path, config.ipcore_path)
        dest=os.path.join(project_path, self.designer.dest_path[config.ipcore_path])
        for entry in os.listdir(src):
            shutil.rmtree(os.path.join(dest, entry), True)
            shutil.copytree(os.path.join(src, entry), os.path.join(dest, entry))
        self.designer.generate(project_path)
        src=os.path.join(config.gen_path, config.c_path)
        dest=os.path.join(project_path, config.c_tb_path)
        mkdir_safe(dest)
        for entry in os.listdir(src):
            shutil.copy(os.path.join(src, entry), dest)

def main():
    parser = argparse.ArgumentParser(description='C->VHDL poroto')
    parser.add_argument('source_files', metavar='<source file>', nargs='+',
                       help='C source file')
    parser.add_argument('--tb', metavar='<file>', dest='test_vectors_file',
                       help='Test vectors file')
    parser.add_argument('--cpp', metavar='<file>', dest='cpp_path',
                       help='C PreProcessor to use')
    parser.add_argument('--cpp-args', metavar='<arguments>', dest='cpp_args', nargs='+',
                       help='Optional arguments to give to cpp')
    parser.add_argument('--header', metavar='<text>', dest='c_header',
                       help='Header to add')
    parser.add_argument('--debug', dest='debug', action='store_true',
                       help='Print debug information')
    parser.add_argument('--create-ast', dest='createAST', action='store_true',
                       help='Create AST files')
    parser.add_argument('--keep-temp', dest='keep_temp', action='store_true',
                       help='Keep temporary files')
    parser.add_argument('--duplicate', dest='duplicate', action='store_true', default=False,
                       help='Duplicate functions')
    parser.add_argument('--sdk', metavar='<sdk name>', dest='sdk',
                       help='SDK name')
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
    parser.add_argument('--project', metavar='<target project path>', dest='project',
                       help='Target project path')
    parser.add_argument('--unisim', dest='unisim', action='store_true', default=False,
                       help='Use unisim simulation library')
    roccc.roccc.ROCCC.register_arguments(parser)
    XilinxPlatform.register_arguments(parser)

    args = parser.parse_args()

    config.create_converted=args.keep_temp
    config.sdk=args.sdk
    config.platform_vendor=args.platform_vendor
    config.platform=args.platform
    config.target=args.target
    config.device_vendor=args.device_vendor
    config.device=args.device
    config.design_tool=args.design_tool
    config.design_version=args.design_version or ''
    config.c_header=args.c_header
    config.duplicate_functions=args.duplicate
    config.use_unisim=args.unisim
    roccc.roccc.ROCCC.parse_arguments(args)
    XilinxPlatform.parse_arguments(args)
    
    poroto=Poroto(debug=args.debug, test_vectors_file=args.test_vectors_file)
    print "Parsing files..."
    for source_file in args.source_files:
        poroto.parse(source_file, createAST=args.createAST)
    print "Convert code..."
    poroto.convert(createAST=args.createAST)
    print "Map streams, ports and memories..."
    poroto.definePorts()
    poroto.defineMmap()
    print "Write wrappers..."
    poroto.writeWrappers()
    poroto.done()

    if args.project:
        print "Update project..."
        poroto.update_project(args.project)
