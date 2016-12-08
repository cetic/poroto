from poroto.stream import Stream
from poroto.roccc.wrappers import BurstWrapper, MicroFifo, SynchInterface

class RocccBramInStream(Stream):
    def __init__(self, name, memory_name, size, data_size, debug):
        Stream.__init__(self, name, memory_name, size, data_size, debug)
        self.in_stream=True

    def get_temp_signals(self):
        burst = BurstWrapper(self.instance.name, self.name, self.debug)
        return burst.get_temp_signals() + [
                "constant %s_stream_NUM_CHANNELS : integer := 1;" % self.full_name,
                "signal %s_stream_channel : STD_LOGIC_VECTOR(%s_stream_NUM_CHANNELS * %s_data_channel0'length - 1 downto 0);" % (self.full_name, self.full_name, self.full_name),
                "signal %s_stream_address : STD_LOGIC_VECTOR(%s_stream_NUM_CHANNELS * 32 - 1 downto 0);" % (self.full_name, self.full_name)
            ]
    def get_adapter_instance(self):
        burst = BurstWrapper(self.instance.name, self.name, self.debug)
        return burst.get_adapter_instance() + [
                "%s_data_channel0 <= %s_stream_channel(1 * %s_data_channel0'length - 1 downto 0 * %s_data_channel0'length);" % (self.full_name, self.full_name, self.full_name, self.full_name),
                "%s_WClk <= clk;" % self.full_name,
                "%s_address_clk <= clk;" % self.full_name,
                "%s_0_address_translator_address_stall <= %s_full;" % (self.full_name, self.full_name),
                "%s_stream_address(31 downto 0) <= %s_0_address_translator_address;" % (self.full_name, self.full_name)
            ]

class RocccBramOutStream(Stream):
    def __init__(self, name, memory_name, size, data_size, debug):
        Stream.__init__(self, name, memory_name, size, data_size, debug)
        self.out_stream=True

    def get_temp_signals(self):
        burst = BurstWrapper(self.instance.name, self.name, self.debug)
        fifo = MicroFifo(self.instance.name, self.name, self.debug)
        syncInterface = SynchInterface(self.instance.name, self.name, self.debug)
        return burst.get_temp_signals() + fifo.get_temp_signals() + syncInterface.get_temp_signals() + [
                "constant %s_stream_NUM_CHANNELS : integer := 1;" % self.full_name,
                "signal %s_stream_channel : STD_LOGIC_VECTOR(%s_stream_NUM_CHANNELS * %s_data_channel0'length - 1 downto 0);" % (self.full_name, self.full_name, self.full_name),
                "signal %s_done : STD_LOGIC;" % self.full_name,
                "signal %s_0_stream_read_enable : STD_LOGIC;" % self.full_name,
                "signal %s_0_stream_data_valid : STD_LOGIC;" % self.full_name,
                "signal %s_0_address_side_valid : std_logic;" % self.full_name,
                "signal %s_0_address_fifo_data : STD_LOGIC_VECTOR(31 downto 0);" % self.full_name,
                "signal %s_0_address_fifo_read_enable : STD_LOGIC;" % self.full_name,
                "signal %s_0_address_fifo_empty : STD_LOGIC;" % self.full_name,
                "signal %s_0_address_fifo_data_2 : std_logic_vector(31 downto 0);" % self.full_name,
                "signal %s_0_empty : std_logic;" % self.full_name,
                "signal %s_0_read : std_logic;" % self.full_name,
                "signal %s_0_mc_valid : std_logic;" % self.full_name,
                "signal %s_0_mc_data : STD_LOGIC_VECTOR(31 downto 0);" % self.full_name,
            ]
    def get_adapter_instance(self):
        burst = BurstWrapper(self.instance.name, self.name, self.debug)
        fifo = MicroFifo(self.instance.name, self.name, self.debug)
        syncInterface = SynchInterface(self.instance.name, self.name, self.debug)
        return burst.get_adapter_instance() + fifo.get_adapter_instance() + syncInterface.get_adapter_instance() + [
                "%s_stream_channel(1 * %s_data_channel0'length - 1 downto 0 * %s_data_channel0'length) <= %s_data_channel0;" % (self.full_name, self.full_name, self.full_name, self.full_name),
                "%s_RClk <= clk;" % self.full_name,
                "%s_address_clk <= clk;" % self.full_name,
                "%s_done <= %s_done and %s_empty and %s_0_address_fifo_empty;" % (self.full_name, self.instance.name, self.full_name, self.full_name),
                "%s_0_address_side_valid <= not %s_0_address_fifo_empty;"  % (self.full_name, self.full_name),
                "%s_0_stream_data_valid <= '1';" % (self.full_name),
                "%s_0_empty <= %s_empty or %s_0_address_fifo_empty;" % (self.full_name, self.full_name, self.full_name),
                "%s_0_read <= %s_0_stream_data_valid and not %s_0_address_fifo_empty;" % (self.full_name, self.full_name, self.full_name)
            ]


