from poroto.converter import Converter
from poroto.common import mkdir_safe
from poroto import config as poroto_config
from function import RocccFunctionInstance
from poroto import function
import intrinsics
import validators
import converters
import tool
import config
from pragma import RocccPragmaHandler
import os

class ROCCC(Converter):
    @classmethod
    def register_arguments(cls, arg_parser):
        arg_parser.add_argument('--no-register', dest='register', action='store_false', default=True,
                       help='Do not register module in ROCCC')

    @classmethod
    def parse_arguments(cls, args):
        config.register=args.register

    def init(self, pragma_registry):
        config.set_roccc_root(os.environ["ROCCC_ROOT"])
        mkdir_safe(os.path.join(poroto_config.gen_path, '.ROCCC'))
        intrinsics.remove_all()
        function.function_instance_generator = RocccFunctionInstance
        pragma_registry.add_pragma_type('roccc', RocccPragmaHandler(self.debug))

    def first_pass_validators(self):
        return validators.first_pass_validators
    
    def second_pass_validators(self):
        return validators.second_pass_validators
    
    def converters(self):
        return converters.converters

    def add_ip(self, name, latency, in_ports, out_ports):
        if config.register:
            tool.invoke_add_module(name, latency, in_ports, out_ports)
