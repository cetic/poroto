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
component %%%BROM_NAME%%% IS
  port (
    clka : IN STD_LOGIC;
    ena : IN STD_LOGIC;
    addra : IN STD_LOGIC_VECTOR(%%%ADDR_LEN%%%-1 DOWNTO 0);
    douta : OUT STD_LOGIC_VECTOR(%%%DATA_SIZE%%%-1 DOWNTO 0)
  );
end component;
begin
	brom : %%%BROM_NAME%%% port map ( clka => clk,  ena => inputReady,  addra => address, douta => value );
	done <= '1';
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
