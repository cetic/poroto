library ieee;
use ieee.std_logic_1164.all;
use ieee.std_logic_unsigned.all;

entity InferredBRAMFifo is
  generic (
      DATA_SIZE : integer := 32;
      DATA_DEPTH : integer := 8
  );
  port(
    Data_out : out std_logic_vector(DATA_SIZE-1 downto 0);
    Empty_out : out std_logic;
    ReadEn_in : in std_logic;
    RClk : in std_logic;
    Data_in : in std_logic_vector(DATA_SIZE-1 downto 0);
    Full_out : out std_logic;
    WriteEn_in : in std_logic;
    WClk : in std_logic;
    Clear_in : in std_logic
  );
end entity;

architecture rtl of InferredBRAMFifo is
    component module_fifo_regs_with_flags is
      generic (
        g_WIDTH    : natural := 8;
        g_DEPTH    : integer := 32;
        g_AF_LEVEL : integer := 28;
        g_AE_LEVEL : integer := 4
        );
      port (
        i_rst_sync : in std_logic;
        i_clk      : in std_logic;
     
        -- FIFO Write Interface
        i_wr_en   : in  std_logic;
        i_wr_data : in  std_logic_vector(g_WIDTH-1 downto 0);
        o_af      : out std_logic;
        o_full    : out std_logic;
     
        -- FIFO Read Interface
        i_rd_en   : in  std_logic;
        o_rd_data : out std_logic_vector(g_WIDTH-1 downto 0);
        o_ae      : out std_logic;
        o_empty   : out std_logic
        );
    end component;
    signal RDEN : std_logic;
    signal WREN : std_logic;
    signal fifo_rst : STD_LOGIC;
begin
      module_fifo_regs_with_flags_i : module_fifo_regs_with_flags
      generic map (
        g_WIDTH    => DATA_SIZE,
        g_DEPTH    => 256,
        g_AF_LEVEL => 128,
        g_AE_LEVEL => 128
        )
      port map (
        i_rst_sync => fifo_rst,
        i_clk      => RClk,
     
        -- FIFO Write Interface
        i_wr_en   => WREN,
        i_wr_data => Data_in,
        o_af      => full_out,
        o_full    => open,
     
        -- FIFO Read Interface
        i_rd_en   => RDEN,
        o_rd_data => Data_out,
        o_ae      => open,
        o_empty   => Empty_out
        );
    
    process( WClk )
        variable rst_buffer : STD_LOGIC_VECTOR(4 downto 0) := (others => '0');
    begin
        if( WClk'event and WClk = '1' )
        then
            rst_buffer(4 downto 0) := rst_buffer(3 downto 0) & Clear_in;
            fifo_rst <= rst_buffer(4) and rst_buffer(3) and rst_buffer(2) and rst_buffer(1) and rst_buffer(0);
        end if;
    end process;
    RDEN <= ReadEn_in and not fifo_rst; 
    WREN <= WriteEn_in and not fifo_rst;
end architecture;
