library ieee;
use ieee.std_logic_1164.all;
use ieee.std_logic_unsigned.all;
use ieee.numeric_std.all;

package poroto_pkg is
	  
  ----------------------
  -- Memory Wrapper   --
  ----------------------
  constant MEM_BRAMS : natural := %%%BRAMS_NB%%%;
  constant REGISTER_DATA_SIZE : natural := 32;
  constant REGISTER_ADDR_SIZE : natural := 32;
  constant C_PCI_DATA_WIDTH : natural := 64;
  constant BRAM_DATA_SIZE : natural := 32;
  
  type poroto_riffa_m2sT is record
        -- RIFFA channel interface: RX
        EN         : std_logic;
        LAST       : std_logic;
        LEN        : std_logic_vector(31 downto 0);
        OFF        : std_logic_vector(30 downto 0);
        DATA       : std_logic_vector(C_PCI_DATA_WIDTH - 1 downto 0);
        DATA_VALID : std_logic;
  end record poroto_riffa_m2sT;
  
  type poroto_riffa_s2mT is record
        ACK        : std_logic;
        DATA_REN   : std_logic;
  end record poroto_riffa_s2mT;

  type poroto_riffa_m2sT_array is array (natural range <>) of poroto_riffa_m2sT;
  type poroto_riffa_s2mT_array is array (natural range <>) of poroto_riffa_s2mT;

  -- Types for entity ports (required for verilog > vhdl translation)
  type sig_array is array (natural range <>) of std_logic;
  type vect32_array is array (natural range <>) of std_logic_vector(31 downto 0);
  type vect31_array is array (natural range <>) of std_logic_vector(30 downto 0);
  type vect_pcidatawidth_array is array (natural range <>) of std_logic_vector(C_PCI_DATA_WIDTH - 1 downto 0);

  type poroto_riffa_ctrl_t is record
        EN         : std_logic;
        LAST       : std_logic;
        LEN        : std_logic_vector(31 downto 0);
        OFF        : std_logic_vector(30 downto 0);
  end record poroto_riffa_ctrl_t;
  type poroto_riffa_ctrl_array_t is array (natural range <>) of poroto_riffa_ctrl_t;

  type poroto_bram_m2sT is record
	re : STD_LOGIC;
	we : STD_LOGIC;
	addr_r : STD_LOGIC_VECTOR(31 DOWNTO 0);
	addr_w : STD_LOGIC_VECTOR(31 DOWNTO 0);
	din : STD_LOGIC_VECTOR(BRAM_DATA_SIZE-1 DOWNTO 0);
  end record poroto_bram_m2sT;

  type poroto_bram_s2mT is record
	dout : STD_LOGIC_VECTOR(BRAM_DATA_SIZE-1 DOWNTO 0);
  end record poroto_bram_s2mT;

  type poroto_bram_m2sT_array is array (natural range <>) of poroto_bram_m2sT;
  type poroto_bram_s2mT_array is array (natural range <>) of poroto_bram_s2mT;

  -- Define type defaults
  constant POROTO_RIFFA_DEFAULT_M2S : poroto_riffa_m2sT :=
    (EN         => '0',
     LAST       => '0',
     LEN        => (others => '0'),
     OFF        => (others => '0'),
     DATA       => (others => '0'),
     DATA_VALID => '0');

  constant POROTO_RIFFA_DEFAULT_S2M : poroto_riffa_s2mT :=
    (ACK        => '0',
     DATA_REN   => '0');

  constant POROTO_BRAM_DEFAULT_M2S : poroto_bram_m2sT :=
    (re   => '0',
     we   => '0',
     addr_r => (others => '0'),
     addr_w => (others => '0'),
     din  => (others => '0'));

  constant POROTO_BRAM_DEFAULT_S2M : poroto_bram_s2mT :=
    (dout => (others => '0'));

  ---------------------------
  -- top level blocks      --
  ---------------------------

end;
