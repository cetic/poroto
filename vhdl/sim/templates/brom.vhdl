library ieee;
use ieee.std_logic_1164.all;
use ieee.std_logic_unsigned.all;
use ieee.numeric_std.all;

entity %%%NAME%%% is
port (
    clk   : in std_logic;
    --rst   : in std_logic;
    --en    : in std_logic;
    addr  : in std_logic_vector(%%%ADDR_LEN%%%-1 downto 0);
    dout  : out std_logic_vector(%%%DATA_SIZE%%%-1 downto 0)
);
end %%%NAME%%%;

architecture rtl of %%%NAME%%% is
    type mem_type is array ( (2**%%%ADDR_LEN%%%)-1 downto 0 ) of std_logic_vector(%%%DATA_SIZE%%%-1 downto 0);
    -- Shared memory
    shared variable mem : mem_type := (
        %%%DATA%%%
    );
begin

process(clk)
begin
    if(clk'event and clk='1') then
        dout <= mem(conv_integer(addr));
    end if;
end process;

end rtl;
