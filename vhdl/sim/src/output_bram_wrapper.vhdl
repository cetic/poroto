library ieee;
use ieee.std_logic_1164.all;
use ieee.std_logic_unsigned.all;
use ieee.std_logic_misc.all;
use ieee.std_logic_arith.all;
use ieee.numeric_std.all;
use work.poroto_pkg.all;

entity output_bram_wrapper is
	port(
		-- Control interface
		clk         : in  std_logic;
		rst         : in  std_logic;

		-- ROCCC Interface
        done_in     : in STD_LOGIC;
        empty_in    : in STD_LOGIC;
        read_enable_out : out STD_LOGIC;
        channel_in : in STD_LOGIC_VECTOR(31 downto 0);
        address_in : in STD_LOGIC_VECTOR(31 downto 0);
        read_in : in STD_LOGIC;

		-- BRAM Interface
		bram_en     : OUT STD_LOGIC;
		bram_addr   : OUT STD_LOGIC_VECTOR(31 DOWNTO 0);
		bram_din    : OUT STD_LOGIC_VECTOR(31 DOWNTO 0)
	);
end entity;

architecture syn of output_bram_wrapper is
  type BRAM_STATE_TYPE is (S_EMPTY, S_READY, S_READ);
  signal bram_state : BRAM_STATE_TYPE;
begin
  process(clk, rst)
  begin
    if( rst = '1' ) then
		bram_state <= S_EMPTY;
		read_enable_out <= '0';
		bram_en           <= '0';
		bram_addr         <= (others => '0');
		bram_din          <= (others => '0');
    elsif( clk'event and clk = '1' ) then
		read_enable_out <= '0';
	    case bram_state is
		  when S_EMPTY =>
			 if( Empty_in = '0' ) then
			   read_enable_out <= '1';
				bram_state <= S_READY;
			 end if;
		  when S_READY =>
			 read_enable_out <= '1';
			 bram_state <= S_READ;
		  when S_READ =>
			 --read?
			 if( Empty_in = '0' ) then
			   read_enable_out <= '1';
			 else
			   bram_state <= S_EMPTY;
			 end if;
		  when others =>
			 bram_state <= S_EMPTY;
		end case;
		if( read_in = '1' ) then
			bram_en <= '1';
			bram_addr <= address_in;
			bram_din <= channel_in;
		else
			bram_en <= '0';
			bram_addr <= (others => '0');
			bram_din <= (others => '0');
        end if;
    end if;
  end process;
end architecture;
