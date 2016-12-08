library IEEE ;
use IEEE.NUMERIC_STD.ALL;
use IEEE.STD_LOGIC_UNSIGNED.all;

use IEEE.STD_LOGIC_1164.all ;
--use IEEE.STD_LOGIC_ARITH.all;

use work.HelperFunctions.all;
use work.HelperFunctions_Unsigned.all;
use work.HelperFunctions_Signed.all;

entity RiffaBramFifo is
  generic (
           ADDRESS_WIDTH      : POSITIVE ;
           DATA_WIDTH         : POSITIVE ;
           ALMOST_FULL_COUNT  : NATURAL ;
           ALMOST_EMPTY_COUNT : NATURAL
         ) ;
  port (
         clk            : in  STD_LOGIC ;
         rst            : in  STD_LOGIC ;
         data_in        : in  STD_LOGIC_VECTOR(DATA_WIDTH-1 downto 0) ;
         valid_in       : in  STD_LOGIC ;
         full_out       : out STD_LOGIC ;
         data_out       : out STD_LOGIC_VECTOR(DATA_WIDTH-1 downto 0) ;
         read_enable_in : in  STD_LOGIC ;
         empty_out      : out STD_LOGIC
       ) ;
end entity;

architecture LBRAM of RiffaBramFifo is

  type RAMType is array(2**ADDRESS_WIDTH-1 downto 0) of STD_LOGIC_VECTOR(DATA_WIDTH-1 downto 0) ;
    
  signal has_data : boolean := false ;
  signal count    : unsigned(ADDRESS_WIDTH downto 0) := (others => '0') ;
  signal ram      : RAMType := (others=>(others=>'0')) ;
  signal full     : boolean ;
  signal empty    : boolean ;
  signal push     : boolean ;
  signal pop      : boolean ;

begin

  empty <= not has_data;
  empty_out <= '1' when count <= (ALMOST_EMPTY_COUNT) else '0';
  full_out <= '1' when (2**ADDRESS_WIDTH-ALMOST_FULL_COUNT <= count) else '0';
  push <= not full and (valid_in = '1');
  pop <= not empty and (read_enable_in = '1');

  process(clk, rst)
    variable rd_addr  : unsigned(ADDRESS_WIDTH-1 downto 0) := (others =>'0') ;
    variable wr_addr  : unsigned(ADDRESS_WIDTH-1 downto 0) := (others =>'0') ;
  begin
    if( rst = '1' ) then
      rd_addr := (others => '0');
      wr_addr := (others => '0');
      has_data <= false;
      count <= (others => '0');
      data_out <= (others => '0');
    elsif( clk'event and clk = '1' ) then
      full <= has_data and (rd_addr = wr_addr);
      if push then
        ram(to_integer(unsigned(wr_addr))) <= data_in;
        wr_addr := wr_addr + 1;
      end if;
      if pop then
        rd_addr := rd_addr + 1;
      end if;
      data_out <= ram(to_integer(unsigned(rd_addr)));
      if (push and not pop) then
        count <= count + 1;
        has_data <= true;
      elsif (not push and pop) then
        count <= count - 1;
        has_data <= (count /= 1);
      end if;
    end if;
  end process;

end architecture LBRAM; 