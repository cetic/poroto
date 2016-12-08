LIBRARY ieee;
USE ieee.std_logic_1164.ALL;
library work;

entity %%%WRAPPER_NAME%%% is
port (
	clk : in STD_LOGIC;
	rst : in STD_LOGIC;
	inputReady : in STD_LOGIC;
	outputReady : out STD_LOGIC;
	done : out STD_LOGIC;
	stall : in STD_LOGIC;
	address : in STD_LOGIC_VECTOR(%%%ADDR_LEN%%%-1 downto 0);
	value : out STD_LOGIC_VECTOR(%%%DATA_SIZE%%%-1 downto 0)
	);
end %%%WRAPPER_NAME%%%;

architecture syn of %%%WRAPPER_NAME%%% is
component %%%BROM_NAME%%% is
port (
    clk   : in std_logic;
    --rst   : in std_logic;
    --en    : in std_logic;
    addr  : in std_logic_vector(%%%ADDR_LEN%%%-1 downto 0);
    dout  : out std_logic_vector(%%%DATA_SIZE%%%-1 downto 0)

);
end component;
begin
	brom : %%%BROM_NAME%%% port map (clk => clk,  addr => address, dout => value);
	done <= '1';
	process (rst, clk) is
	begin
	  if (rst = '1') then
          outputReady <= '0';
	  elsif( clk'event and clk = '1' ) then
	  	if ( inputReady = '1' ) then
	  		outputReady <= '1';
	  	else
	  		outputReady <= '0';
	  	end if;	  		
	  end if;
	end process;
end syn;
