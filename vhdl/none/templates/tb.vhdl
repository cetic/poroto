LIBRARY ieee;
USE ieee.std_logic_1164.ALL;
USE ieee.numeric_std.ALL;

package output_memory_types is
constant MAX_CHANNEL_BITWIDTH : integer := 32;
type t_2D_output_memory_type is array (natural range<>, natural range<>) of std_logic_vector(MAX_CHANNEL_BITWIDTH - 1 downto 0);
type t_1D_output_memory_type is array (natural range<>) of std_logic_vector(MAX_CHANNEL_BITWIDTH - 1 downto 0);
end package;

LIBRARY ieee;
USE ieee.std_logic_1164.ALL;
USE ieee.std_logic_unsigned.all;
use ieee.std_logic_misc.all;
use ieee.numeric_std.all;
USE work.output_memory_types.ALL;
use work.poroto_pkg.all;

ENTITY poroto_tb IS
END poroto_tb;

ARCHITECTURE behavior OF poroto_tb IS

	-- %%%COMPONENTS%%%
	-- %%%MEM_COMPONENTS%%%
	
	component SpecialBurstAddressGen1Channels is
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
end component;
	
    -- %%%SIGNALS%%%
    --TODO

  signal bram_app_m2s : poroto_bram_m2sT_array(0 to MEM_BRAMS-1);
  signal bram_app_s2m : poroto_bram_s2mT_array(0 to MEM_BRAMS-1) := (others => POROTO_BRAM_DEFAULT_S2M);
    
  -- TB Signals
  signal clk : STD_LOGIC := '0';
  signal rst : STD_LOGIC := '1';
  signal test_passed : boolean := false;

  -- Clock period definitions
  constant clk_period : time := 1 ns;

  component InputStream is
    generic (
      CHANNEL_BITWIDTH: integer;
      NUM_CHANNELS : integer;
      CONCURRENT_MEM_ACCESS : integer;
      NUM_MEMORY_ELEMENTS : integer;
      STREAM_NAME : string
      );
    port (
      clk : in STD_LOGIC;
      rst : in STD_LOGIC;
      full_in : in STD_LOGIC;
      write_enable_out : out STD_LOGIC;
      channel_out : out STD_LOGIC_VECTOR(NUM_CHANNELS * CHANNEL_BITWIDTH - 1 downto 0);
      address_in : in STD_LOGIC_VECTOR(NUM_CHANNELS * 32 - 1 downto 0);
      read_in : in STD_LOGIC;
      memory : in STD_LOGIC_VECTOR(NUM_MEMORY_ELEMENTS * CHANNEL_BITWIDTH - 1 downto 0)
      );
    end component;

  component OutputStream is
    generic (
      CHANNEL_BITWIDTH: integer;
      NUM_MEMORY_ELEMENTS: integer;
      NUM_CHANNELS : integer;
      STREAM_NAME: string
      );
    port (
      clk : in STD_LOGIC;
      rst : in STD_LOGIC;
      done_in : in STD_LOGIC;
      empty_in : in STD_LOGIC;
      read_enable_out : out STD_LOGIC;
      channel_in : in STD_LOGIC_VECTOR((NUM_CHANNELS * CHANNEL_BITWIDTH) - 1 downto 0);
      address_in : in STD_LOGIC_VECTOR(NUM_CHANNELS * 32 - 1 downto 0);
      read_in : in STD_LOGIC;
      OUTPUT_CORRECT : in t_1D_output_memory_type(0 to NUM_MEMORY_ELEMENTS - 1);
      output_status : out STD_LOGIC
      );
    end component;

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

    function TO_STRING(VALUE : STD_LOGIC_VECTOR) return STRING is
      alias ivalue : STD_LOGIC_VECTOR(1 to value'length) is value;
      variable result : STRING(1 to value'length);
    begin
      if value'length < 1 then
        return "";
      else
        for i in ivalue'range loop
          if ivalue(i) = '0' then
            result(i) := '0';
          else
            result(i) := '1';
          end if;
        end loop;
        return result;
      end if;
    end function to_string;

    function TO_STRING(VALUE : STD_LOGIC) return STRING is
    begin
      if( VALUE = '0') then
        return "0";
      elsif( VALUE = '1') then
        return "1";
      elsif( VALUE = 'X' ) then
        return "X";
      elsif( VALUE = 'U' ) then
        return "U";
      else
        return "N";
      end if;
    end function TO_STRING;

    component SynchInterfaceGeneric is
    generic(
      INPUT_DATA_WIDTH : INTEGER;
      OUTPUT_DATA_WIDTH : INTEGER
    );
    port (
      clk : in STD_LOGIC;
      rst : in STD_LOGIC;
      data_in : in STD_LOGIC_VECTOR(INPUT_DATA_WIDTH - 1 downto 0);
      data_empty : in STD_LOGIC;
      data_read : out STD_LOGIC;
      address_in : in STD_LOGIC_VECTOR(31 downto 0);
      address_valid : in STD_LOGIC;
      stallAddress : out STD_LOGIC;
      addressPop : out STD_LOGIC;
      mc_stall_in : in STD_LOGIC;
      mc_vadr_out : out STD_LOGIC_VECTOR(31 downto 0);
      mc_valid_out : out STD_LOGIC;
      mc_data_out : out STD_LOGIC_VECTOR(OUTPUT_DATA_WIDTH - 1 downto 0)
    );
    end component;

  BEGIN

    -- %%%PORTMAPS%%%
    -- %%%MEMORY%%%

    -- Clock Process Definition
    clk_process : process
    begin
      clk <= '0';
      wait for clk_period / 2;
      clk <= '1';
      wait for clk_period / 2;
      if (test_passed) then
          wait;
      end if;
    end process;

    -- Stimulus Process
    stim_proc : process
    begin
      wait until clk'event and clk = '1';

      -- %%%STIMULATE%%%

      wait;
    end process;

    OutputProcess : process
    begin
      -- %%%VERIFY%%%
      test_passed <= true;
      wait for clk_period;
      if (test_passed) then
        report "Test of design completed: PASSED.";
      else
        assert false report "Test of design completed: FAILED." severity failure;
      end if;
      wait;
    end process;

  END behavior;