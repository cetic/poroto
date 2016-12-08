library ieee;
use ieee.std_logic_1164.all;
use ieee.std_logic_unsigned.all;

entity InferredBRAMFifo32 is
  generic (DATA_DEPTH : integer);
  port(
    Data_out : out std_logic_vector(31 downto 0);
    Empty_out : out std_logic;
    ReadEn_in : in std_logic;
    RClk : in std_logic;
    Data_in : in std_logic_vector(31 downto 0);
    Full_out : out std_logic;
    WriteEn_in : in std_logic;
    WClk : in std_logic;
    Clear_in : in std_logic
  );
end entity;

architecture rtl of InferredBRAMFifo32 is
COMPONENT hw_fifo_32
  PORT (
    clk : IN STD_LOGIC;
    rst : IN STD_LOGIC;
    din : IN STD_LOGIC_VECTOR(31 DOWNTO 0);
    wr_en : IN STD_LOGIC;
    rd_en : IN STD_LOGIC;
    dout : OUT STD_LOGIC_VECTOR(31 DOWNTO 0);
    full : OUT STD_LOGIC;
    empty : OUT STD_LOGIC
  );
END COMPONENT;

begin
	fifo : hw_fifo_32 port map (dout => Data_out, empty => Empty_out, rd_en => ReadEn_in, clk => WClk, din => Data_in, full => Full_out, wr_en => WriteEn_in, rst => Clear_in);
	
end architecture;
