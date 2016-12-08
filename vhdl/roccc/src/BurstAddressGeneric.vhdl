LIBRARY ieee;
USE ieee.std_logic_1164.ALL;
USE ieee.std_logic_unsigned.all;
USE ieee.numeric_std.ALL;

use work.HelperFunctions.all;
use work.HelperFunctions_Unsigned.all;
use work.HelperFunctions_Signed.all;

entity SpecialBurstAddressGen1Channels is
	port(
		clk : in STD_LOGIC;
		rst : in STD_LOGIC;

		burst_address_in : in STD_LOGIC_VECTOR(31 downto 0);
		burst_count_in : in STD_LOGIC_VECTOR(31 downto 0);
		burst_valid_in : in STD_LOGIC;
		burst_stall_out : out STD_LOGIC;

		address_valid_out : out STD_LOGIC;
		address_stall_channel0_in : in STD_LOGIC;

		address_channel0_out : out STD_LOGIC_VECTOR(31 downto 0)
		);
end SpecialBurstAddressGen1Channels;

architecture Generated of SpecialBurstAddressGen1Channels is

	component MicroFifo is
	generic (
		ADDRESS_WIDTH : POSITIVE;
		DATA_WIDTH : POSITIVE;
		ALMOST_FULL_COUNT : NATURAL;
		ALMOST_EMPTY_COUNT : NATURAL
	);
	port(
		clk : in STD_LOGIC;
		rst : in STD_LOGIC;
		data_in : in STD_LOGIC_VECTOR(DATA_WIDTH-1 downto 0);
		valid_in : in STD_LOGIC;
		full_out : out STD_LOGIC;
		data_out : out STD_LOGIC_VECTOR(DATA_WIDTH-1 downto 0);
		read_enable_in : in STD_LOGIC;
		empty_out : out STD_LOGIC
	);
	end component;

	signal base_value : std_logic_vector(31 downto 0);
	signal burst_value : std_logic_vector(31 downto 0);
	signal micro_read_enable_in : std_logic;
	signal micro_empty_out : std_logic;

	type STATE_TYPE is (S_READY, S_READ, S_POP);

	signal state : STATE_TYPE;

	signal cur_address : std_logic_vector(31 downto 0);
	signal end_address : std_logic_vector(31 downto 0);
begin

	micro_lilo : MicroFifo
		generic map(
				ADDRESS_WIDTH => 4,
				DATA_WIDTH => 64,
				ALMOST_FULL_COUNT => 3,
				ALMOST_EMPTY_COUNT => 0
			)
		port map(
			clk => clk,
			rst => rst,
			data_in(31 downto 0) => burst_address_in,
			data_in(63 downto 32) => burst_count_in,
			valid_in => burst_valid_in,
			full_out => burst_stall_out,
			data_out(31 downto 0) => base_value,
			data_out(63 downto 32) => burst_value,
			read_enable_in => micro_read_enable_in,
			empty_out => micro_empty_out
		);

	process(clk, rst)
	begin
		if (rst = '1') then
			address_valid_out <= '0';
			address_channel0_out <= (others => '0');
			cur_address <= (others => '0');
			end_address <= (others => '0');
			micro_read_enable_in <= '0';
			state <= S_READY;

		elsif (clk'event and clk ='1') then
			address_valid_out <= '0';
			micro_read_enable_in <= '0';

			case state is

				when S_READY =>

					if(micro_empty_out = '0') then
						state <= S_POP;
						micro_read_enable_in <= '1';
					else
						state <= S_READY;
					end if;

				when S_POP =>
					cur_address <= base_value;
					end_address <= ROCCCADD(base_value, burst_value, 32);
					state <= S_READ;
				when S_READ =>

					if(address_stall_channel0_in = '0') then
						address_valid_out <= '1';
						address_channel0_out <= cur_address;
						cur_address <= ROCCCADD(cur_address, x"00000001", 32);
						if(ROCCCADD(cur_address, x"00000001", 32) >= end_address) then
						if(micro_empty_out = '0') then
							state <= S_POP;
							micro_read_enable_in <= '1';
						else
							state <= S_READY;
						end if;
					else
						state <= S_READ;
					end if;
				else
					state <= S_READ;
				end if;

			when others =>
				state <= S_READY;
		end case;
		end if;
	end process;

end Generated;
