LIBRARY ieee;
USE ieee.std_logic_1164.ALL;
USE IEEE.STD_LOGIC_ARITH.ALL;
USE IEEE.STD_LOGIC_SIGNED.ALL;
library work;

entity %%%WRAPPER_NAME%%% is
port (
	clk : in STD_LOGIC;
	rst : in STD_LOGIC;
	inputReady : in STD_LOGIC;
	outputReady : out STD_LOGIC;
	done : out STD_LOGIC;
	stall : in STD_LOGIC;
	enable : in STD_LOGIC;
	address : in STD_LOGIC_VECTOR(%%%ADDR_WIDTH%%%-1 downto 0);
	value : in STD_LOGIC_VECTOR(%%%DATA_SIZE%%%-1 downto 0);
    bram_clk : OUT STD_LOGIC;
    bram_we : OUT STD_LOGIC;
    bram_addr : OUT STD_LOGIC_VECTOR(31 DOWNTO 0);
    bram_din : OUT STD_LOGIC_VECTOR(31 DOWNTO 0);
    dummy_%%%BRAM_NAME%%% : OUT STD_LOGIC_VECTOR(31 DOWNTO 0)
	);
end %%%WRAPPER_NAME%%%;

architecture syn of %%%WRAPPER_NAME%%% is
begin
	bram_clk <= clk;
	bram_we <= inputReady and enable;
	outputReady <= '1';
	done <= '1';
	bram_addr <= (others => '0' );
	bram_addr(%%%ADDR_WIDTH%%%-1 downto 0) <= address(%%%ADDR_WIDTH%%%-2-1 downto 0) & "00";
	bram_din <= %%%EXT%%%(value, bram_din'LENGTH);
	dummy_%%%BRAM_NAME%%% <= ( others => '0' );
end syn;
