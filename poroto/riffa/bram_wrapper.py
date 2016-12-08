from poroto.memory import Memory

class BramMemoryWrapper(Memory):
    def get_component(self):
        return self.mem.get_component()

    def get_instance(self):
        return [
                "%s_conv_i : riffa_bram" % (self.name),
                "port map(",
                "\trst          => rst,",
                "\tclk          => clk,",
                "\t-- BRAM RIFFA interface: RX",
                "\triffa_rx_m2s => riffa_rx_m2s(%d)," % (self.index + 1),
                "\triffa_rx_s2m => riffa_rx_s2m(%d)," % (self.index + 1),
                "\t-- BRAM RIFFA interface: TX",
                "\triffa_tx_m2s => riffa_tx_m2s(%d)," % (self.index + 1),
                "\triffa_tx_s2m => riffa_tx_s2m(%d)," % (self.index + 1),
                "\t-- RIFFA remote control",
                "\triffa_ctrl => riffa_ctrl(%d)," % (self.index + 1),
                "\t-- BRAM BUS Interface",
                "\tbram_m2s => bram_mem_m2s(%d)," % self.index,
                "\tbram_s2m => bram_mem_s2m(%d));" % self.index
                ] + self.mem.get_instance()

    def generate(self, designer):
        self.mem = self.platform.create_mem_from("bram", self)
        self.mem.index = self.index
        self.mem.internal = False
        self.mem.generate(designer)