class BramBaseStream(Stream):
    def __init__(self, name, memory_name, size, data_size, debug):
        Stream.__init__(self, name, memory_name, size, data_size, debug)

    def assign_instance(self, instance, from_instance):
        Stream.assign_instance(self, instance, from_instance)
        if from_instance:
            if self.memory_name not in from_instance.streams_map:
                print "Add bram stream in %s for %s" % (from_instance.name, self.memory_name)
                mem_stream = BramStream(self.memory_name, self.memory_name, self.size, self.debug)
                from_instance.add_stream(mem_stream)
            self.mem_stream = from_instance.streams_map[self.memory_name]
            if self.out_stream:
                self.mem_stream.out_stream=True
            if self.in_stream:
                self.mem_stream.in_stream=True

class BramStream(BramBaseStream):
    def get_user_signals(self):
        signals=[]
        if self.out_stream:
            signals += [
            '%s_clka : OUT STD_LOGIC;' % self.name,
            '%s_wea : OUT STD_LOGIC;' % self.name,
            '%s_addra : OUT STD_LOGIC_VECTOR(%d DOWNTO 0);' % (self.name, self.memory.address_size - 1),
            '%s_dina : OUT STD_LOGIC_VECTOR(31 DOWNTO 0);' % (self.name) ]
        if self.in_stream:
            signals += [
            '%s_clkb : OUT STD_LOGIC;' % self.name,
            '%s_enb : OUT STD_LOGIC;' % self.name,
            '%s_addrb : OUT STD_LOGIC_VECTOR(%d DOWNTO 0);' % (self.name, self.memory.address_size - 1),
            '%s_doutb : IN STD_LOGIC_VECTOR(31 DOWNTO 0);' % (self.name) ]
        return signals
    def get_temp_signals(self):
        signals=[]
        if self.out_stream:
            signals += [
            'signal %s_clka : STD_LOGIC;' % self.name,
            'signal %s_wea :  STD_LOGIC;' % self.name,
            'signal %s_addra : STD_LOGIC_VECTOR(%d DOWNTO 0);' % (self.name, self.memory.address_size - 1),
            'signal %s_dina : STD_LOGIC_VECTOR(31 DOWNTO 0);' % (self.name) ]
        if self.in_stream:
            signals += [
            'signal %s_clkb : STD_LOGIC;' % self.name,
            'signal %s_enb : STD_LOGIC;' % self.name,
            'signal %s_addrb : STD_LOGIC_VECTOR(%d DOWNTO 0);' % (self.name, self.memory.address_size - 1),
            'signal %s_doutb : STD_LOGIC_VECTOR(31 DOWNTO 0);' % (self.name) ]
        return signals
    def get_port_map(self):
        signals=[]
        if self.out_stream:
            signals += [
            '%s_clka => %s_clka' % (self.name, self.name),
            '%s_wea => %s_wea' % (self.name, self.name),
            '%s_addra => %s_addra' % (self.name, self.name),
            '%s_dina => %s_dina' % (self.name, self.name) ]
        if self.in_stream:
            signals += [
            '%s_clkb => %s_clkb' % (self.name, self.name),
            '%s_enb => %s_enb' % (self.name, self.name),
            '%s_addrb => %s_addrb' % (self.name, self.name),
            '%s_doutb => %s_doutb' % (self.name, self.name) ]
        return signals
    def get_adapter_instance(self):
        if self.in_stream and self.out_stream:
            return [
            'bram_app_m2s(%d).re <= %s_enb;'  % (self.memory.index, self.name),
            'bram_app_m2s(%d).we <= %s_wea;' % (self.memory.index, self.name),
            "bram_app_m2s(%d).addr_r <= (others => '0');" % (self.memory.index),
            "bram_app_m2s(%d).addr_r(%d-1 downto 0) <= %s_addrb;" % (self.memory.index, self.memory.address_size, self.name),
            "bram_app_m2s(%d).addr_w <= (others => '0');" % (self.memory.index),
            "bram_app_m2s(%d).addr_w(%d-1 downto 0) <= %s_addra;" % (self.memory.index, self.memory.address_size, self.name),
            'bram_app_m2s(%d).din <=  %s_dina;' % (self.memory.index, self.name),
            '%s_doutb <= bram_app_s2m(%d).dout;' % (self.name, self.memory.index),
            ]
        elif self.out_stream:
            return [
            "bram_app_m2s(%d).re <= '0';"  % (self.memory.index),
            'bram_app_m2s(%d).we <= %s_wea;' % (self.memory.index, self.name),
            "bram_app_m2s(%d).addr_r <= (others => '0');"  % (self.memory.index),
            "bram_app_m2s(%d).addr_w <= (others => '0');" % (self.memory.index),
            "bram_app_m2s(%d).addr_w(%d-1 downto 0) <= %s_addra;" % (self.memory.index, self.memory.address_size, self.name),
            'bram_app_m2s(%d).din <=  %s_dina;' % (self.memory.index, self.name),
            ]
        elif self.in_stream:
            return [
            'bram_app_m2s(%d).re <= %s_enb;'  % (self.memory.index, self.name),
            "bram_app_m2s(%d).we <= '0';" % (self.memory.index),
            "bram_app_m2s(%d).addr_r <= (others => '0');" % (self.memory.index),
            "bram_app_m2s(%d).addr_r(%d-1 downto 0) <= %s_addrb;" % (self.memory.index, self.memory.address_size, self.name),
            "bram_app_m2s(%d).addr_w <= (others => '0');"  % (self.memory.index),
            '%s_doutb <= bram_app_s2m(%d).dout;' % (self.name, self.memory.index),
            ]
        else:
            return []
    def get_c_decl(self):
        return [ 'extern %s* %s;' % (self.data_type, self.name)]
    def get_c_def(self):
        return [ '%s %s_array[%s];' % (self.data_type, self.name, self.memory.size),
                 '%s* %s = %s_array;' % (self.data_type, self.name, self.name) ]
    def get_set_data(self, src):
        if self.in_stream:
            return ['memcpy(%s, %s, %s*sizeof(%s));' % (self.name, src, self.size, self.data_type)]
        else:
            return []
    def get_get_data(self, target):
        if self.out_stream:
            return ['memcpy(%s, %s, %s*sizeof(%s));' % (target, self.name, self.size, self.data_type)]
        else:
            return []

