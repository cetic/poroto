 library ieee;
use ieee.std_logic_1164.all;
use ieee.std_logic_unsigned.all;
use ieee.numeric_std.all;

entity bram is
generic (
    DATA    : integer := 32;
    ADDR    : integer := 8
);
port (
    -- Port A
    clka   : in std_logic;
    --rsta   : in std_logic;
    --enb    : in std_logic;
    wea    : in std_logic;
    addra  : in std_logic_vector(ADDR-1 downto 0);
    dina   : in std_logic_vector(DATA-1 downto 0);
    douta  : out std_logic_vector(DATA-1 downto 0);

    -- Port B
    clkb   : in std_logic;
    --rstb   : in std_logic;
    --enb    : in std_logic;
    web    : in std_logic;
    addrb  : in std_logic_vector(ADDR-1 downto 0);
    dinb   : in std_logic_vector(DATA-1 downto 0);
    doutb  : out std_logic_vector(DATA-1 downto 0)
);
end bram;

architecture rtl of bram is
    -- Shared memory
    type mem_type is array ( (2**ADDR)-1 downto 0 ) of std_logic_vector(DATA-1 downto 0);
    shared variable mem : mem_type := (others => (others => '0'));
begin

-- Port A
process(clka)
begin
    if(clka'event and clka='1') then
        if(wea='1') then
            mem(conv_integer(addra)) := dina;
            report "Bram write-a " & integer'image(to_integer(unsigned(dina))) & " at " & integer'image(to_integer(unsigned(addra)));
        end if;
        douta <= mem(conv_integer(addra));
    end if;
end process;

-- Port B
process(clkb)
begin
    if(clkb'event and clkb='1') then
        if(web='1') then
            mem(conv_integer(addrb)) := dinb;
            report "Bram write-b " & integer'image(to_integer(unsigned(dinb))) & " at " & integer'image(to_integer(unsigned(addrb)));
        end if;
        doutb <= mem(conv_integer(addrb));
    end if;
end process;

end rtl;
