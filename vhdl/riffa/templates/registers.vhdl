library ieee;
use ieee.std_logic_1164.all;
use ieee.std_logic_unsigned.all;
use ieee.numeric_std.all;

library work;
use work.poroto_pkg.all;

entity registers is
    port(
        clk          : in  std_logic;
        rst          : in  std_logic;
        bram_m2s : in poroto_bram_m2sT;
        bram_s2m : out poroto_bram_s2mT;
        -- RIFFA Remote Control
        riffa_ctrl   : out poroto_riffa_ctrl_array_t(0 to MEM_BRAMS);
        --On-board BRAM interface
        bram_app_m2s : out poroto_bram_m2sT_array(0 to MEM_BRAMS - 1);
        bram_app_s2m : in  poroto_bram_s2mT_array(0 to MEM_BRAMS - 1)
    );
end registers;

---%%%MEMMAP%%%

architecture rtl of registers is
    --------------------------------------------------------------
    -- ROCCC Application data                                   --
    -------------------------------------------------------------- 
    --%%%SIGNALS%%%
    signal usr_clk : std_logic;

    ----------------------------
    -- Application components --
    ----------------------------
    -- %%%COMPONENTS%%%

    -----------------------
    -- Helper components --
    -----------------------
    component input_bram_wrapper is
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
    end component;

    component output_bram_wrapper is
        port(
            -- Control interface
            clk             : in  std_logic;
            rst             : in  std_logic;

            -- ROCCC Interface
            done_in         : in  STD_LOGIC;
            empty_in        : in  STD_LOGIC;
            read_enable_out : out STD_LOGIC;
            channel_in      : in  STD_LOGIC_VECTOR(31 downto 0);
            address_in      : in  STD_LOGIC_VECTOR(31 downto 0);
            read_in         : in  STD_LOGIC;

            -- BRAM Interface   
            bram_en         : OUT STD_LOGIC;
            bram_addr       : OUT STD_LOGIC_VECTOR(31 DOWNTO 0);
            bram_din        : OUT STD_LOGIC_VECTOR(31 DOWNTO 0)
        );
    end component;
    component SpecialBurstAddressGen1Channels is
        port(
            clk                       : in  STD_LOGIC;
            rst                       : in  STD_LOGIC;

            burst_address_in          : in  STD_LOGIC_VECTOR(31 downto 0);
            burst_count_in            : in  STD_LOGIC_VECTOR(31 downto 0);
            burst_valid_in            : in  STD_LOGIC;
            burst_stall_out           : out STD_LOGIC;

            address_valid_out         : out STD_LOGIC;
            address_stall_channel0_in : in  STD_LOGIC;

            address_channel0_out      : out STD_LOGIC_VECTOR(31 downto 0)
        );
    end component;
    component MicroFifo is
        generic(
            ADDRESS_WIDTH      : POSITIVE;
            DATA_WIDTH         : POSITIVE;
            ALMOST_FULL_COUNT  : NATURAL;
            ALMOST_EMPTY_COUNT : NATURAL
        );
        port(
            clk            : in  STD_LOGIC;
            rst            : in  STD_LOGIC;
            data_in        : in  STD_LOGIC_VECTOR(DATA_WIDTH - 1 downto 0);
            valid_in       : in  STD_LOGIC;
            full_out       : out STD_LOGIC;
            data_out       : out STD_LOGIC_VECTOR(DATA_WIDTH - 1 downto 0);
            read_enable_in : in  STD_LOGIC;
            empty_out      : out STD_LOGIC
        );
    end component;
    component SynchInterfaceGeneric is
        generic(
            INPUT_DATA_WIDTH  : INTEGER;
            OUTPUT_DATA_WIDTH : INTEGER
        );
        port(
            clk           : in  STD_LOGIC;
            rst           : in  STD_LOGIC;
            data_in       : in  STD_LOGIC_VECTOR(INPUT_DATA_WIDTH - 1 downto 0);
            data_empty    : in  STD_LOGIC;
            data_read     : out STD_LOGIC;
            address_in    : in  STD_LOGIC_VECTOR(31 downto 0);
            address_valid : in  STD_LOGIC;
            stallAddress  : out STD_LOGIC;
            addressPop    : out STD_LOGIC;
            mc_stall_in   : in  STD_LOGIC;
            mc_vadr_out   : out STD_LOGIC_VECTOR(31 downto 0);
            mc_valid_out  : out STD_LOGIC;
            mc_data_out   : out STD_LOGIC_VECTOR(OUTPUT_DATA_WIDTH - 1 downto 0)
        );
    end component;

begin

    --Temporary until clock name is refactored
    
    usr_clk <= clk;
    ---------------------------------------------------------------
    -- Generate application result ready                         --
    ---------------------------------------------------------------
    gen_resultReady : process(rst, clk)
    begin
        if rst = '1' then
        --%%%RESET_RESULT_READY%%%
        elsif rising_edge(clk) then
        --%%%RESULT_READY%%%
        end if;
    end process;

    -----------------------------
    -- Registers management  ----
    -----------------------------
    register_proc : process(clk)
    begin
        if (clk'event and clk = '1') then
            --%%%WRITE_REGS%%%
            if (bram_m2s.re = '1') then
                case bram_m2s.addr_r is
                    --%%%READ_REGS%%%
                end case; 
            end if;
        end if;
    end process;

  ---------------------------
  -- Application interface --
  ---------------------------
  -- %%%INTERFACES%%%

end rtl;
