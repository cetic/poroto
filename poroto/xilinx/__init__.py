from poroto.platform import Platform
from poroto.common import load_template, mkdir_safe
from poroto.config import gen_path, src_path, ipcore_path
from poroto.template import FileTemplate
from poroto import roccc, config

from .bram import BramMemory, BromMemory
from .fifo import Fifo
import string

class XilinxPlatform(Platform):
    device_family = None
    package = None
    speedgrade = None
    def __init__(self, designer, debug):
        Platform.__init__(self, designer, debug)
        designer.add_file(src_path, "HwBramFifo.vhdl")
        roccc.intrinsics.add_fp_add(latency=11)
        roccc.intrinsics.add_fp_sub(latency=11)
        roccc.intrinsics.add_fp_mul(latency=8)
        roccc.intrinsics.add_fp_div(latency=28)
        roccc.intrinsics.add_int_div(latency=13)

    @classmethod
    def register_arguments(cls, arg_parser):
        arg_parser.add_argument('--device-family', metavar='<device family name>', dest='device_family', default="",
                       help='Define Xilinx device family')
        arg_parser.add_argument('--package', metavar='<package type>', dest='package', default="",
                       help='Define Xilinx package type')
        arg_parser.add_argument('--speed-grade', metavar='<speed grade value>', dest='speedgrade', default="",
                       help='Define Xilinx device speed grade')

    @classmethod
    def parse_arguments(cls, args):
        cls.device_family=args.device_family
        cls.package=args.package
        cls.speedgrade=string.replace(args.speedgrade, 'm', '-')

    def create_mem(self, mem_type, name, data_type, size, init):
        if mem_type == 'bram':
            return BramMemory(name, data_type, size, init, self.debug)
        elif mem_type == 'brom':
            return BromMemory(name, data_type, size, init, self.debug)

    def create_fifo(self):
        return Fifo(self.debug)

    def add_intrinsic(self, designer, intrinsic):
        FileTemplate(intrinsic + "_impl.xco").generate(gen_path, ipcore_path, intrinsic + "_impl", intrinsic + "_impl.xco")
        designer.add_file(src_path, "%s.vhdl" % intrinsic)
        designer.add_file(ipcore_path, "%s_impl/%s_impl.xco" % (intrinsic, intrinsic))

    def get_keys(self):
        return {
                'DEVICE_FAMILY': self.device_family,
                'DEVICE': config.device,
                'PACKAGE': self.package,
                'SPEEDGRADE': self.speedgrade
               }