class BramSetStream(BramBaseStream):
    def __init__(self, name, memory_name, size, data_size, mem_stream, debug):
        BramBaseStream.__init__(self, name, memory_name, size, data_size, debug)
        self.mem_stream=mem_stream
        if self.mem_stream:
            mem_stream.out_stream = True
        self.out_stream=True

    def get_user_signals(self):
        return [
            'bram_clk : OUT STD_LOGIC;',
            'bram_we : OUT STD_LOGIC;',
            'bram_addr : OUT STD_LOGIC_VECTOR(%d DOWNTO 0);' % (self.memory.address_size - 1),
            'bram_din : OUT STD_LOGIC_VECTOR(31 DOWNTO 0);'
            ]
    def get_port_map(self):
        return [
            'bram_clk => %s_clka' % self.name,
            'bram_we => %s_wea' % self.name,
            'bram_addr => %s_addra' % self.name,
            'bram_din => %s_dina' % self.name
            ]

class BramGetStream(BramBaseStream):
    def __init__(self, name, memory_name, size, data_size, mem_stream, debug):
        BramBaseStream.__init__(self, name, memory_name, size, data_size, debug)
        if mem_stream:
            mem_stream.in_stream=True
        self.in_stream=True
    
    def get_user_signals(self):
        return [
            'bram_clk : OUT STD_LOGIC;',
            'bram_en : OUT STD_LOGIC;',
            'bram_addr : OUT STD_LOGIC_VECTOR(%d DOWNTO 0);' % (self.memory.address_size - 1),
            'bram_dout : IN STD_LOGIC_VECTOR(31 DOWNTO 0);'
            ]
    def get_port_map(self):
        return [
            'bram_clk => %s_clkb' % self.name,
            'bram_en => %s_enb' % self.name,
            'bram_addr => %s_addrb' % self.name,
            'bram_dout => %s_doutb' % self.name
            ]