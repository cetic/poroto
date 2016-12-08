library ieee;
use ieee.std_logic_1164.all;

library work;
use work.poroto_pkg.all;

entity poroto is
    port(
        rst          		: in std_logic;
        clk         		: in std_logic;

		riffa_rx_en 		: in sig_array(0 to MEM_BRAMS);
		riffa_rx_last		: in sig_array(0 to MEM_BRAMS);
		riffa_rx_len		: in vect32_array(0 to MEM_BRAMS);
		riffa_rx_off		: in vect31_array(0 to MEM_BRAMS);
		riffa_rx_data		: in vect_pcidatawidth_array(0 to MEM_BRAMS);
		riffa_rx_data_valid	: in sig_array(0 to MEM_BRAMS);
		riffa_rx_ack		: out sig_array(0 to MEM_BRAMS);
		riffa_rx_data_ren	: out sig_array(0 to MEM_BRAMS);

		riffa_tx_en 		: out sig_array(0 to MEM_BRAMS);
		riffa_tx_last		: out sig_array(0 to MEM_BRAMS);
		riffa_tx_len		: out vect32_array(0 to MEM_BRAMS);
		riffa_tx_off		: out vect31_array(0 to MEM_BRAMS);
		riffa_tx_data		: out vect_pcidatawidth_array(0 to MEM_BRAMS);
		riffa_tx_data_valid	: out sig_array(0 to MEM_BRAMS);
		riffa_tx_ack		: in sig_array(0 to MEM_BRAMS);
		riffa_tx_data_ren	: in sig_array(0 to MEM_BRAMS)
    );
end;


architecture syn of poroto is  
  -----------------------
  -- Interface signals --
  -----------------------
  --	Port signals:
  -- Entity must be declared without any record type for instantiation in verilog files
  -- Records are kept in poroto.vhd file - and mapped to entity ports
  signal riffa_rx_m2s  	:	poroto_riffa_m2sT_array(0 to MEM_BRAMS);
  signal riffa_rx_s2m 	: 	poroto_riffa_s2mT_array(0 to MEM_BRAMS);
  signal riffa_tx_m2s 	: 	poroto_riffa_m2sT_array(0 to MEM_BRAMS);
  signal riffa_tx_s2m 	: 	poroto_riffa_s2mT_array(0 to MEM_BRAMS);

  -- BRAM memory interface
  signal bram_mem_m2s : poroto_bram_m2sT_array(0 to MEM_BRAMS-1);
  signal bram_mem_s2m : poroto_bram_s2mT_array(0 to MEM_BRAMS-1) := (others => POROTO_BRAM_DEFAULT_S2M);

  signal bram_app_m2s : poroto_bram_m2sT_array(0 to MEM_BRAMS-1);
  signal bram_app_s2m : poroto_bram_s2mT_array(0 to MEM_BRAMS-1) := (others => POROTO_BRAM_DEFAULT_S2M);
  
  signal bram_registers_m2s : poroto_bram_m2sT;
  signal bram_registers_s2m : poroto_bram_s2mT;
  
  -- RIFFA Remote Control
  signal riffa_ctrl         : poroto_riffa_ctrl_array_t(0 to MEM_BRAMS);

  ----------------
  -- Components --
  ----------------
    component riffa_bram is
        generic(C_PCI_DATA_WIDTH : integer := 64);
        port(
            CLK                : in  std_logic;
            RST                : in  std_logic;
            
            -- RIFFA channel interface: RX
            riffa_rx_m2s       : in poroto_riffa_m2sT;
            riffa_rx_s2m       : out poroto_riffa_s2mT;
            -- RIFFA channel interface: TX
            riffa_tx_m2s       : out poroto_riffa_m2sT;
            riffa_tx_s2m       : in poroto_riffa_s2mT;
            -- RIFFA remote control
            riffa_ctrl         : poroto_riffa_ctrl_t;
            -- BRAM BUS Interface
            bram_m2s           : out poroto_bram_m2sT;
            bram_s2m           : in poroto_bram_s2mT);
    end component;
    component registers is
    port (
        clk   : in std_logic;
        rst   : in std_logic;
        bram_m2s : in poroto_bram_m2sT;
        bram_s2m : out poroto_bram_s2mT;
        -- RIFFA Remote Control
        riffa_ctrl   : out poroto_riffa_ctrl_array_t(0 to MEM_BRAMS);
        --On-board BRAM interface
        bram_app_m2s : out poroto_bram_m2sT_array(0 to MEM_BRAMS-1);
        bram_app_s2m : in poroto_bram_s2mT_array(0 to MEM_BRAMS-1)
    );
    end component;

    --Temporarily here until better platform definition
    component bram is
    generic (
        DATA    : integer := 32;
        ADDR    : integer := 8
    );
    port (
        -- Port A
        clka   : in std_logic;
        --rsta   : in std_logic;
        --enb    : in std_logic;
        wea    : in std_logic;
        addra  : in std_logic_vector(ADDR-1 downto 0);
        dina   : in std_logic_vector(DATA-1 downto 0);
        douta  : out std_logic_vector(DATA-1 downto 0);

        -- Port B
        clkb   : in std_logic;
        --rstb   : in std_logic;
        --enb    : in std_logic;
        web    : in std_logic;
        addrb  : in std_logic_vector(ADDR-1 downto 0);
        dinb   : in std_logic_vector(DATA-1 downto 0);
        doutb  : out std_logic_vector(DATA-1 downto 0)
    );
    end component;

  -- %%%MEM_COMPONENTS%%%

