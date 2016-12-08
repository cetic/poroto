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
	address : in STD_LOGIC_VECTOR(%%%ADDR_WIDTH%%%-1 downto 0);
	value : out STD_LOGIC_VECTOR(%%%DATA_SIZE%%%-1 downto 0);
    bram_clk : OUT STD_LOGIC;
    bram_en : OUT STD_LOGIC;
    bram_addr : OUT STD_LOGIC_VECTOR(31 DOWNTO 0);
    bram_dout : IN STD_LOGIC_VECTOR(31 DOWNTO 0)
	);
end %%%WRAPPER_NAME%%%;

architecture syn of %%%WRAPPER_NAME%%% is
begin
	bram_clk <= clk;
	bram_en <= inputReady;
	done <= '1';
	bram_addr <= (others => '0' );
	bram_addr(%%%ADDR_WIDTH%%%-1 downto 0) <= address(%%%ADDR_WIDTH%%%-2-1 downto 0) & "00";
	value <= bram_dout(%%%DATA_SIZE%%%-1 downto 0);
	process (rst, clk) is
	begin
	  if (rst = '1') then
	  elsif( clk'event and clk = '1' ) then
	  	if ( inputReady = '1' ) then
	  		outputReady <= '1';
	  	else
	  		outputReady <= '0';
	  	end if;	  		
	  end if;
	end process;
end syn;
