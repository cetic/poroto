LIBRARY ieee;
USE ieee.std_logic_1164.ALL;
USE ieee.std_logic_unsigned.all;
USE ieee.numeric_std.ALL;

use work.HelperFunctions.all;
use work.HelperFunctions_Unsigned.all;
use work.HelperFunctions_Signed.all;

entity SynchInterfaceGeneric is
    generic (
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
end SynchInterfaceGeneric;

architecture Handwritten of SynchInterfaceGeneric is

    type State is (ST0, ST1, ST2);
    signal currentState : State;
    signal data_internal : std_logic_vector(OUTPUT_DATA_WIDTH - 1 downto 0);

begin

    L0: if (OUTPUT_DATA_WIDTH > INPUT_DATA_WIDTH) generate
    data_internal(OUTPUT_DATA_WIDTH - 1 downto INPUT_DATA_WIDTH) <= (others => '0');
    data_internal(INPUT_DATA_WIDTH - 1 downto 0) <= data_in ;
    end generate L0;

    L1: if (INPUT_DATA_WIDTH >= OUTPUT_DATA_WIDTH) generate
        data_internal <= data_in(OUTPUT_DATA_WIDTH - 1 downto 0);
    end generate L1;

    stallAddress <= mc_stall_in;

    process(clk, rst)
    begin
        if (rst = '1') then
            mc_vadr_out <= (others => '0');
            mc_valid_out <= '0';
            mc_data_out <= (others => '0');
            data_read <= '0';
            addressPop <= '0';

            currentState <= ST0;

        elsif (clk'event and clk = '1') then

            data_read <= '0' ;
            addressPop <= '0' ;
            mc_valid_out <= '0';

            case currentState is
                when ST0 =>
                    if (mc_stall_in = '0' and data_empty = '0' and address_valid = '1')
                    then
                        data_read <= '1';
                        currentState <= ST1;
                    end if;
                when ST1 =>
                    currentState <= ST2;
                when ST2 =>
                    addressPop <= '1';
                    mc_vadr_out <= address_in;
                    mc_valid_out <= '1';
                    mc_data_out <= data_internal;
                    currentState <= ST0;
                when others =>
                    currentState <= ST0;
            end case;
        end if;
    end process;

end Handwritten;