begin
 --------------------------
 -- Entity ports mapping --
 --------------------------


	ent_portmap : for i in 0 to MEM_BRAMS generate
		riffa_rx_m2s(i).EN 			<=	riffa_rx_en(i);
		riffa_rx_m2s(i).LAST       	<=	riffa_rx_last(i);
		riffa_rx_m2s(i).LEN 		<=	riffa_rx_len(i);
		riffa_rx_m2s(i).OFF 		<=	riffa_rx_off(i);
		riffa_rx_m2s(i).DATA 		<=	riffa_rx_data(i);
		riffa_rx_m2s(i).DATA_VALID 	<=	riffa_rx_data_valid(i);
		riffa_rx_ack(i)				<= 	riffa_rx_s2m(i).ACK;
		riffa_rx_data_ren(i)		<= 	riffa_rx_s2m(i).DATA_REN;

		riffa_tx_en(i) 				<=	riffa_tx_m2s(i).EN;
		riffa_tx_last(i)			<=	riffa_tx_m2s(i).LAST;
		riffa_tx_len(i)				<=	riffa_tx_m2s(i).LEN;
		riffa_tx_off(i)				<=	riffa_tx_m2s(i).OFF;
		riffa_tx_data(i)			<=	riffa_tx_m2s(i).DATA;
		riffa_tx_data_valid(i)		<=	riffa_tx_m2s(i).DATA_VALID;
		riffa_tx_s2m(i).ACK			<= 	riffa_tx_ack(i);
		riffa_tx_s2m(i).DATA_REN	<= 	riffa_tx_data_ren(i);
	end generate;

  --------------------
  -- BRAM Interface --
  --------------------

  -- %%%MEMORY%%%
  
   --------------------------
  -- Application interface --
  ---------------------------
  riffa_bram_i : riffa_bram
  port map (
    CLK                => clk,
    RST                => rst,
    
    -- RIFFA channel interface: RX
    riffa_rx_m2s       => riffa_rx_m2s(0),
    riffa_rx_s2m       => riffa_rx_s2m(0),
    -- RIFFA channel interface: TX
    riffa_tx_m2s       => riffa_tx_m2s(0),
    riffa_tx_s2m       => riffa_tx_s2m(0),
    -- RIFFA remote control
    riffa_ctrl         => riffa_ctrl(0),
    -- BRAM BUS Interface
    bram_m2s           => bram_registers_m2s,
    bram_s2m           => bram_registers_s2m
  );
  
  registers_i : registers
  port map (
    clk => clk,
    rst => rst,
    bram_m2s => bram_registers_m2s,
    bram_s2m => bram_registers_s2m,
    riffa_ctrl => riffa_ctrl,
    bram_app_m2s => bram_app_m2s,
    bram_app_s2m => bram_app_s2m
  );
end;