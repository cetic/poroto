library ieee;
use ieee.std_logic_1164.all;
use ieee.std_logic_unsigned.all;
use ieee.numeric_std.all;

package poroto_pkg is
  
  constant MEM_BRAMS : natural := 6; --TODO: %%%BRAMS_NB%%%;
  constant BRAM_ADDR_WIDTH : natural := 32;
  
  ----------------------
  -- Memory Wrapper   --
  ----------------------

  type poroto_bram_m2sT is record
	re : STD_LOGIC;
	we : STD_LOGIC;
	addr_r : STD_LOGIC_VECTOR(31 DOWNTO 0);
	addr_w : STD_LOGIC_VECTOR(31 DOWNTO 0);
	din : STD_LOGIC_VECTOR(31 DOWNTO 0);
  end record poroto_bram_m2sT;

  -- Block Data Flow from Slave to Master
  type poroto_bram_s2mT is record
	dout : STD_LOGIC_VECTOR(31 DOWNTO 0);
  end record poroto_bram_s2mT;

  type poroto_bram_m2sT_array is array (natural range <>) of poroto_bram_m2sT;
  type poroto_bram_s2mT_array is array (natural range <>) of poroto_bram_s2mT;

  -- Define type defaults
  constant POROTO_BRAM_DEFAULT_M2S : poroto_bram_m2sT :=
    (re   => '0',
     we   => '0',
     addr_r => (others => '0'),
     addr_w => (others => '0'),
     din  => (others => '0'));

  constant POROTO_BRAM_DEFAULT_S2M : poroto_bram_s2mT :=
    (dout => (others => '0'));

end;


package body poroto_pkg is

end;