LIBRARY ieee;
USE ieee.std_logic_1164.ALL;
USE ieee.std_logic_unsigned.all;
use ieee.std_logic_misc.all;
use ieee.numeric_std.all;
use work.poroto_pkg.all;

ENTITY poroto_tb IS
END poroto_tb;

ARCHITECTURE behavior OF poroto_tb IS 
  subtype word_t is std_logic_vector(C_PCI_DATA_WIDTH-1 downto 0);
  type word_vector_t is array(natural range <>) of word_t;

  procedure riffa_channel_write(
    offset              : in natural;
    data                : in word_vector_t;
    last                : in std_logic;      
    signal clk          : in std_logic;      
    signal riffa_m2s    : out poroto_riffa_m2sT;
    signal riffa_s2m    : in poroto_riffa_s2mT
    )
  is
    variable i  : natural;
  begin
    i := 0;

    wait until rising_edge(clk);
    report "Enabling channel";
    riffa_m2s.EN <= '1';
    riffa_m2s.LAST <= '1';
    riffa_m2s.LEN <= std_logic_vector(TO_UNSIGNED(data'length,riffa_m2s.LEN'length));
    riffa_m2s.OFF <= std_logic_vector(TO_UNSIGNED(0,riffa_m2s.OFF'length));   
    riffa_m2s.DATA_VALID <= '0';
    riffa_m2s.DATA <= (others => '0');
    wait until rising_edge(clk) and riffa_s2m.ACK = '1';
    report "Ack received";
    
    while (i /= data'length) loop
      if (riffa_s2m.DATA_REN = '1') then 
        riffa_m2s.DATA_VALID <= '1';
        riffa_m2s.DATA <= data(i);
        i := i + 1;
      end if;  
      wait until rising_edge(clk);
    end loop;
    riffa_m2s.EN <= '0';
    riffa_m2s.DATA_VALID <= '0';
    riffa_m2s.DATA <= (others => '0');
    report "Transfer done";
  end;
  procedure riffa_channel_read(
    signal offset       : out natural;
    signal length       : out natural;
    signal data         : out word_vector_t;
    signal last         : out std_logic;      
    signal clk          : in std_logic;      
    signal riffa_m2s    : in poroto_riffa_m2sT;
    signal riffa_s2m    : out poroto_riffa_s2mT
    )
  is
    variable i  : natural;
    variable len  : natural;
  begin
    i := 0;
    riffa_s2m.DATA_REN <= '0';
    riffa_s2m.ACK <= '0';
    wait until rising_edge(clk) and riffa_m2s.EN = '1';
    riffa_s2m.ACK <= '1';
    offset <= to_integer(unsigned(riffa_m2s.OFF));
    len := to_integer(unsigned(riffa_m2s.LEN));
    length <= len;
    last <= riffa_m2s.LAST;
    report "Channel enabled, receiving " & integer'image(len) & " words, expecting " & integer'image(data'length);
    wait until rising_edge(clk);
    report "Ack sent";
    riffa_s2m.ACK <= '0';
    riffa_s2m.DATA_REN <= '1';
    report "Activating REN";
    wait until rising_edge(clk);
    while (i /= len) loop
      if (riffa_m2s.DATA_VALID = '1') then 
        report "Received Data: " & integer'image(to_integer(signed(riffa_m2s.DATA))) & " from " & integer'image(i);
        data(i) <= riffa_m2s.DATA;
        i := i + 1;
      end if;  
      wait until rising_edge(clk);
    end loop;
    riffa_s2m.DATA_REN <= '0';
    report "Transfer done";
  end;

  procedure verify_memory(
    signal data         : in word_vector_t;
    signal len          : in natural;
    signal expected     : in word_vector_t;
    signal test_ok      : out boolean
  )
  is
    variable i  : natural;
  begin
     check_output: for i in 0 to len-1
     loop
        if data(i) /= expected(i) then
           report "Received Data at " & integer'image(i) & " : " & integer'image(to_integer(signed(data(i)))) & " Expected: " & integer'image(to_integer(signed(expected(i))));
           test_ok <= false;
        end if;
      end loop;
  end;

    component poroto is
        port(
            rst                 : in std_logic;
            clk                 : in std_logic;
            riffa_rx_en         : in sig_array(0 to MEM_BRAMS);
            riffa_rx_last       : in sig_array(0 to MEM_BRAMS);
            riffa_rx_len        : in vect32_array(0 to MEM_BRAMS);
            riffa_rx_off        : in vect31_array(0 to MEM_BRAMS);
            riffa_rx_data       : in vect_pcidatawidth_array(0 to MEM_BRAMS);
            riffa_rx_data_valid : in sig_array(0 to MEM_BRAMS);
            riffa_rx_ack        : out sig_array(0 to MEM_BRAMS);
            riffa_rx_data_ren   : out sig_array(0 to MEM_BRAMS);

            riffa_tx_en         : out sig_array(0 to MEM_BRAMS);
            riffa_tx_last       : out sig_array(0 to MEM_BRAMS);
            riffa_tx_len        : out vect32_array(0 to MEM_BRAMS);
            riffa_tx_off        : out vect31_array(0 to MEM_BRAMS);
            riffa_tx_data       : out vect_pcidatawidth_array(0 to MEM_BRAMS);
            riffa_tx_data_valid : out sig_array(0 to MEM_BRAMS);
            riffa_tx_ack        : in sig_array(0 to MEM_BRAMS);
            riffa_tx_data_ren   : in sig_array(0 to MEM_BRAMS)
        );
    end component;
    
  -- TB Signals
  signal clk : STD_LOGIC := '0';
  signal rst : STD_LOGIC := '1';
  signal test_passed : boolean := false;
  signal test_ok     : boolean := true;

  -- Clock period definitions
  constant clk_period : time := 1 ns;

  signal riffa_rx_en         : sig_array(0 to MEM_BRAMS);
  signal riffa_rx_last       : sig_array(0 to MEM_BRAMS);
  signal riffa_rx_len        : vect32_array(0 to MEM_BRAMS);
  signal riffa_rx_off        : vect31_array(0 to MEM_BRAMS);
  signal riffa_rx_data       : vect_pcidatawidth_array(0 to MEM_BRAMS);
  signal riffa_rx_data_valid : sig_array(0 to MEM_BRAMS);
  signal riffa_rx_ack        : sig_array(0 to MEM_BRAMS);
  signal riffa_rx_data_ren   : sig_array(0 to MEM_BRAMS);

  signal riffa_tx_en         : sig_array(0 to MEM_BRAMS);
  signal riffa_tx_last       : sig_array(0 to MEM_BRAMS);
  signal riffa_tx_len        : vect32_array(0 to MEM_BRAMS);
  signal riffa_tx_off        : vect31_array(0 to MEM_BRAMS);
  signal riffa_tx_data       : vect_pcidatawidth_array(0 to MEM_BRAMS);
  signal riffa_tx_data_valid : sig_array(0 to MEM_BRAMS);
  signal riffa_tx_ack        : sig_array(0 to MEM_BRAMS);
  signal riffa_tx_data_ren   : sig_array(0 to MEM_BRAMS);

  signal riffa_rx_m2s : poroto_riffa_m2sT_array(0 to MEM_BRAMS);
  signal riffa_rx_s2m : poroto_riffa_s2mT_array(0 to MEM_BRAMS);
  signal riffa_tx_m2s : poroto_riffa_m2sT_array(0 to MEM_BRAMS);
  signal riffa_tx_s2m : poroto_riffa_s2mT_array(0 to MEM_BRAMS);

    signal registers_reset : word_vector_t(0 to 1) := (
      std_logic_vector(to_unsigned(1, C_PCI_DATA_WIDTH)),
      std_logic_vector(to_unsigned(1, C_PCI_DATA_WIDTH))
    );
  
  -- %%%SIGNALS%%%
  
  BEGIN
    ent_portmap : for i in 0 to MEM_BRAMS generate
        riffa_rx_en(i) <= riffa_rx_m2s(i).EN;
        riffa_rx_last(i) <= riffa_rx_m2s(i).LAST;
        riffa_rx_len(i) <= riffa_rx_m2s(i).LEN;
        riffa_rx_off(i) <= riffa_rx_m2s(i).OFF;
        riffa_rx_data(i) <= riffa_rx_m2s(i).DATA;
        riffa_rx_data_valid(i) <= riffa_rx_m2s(i).DATA_VALID;
        riffa_rx_s2m(i).ACK <= riffa_rx_ack(i);
        riffa_rx_s2m(i).DATA_REN <= riffa_rx_data_ren(i);

        riffa_tx_m2s(i).EN <= riffa_tx_en(i);
        riffa_tx_m2s(i).LAST <= riffa_tx_last(i);
        riffa_tx_m2s(i).LEN <= riffa_tx_len(i);
        riffa_tx_m2s(i).OFF <= riffa_tx_off(i);
        riffa_tx_m2s(i).DATA <= riffa_tx_data(i);
        riffa_tx_m2s(i).DATA_VALID <= riffa_tx_data_valid(i);
        riffa_tx_ack(i) <= riffa_tx_s2m(i).ACK;
        riffa_tx_data_ren(i) <= riffa_tx_s2m(i).DATA_REN;
    end generate;

    uut : poroto
    port map (
           clk => clk,
           rst => rst,
           riffa_rx_en => riffa_rx_en,
           riffa_rx_last => riffa_rx_last,
           riffa_rx_len => riffa_rx_len,
           riffa_rx_off => riffa_rx_off,
           riffa_rx_data => riffa_rx_data,
           riffa_rx_data_valid => riffa_rx_data_valid,
           riffa_rx_ack => riffa_rx_ack,
           riffa_rx_data_ren => riffa_rx_data_ren,

           riffa_tx_en => riffa_tx_en,
           riffa_tx_last => riffa_tx_last,
           riffa_tx_len => riffa_tx_len,
           riffa_tx_off => riffa_tx_off,
           riffa_tx_data => riffa_tx_data,
           riffa_tx_data_valid => riffa_tx_data_valid,
           riffa_tx_ack => riffa_tx_ack,
           riffa_tx_data_ren => riffa_tx_data_ren
    );
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
      wait for clk_period * 10;
      rst <= '0';

      -- %%%STIMULATE%%%

      test_passed <= true;
      if (test_ok) then
        report "Test of design completed: PASSED.";
      else
        assert false report "Test of design completed: FAILED." severity failure;
      end if;
      wait;
    end process;

  END behavior;