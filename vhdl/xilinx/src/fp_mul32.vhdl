library IEEE;
use IEEE.STD_LOGIC_1164.ALL;

use IEEE.NUMERIC_STD.ALL;
use IEEE.STD_LOGIC_UNSIGNED.ALL;

entity fp_mul32 is
port (
    clk : in STD_LOGIC;
    rst : in STD_LOGIC;
    inputReady : in STD_LOGIC;
    outputReady : out STD_LOGIC;
    done : out STD_LOGIC;
    stall : in STD_LOGIC;
    a : in STD_LOGIC_VECTOR(31 downto 0);
    b : in STD_LOGIC_VECTOR(31 downto 0);
    result : out STD_LOGIC_VECTOR(31 downto 0)
    );
end fp_mul32;

architecture behavioral of fp_mul32 is

    COMPONENT fp_mul32_impl
      PORT (
        a : IN STD_LOGIC_VECTOR(31 DOWNTO 0);
        b : IN STD_LOGIC_VECTOR(31 DOWNTO 0);
        operation_nd : IN STD_LOGIC;
        operation_rfd : OUT STD_LOGIC;
        clk : IN STD_LOGIC;
        sclr : IN STD_LOGIC;
        ce : IN STD_LOGIC;
        result : OUT STD_LOGIC_VECTOR(31 DOWNTO 0);
        rdy : OUT STD_LOGIC
      );
    END COMPONENT;

    --signals
    signal ce_sig               : std_logic;
    
begin

    floating_point_inst: fp_mul32_impl
      PORT MAP (
        a => a,
        b => b,
        operation_nd => inputReady,
        operation_rfd => open, 
        clk => clk,
        sclr => rst,
        ce => ce_sig,
        result => result,
        rdy => outputReady
      );

    ce_sig <= not(stall);

  
end  behavioral;