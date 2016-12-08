library UNISIM;
use UNISIM.vcomponents.all;
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
signal fifo_rst : STD_LOGIC;
signal FIFO18E1_inst0_DI : STD_LOGIC_VECTOR(31 downto 0);
signal FIFO18E1_inst0_DO : STD_LOGIC_VECTOR(31 downto 0);
signal FIFO18E1_inst0_DIP : STD_LOGIC_VECTOR(3 downto 0);
signal FIFO18E1_inst0_DOP : STD_LOGIC_VECTOR(3 downto 0);
signal FIFO18E1_inst0_FULL : STD_LOGIC;
signal FIFO18E1_inst0_EMPTY : STD_LOGIC;
signal RDEN : std_logic;
signal WREN : std_logic;
begin
process( WClk )
variable rst_buffer : STD_LOGIC_VECTOR(4 downto 0) := (others => '0');
begin
  if( WClk'event and WClk = '1' )
  then
    rst_buffer(4 downto 0) := rst_buffer(3 downto 0) & Clear_in;
    fifo_rst <= rst_buffer(4) and rst_buffer(3) and rst_buffer(2) and rst_buffer(1) and rst_buffer(0);
  end if;
end process;
FIFO18E1_inst0_DI(DATA_SIZE-1 downto 0) <= Data_in(DATA_SIZE-1 downto 0);
Data_out(DATA_SIZE-1 downto 0) <= FIFO18E1_inst0_DO(DATA_SIZE-1 downto 0);
process( WClk )
begin
  if( WClk'event and WClk = '1' )
  then
    Full_out <= FIFO18E1_inst0_FULL;
  end if;
end process;
Empty_out <= FIFO18E1_inst0_EMPTY;
FIFO18E1_inst0 : FIFO18E1 generic map (
  DO_REG => 1, 
  EN_SYN => FALSE, 
  FIFO_MODE => "FIFO18_36", 
  ALMOST_FULL_OFFSET => X"0080", 
  ALMOST_EMPTY_OFFSET => X"0080", 
  DATA_WIDTH => 36, 
  FIRST_WORD_FALL_THROUGH => FALSE) 
port map (
  ALMOSTEMPTY => open, 
  ALMOSTFULL => FIFO18E1_inst0_FULL, 
  DI => FIFO18E1_inst0_DI,
  DO => FIFO18E1_inst0_DO,
  DIP => FIFO18E1_inst0_DIP,
  DOP => FIFO18E1_inst0_DOP,
  EMPTY => FIFO18E1_inst0_EMPTY, 
  FULL => open,
  RDCOUNT => open, 
  RDERR => open, 
  WRCOUNT => open, 
  WRERR => open, 
  REGCE => '1', 
  RSTREG => fifo_rst, 
  RDCLK => RClk, 
  RDEN => RDEN, 
  RST => fifo_rst, 
  WRCLK => WClk, 
  WREN => WREN
);
  RDEN <= ReadEn_in and not fifo_rst; 
  WREN <= WriteEn_in and not fifo_rst;
end architecture;
