library ieee;
use ieee.std_logic_1164.all;
use ieee.std_logic_unsigned.all;
use ieee.std_logic_misc.all;
use ieee.std_logic_arith.all;
use ieee.numeric_std.all;
use work.poroto_pkg.all;

entity input_bram_wrapper is
    generic (
        INPUT_DATA_WIDTH : INTEGER;
        OUTPUT_DATA_WIDTH : INTEGER
    );
	port(
		-- Control interface
		clk           : in  std_logic;
		rst           : in  std_logic;

		-- ROCCC Interface
		full          : in  std_logic;  --full_in (not used) : set to 1 when new data can not be handled by system
		data_ready    : out std_logic;  --write_enable_out : set to 1 when data is valid
		data          : out std_logic_vector(OUTPUT_DATA_WIDTH-1 downto 0); --channel_out : data read
		address       : in  std_logic_vector(31 downto 0); --address_in : address to read
		address_ready : in  std_logic;  --read_in : set to 1 when address is valid and a read is triggered

		-- BRAM Interface
		bram_en       : OUT STD_LOGIC;
		bram_addr     : OUT STD_LOGIC_VECTOR(31 DOWNTO 0);
		bram_dout     : IN  STD_LOGIC_VECTOR(INPUT_DATA_WIDTH-1 DOWNTO 0)
	);
end entity;

architecture syn of input_bram_wrapper is
	signal en_pipeline : STD_LOGIC_VECTOR(1 downto 0);

begin
	bram_en   <= address_ready;
	bram_addr <= address(31 - 2 downto 0) & "00";
 
    L0: if (OUTPUT_DATA_WIDTH > INPUT_DATA_WIDTH) generate
    data(OUTPUT_DATA_WIDTH - 1 downto INPUT_DATA_WIDTH) <= (others => '0');
    data(INPUT_DATA_WIDTH - 1 downto 0) <= bram_dout;
    end generate L0;

    L1: if (INPUT_DATA_WIDTH >= OUTPUT_DATA_WIDTH) generate
        data <= bram_dout(OUTPUT_DATA_WIDTH - 1 downto 0);
    end generate L1;

	action_process : process(clk, address_ready)
	begin
		if rst = '1' then
			data_ready  <= '0';
			en_pipeline <= (others => '0');
		elsif clk'event and clk = '1' then
			data_ready  <= en_pipeline(0);
			en_pipeline <= address_ready & en_pipeline(1);
		end if;
	end process;

end architecture;
