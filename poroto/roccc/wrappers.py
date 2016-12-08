class BurstWrapper:
    def __init__(self, instance_name, stream_name, debug):
        self.debug = debug
        self.instance_name = instance_name
        self.stream_name = stream_name
        self.full_name = "%s_%s" % (instance_name, stream_name)
    def get_temp_signals(self):
        return [
            "signal %s_address_translator_address_valid : STD_LOGIC;" % self.full_name,
            "signal %s_0_address_translator_address_stall : STD_LOGIC;" % self.full_name,
            "signal %s_0_address_translator_address : STD_LOGIC_VECTOR(31 downto 0);" % self.full_name
             ]

    def get_adapter_instance(self):
        return [
            "%s_address_translator0 : SpecialBurstAddressGen1Channels PORT MAP(" % self.full_name,
            "\tclk => %s_address_clk," % self.full_name,
            "\trst => %s_rst," % self.instance_name,
            "\tburst_address_in => %s_address_channel0_base," % self.full_name,
            "\tburst_count_in => %s_address_channel0_count," % self.full_name,
            "\tburst_valid_in => %s_address_rdy," % self.full_name,
            "\tburst_stall_out => %s_address_stall," % self.full_name,
            "\taddress_valid_out => %s_address_translator_address_valid," % self.full_name,
            "\taddress_stall_channel0_in => %s_0_address_translator_address_stall," % (self.full_name),
            "\taddress_channel0_out => %s_0_address_translator_address" % self.full_name,
            ");" ]

class MicroFifo:
    def __init__(self, instance_name, stream_name, debug):
        self.debug = debug
        self.instance_name = instance_name
        self.stream_name = stream_name
        self.full_name = "%s_%s" % (instance_name, stream_name)
    def get_temp_signals(self):
        return []
    def get_adapter_instance(self):
        return [
            "%s_0_address_lilo : MicroFifo" % self.full_name,
            "generic map(",
            "\tADDRESS_WIDTH => 8,",
            "\tDATA_WIDTH => 32,",
            "\tALMOST_FULL_COUNT => 3,",
            "\tALMOST_EMPTY_COUNT => 0",
            ") port map(",
            "\tclk => %s_address_clk," % self.full_name,
            "\trst => %s_rst," % self.instance_name,
            "\tdata_in => %s_0_address_translator_address," % self.full_name,
            "\tvalid_in => %s_address_translator_address_valid," % self.full_name,
            "\tfull_out => %s_0_address_translator_address_stall," % self.full_name,
            "\tdata_out => %s_0_address_fifo_data," % self.full_name,
            "\tread_enable_in => %s_0_address_fifo_read_enable," % self.full_name,
            "\tempty_out => %s_0_address_fifo_empty" % self.full_name,
            ");"
            ]

class SynchInterface:
    def __init__(self, instance_name, stream_name, debug):
        self.debug = debug
        self.instance_name = instance_name
        self.stream_name = stream_name
        self.full_name = "%s_%s" % (instance_name, stream_name)
    def get_temp_signals(self):
        return []
    def get_adapter_instance(self):
        return [
        "U_%s_0_Synch : SynchInterfaceGeneric" % self.full_name,
        "generic map(",
        "\tINPUT_DATA_WIDTH => %s_data_channel0'length," % self.full_name,
        "\tOUTPUT_DATA_WIDTH => 32",
        ") port map(",
            "\tclk => %s_address_clk," % self.full_name,
        "\trst => %s_rst," % self.instance_name,
        "\tdata_in => %s_data_channel0," % self.full_name,
        "\tdata_empty => %s_empty," % self.full_name,
        "\tdata_read => %s_read," % self.full_name,
        "\taddress_in => %s_0_address_fifo_data," % self.full_name,
        "\taddress_valid => %s_0_address_side_valid," % self.full_name,
        "\tstallAddress => open,"
        "\taddressPop => %s_0_address_fifo_read_enable,"  % self.full_name,
        "\tmc_stall_in => '0',"
        "\tmc_vadr_out => %s_0_address_fifo_data_2," % self.full_name,
        "\tmc_valid_out => %s_0_mc_valid," % self.full_name,
        "\tmc_data_out => %s_0_mc_data" % self.full_name,
        ");"
        ]
