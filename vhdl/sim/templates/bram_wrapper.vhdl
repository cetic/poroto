
library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;

library work;
use work.poroto_pkg.all;

entity %%%NAME%%% is
port(
  rst     : in    std_logic;
  clk     : in    std_logic;
  -- MEM BRAM BUS Interface
  bram_mem_m2s : in poroto_bram_m2sT;
  bram_mem_s2m : out poroto_bram_s2mT;
  -- APP BRAM BUS Interface
  bram_app_m2s : in poroto_bram_m2sT;
  bram_app_s2m : out poroto_bram_s2mT);
end;

architecture syn of %%%NAME%%% is
  
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

  signal addra : std_logic_vector(%%%BRAM_ADDR_LEN%%%-1 downto 0);
  signal addrb : std_logic_vector(%%%BRAM_ADDR_LEN%%%-1 downto 0);

begin
  %%%NAMEGEN%%%_i: bram generic map (
  	DATA => 32,
  	ADDR => %%%BRAM_ADDR_LEN%%%
  )
  port map (
    clka => clk,
    --rsta => ocp_rst,
    --ena => tmp_ena,
    wea => bram_mem_m2s.we,
    addra => addra,
    dina => bram_mem_m2s.din,
    douta => bram_mem_s2m.dout,
    clkb => clk,
    --enb => '0',
    web => bram_app_m2s.we,
    addrb => addrb,
    dinb => bram_app_m2s.din,
    doutb => bram_app_s2m.dout
  );

  addra <= bram_mem_m2s.addr_w(%%%BRAM_ADDR_LEN%%%-1 downto 0) when (bram_mem_m2s.we = '1') else bram_mem_m2s.addr_r(%%%BRAM_ADDR_LEN%%%-1 downto 0);
  addrb <= bram_app_m2s.addr_w(%%%BRAM_ADDR_LEN%%%-1 downto 0) when (bram_app_m2s.we = '1') else bram_app_m2s.addr_r(%%%BRAM_ADDR_LEN%%%-1 downto 0);
end;
