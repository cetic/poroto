library IEEE;
use IEEE.STD_LOGIC_1164.ALL;

use IEEE.NUMERIC_STD.ALL;
use IEEE.STD_LOGIC_UNSIGNED.ALL;

library work;
use work.poroto_pkg.all;

entity riffa_bram is
    generic(C_PCI_DATA_WIDTH : integer := 64);
    port(
        CLK                : in  std_logic;
        RST                : in  std_logic;
        
        -- RIFFA channel interface: RX
        riffa_rx_m2s       : in poroto_riffa_m2sT;
        riffa_rx_s2m       : out poroto_riffa_s2mT;
        -- RIFFA channel interface: TX
        riffa_tx_m2s       : out poroto_riffa_m2sT;
        riffa_tx_s2m       : in poroto_riffa_s2mT;
        -- RIFFA remote control
        riffa_ctrl         : poroto_riffa_ctrl_t;
        -- BRAM BUS Interface
        bram_m2s           : out poroto_bram_m2sT;
        bram_s2m           : in poroto_bram_s2mT);
end riffa_bram;

architecture behavioral of riffa_bram is    
    -- global state
    signal in_receive    : std_logic;
    signal in_transmit   : std_logic;
    
    -- RX from RIFFA channel interface
    type rxchnl_state_type is (RX_CHNL_IDLE, RX_CHNL_READY, RX_CHNL_RUN);
    signal rxchnl_state : rxchnl_state_type;
    signal rCount       : std_logic_vector(31 downto 0);
    signal rAddr        : std_logic_vector(31 downto 0);

    -- TX to RIFFA channel interface
    type txchnl_state_type is (TX_CHNL_IDLE, TX_CHNL_START, TX_CHNL_READY, TX_CHNL_RUN);
    signal txchnl_state : txchnl_state_type;
    signal tCount       : std_logic_vector(31 downto 0);
    signal tAddr        : std_logic_vector(31 downto 0);
    signal txEn         : std_logic;
    signal txLast       : std_logic;
    signal txLen        : std_logic_vector(31 downto 0);
    signal txOffset     : std_logic_vector(30 downto 0);

    signal en_pipeline  : STD_LOGIC_VECTOR(2 downto 0);

    component RiffaBramFifo is
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
    end component;

    signal fifo_full_out : std_logic;
    --signal fifo_valid_in : std_logic;
    signal fifo_empty_out : std_logic;

begin    
    bram_proc : process(CLK, RST)
    begin
        if (RST = '1') then
            bram_m2s <= POROTO_BRAM_DEFAULT_M2S;
        elsif rising_edge(CLK) then
            if (in_receive = '1') then
                bram_m2s.re <= '0';
                bram_m2s.addr_r <= (others => '0');
                if (riffa_rx_m2s.DATA_VALID = '1') then
                    bram_m2s.we <= '1';
                    bram_m2s.addr_w <= rAddr;
                    bram_m2s.din <= riffa_rx_m2s.DATA(BRAM_DATA_SIZE-1 downto 0);
                else
                    bram_m2s.we <= '0';
                    bram_m2s.addr_w <= (others => '0');
                    bram_m2s.din <= (others => '0');
                end if;
                --riffa_tx_m2s.DATA <= (others => '0');
            elsif (in_transmit = '1') then
                bram_m2s.re <= '1';
                bram_m2s.addr_w <= (others => '0');
                bram_m2s.addr_r <= tAddr;
                --riffa_tx_m2s.DATA <= (others => '0');
                --riffa_tx_m2s.DATA(BRAM_DATA_SIZE-1 downto 0) <= bram_s2m.dout;
            else
                bram_m2s <= POROTO_BRAM_DEFAULT_M2S;
                --riffa_tx_m2s.DATA <= (others => '0');
            end if;
        end if;
    end process;
    
    -- RX from RIFFA channel interface & to user interface --
    rxfsm_proc : process(CLK, RST)
    begin
        if (RST = '1') then
            rxchnl_state     <= RX_CHNL_IDLE;
            riffa_rx_s2m.ACK      <= '0';
            riffa_rx_s2m.DATA_REN <= '0';
            in_receive       <= '0';
        elsif rising_edge(CLK) then
            if (rxchnl_state = RX_CHNL_IDLE) then
                in_receive <= '0';
            else
                in_receive <= '1';
            end if;
            case rxchnl_state is
                when RX_CHNL_IDLE =>
                    riffa_rx_s2m.ACK      <= '0';
                    riffa_rx_s2m.DATA_REN <= '0';
                    rCount           <= (others => '0');
                    rAddr            <= (others => '0');

                    if (riffa_rx_m2s.EN = '1') then
                        report "Riffa Bram Rx : channel enabled";
                        riffa_rx_s2m.ACK  <= '1';
                        rxchnl_state <= RX_CHNL_READY;
                        rAddr <= riffa_rx_m2s.OFF & '0';
                    end if;

                when RX_CHNL_READY =>
                    riffa_rx_s2m.ACK  <= '0';
                    rxchnl_state <= RX_CHNL_RUN;

                when RX_CHNL_RUN =>
                    riffa_rx_s2m.DATA_REN <= '1';
                    if (riffa_rx_m2s.DATA_VALID = '1') then
                        report "Riffa Bram Rx : got data : " & integer'image(to_integer(signed(riffa_rx_m2s.DATA))) & " to " & integer'image(to_integer(unsigned(rAddr)));
                        rCount       <= rCount + 1; --(C_PCI_DATA_WIDTH / 32);
                        rAddr        <= rAddr + 1; --(C_PCI_DATA_WIDTH / 8);
                    end if;
                    if (riffa_rx_m2s.EN = '0' and riffa_rx_m2s.DATA_VALID = '0') then
                        rxchnl_state <= RX_CHNL_IDLE;
                    end if;

                when others => rxchnl_state <= RX_CHNL_IDLE;
            end case;
        end if;
    end process;

    -- TX from user interface & to RIFFA channel interface --
    riffa_tx_m2s.EN   <= txEn;
    riffa_tx_m2s.LAST <= txLast;
    riffa_tx_m2s.LEN  <= txLen;
    riffa_tx_m2s.OFF  <= txOffset;

    tx_fifo : RiffaBramFifo generic map(
        ADDRESS_WIDTH => 8,
        DATA_WIDTH => 32,
        ALMOST_FULL_COUNT => 3,
        ALMOST_EMPTY_COUNT => 0
    )
    port map(
        clk => clk,
        rst => rst,
        data_in => bram_s2m.dout,
        valid_in => en_pipeline(0),
        full_out => fifo_full_out,
        data_out => riffa_tx_m2s.DATA(BRAM_DATA_SIZE-1 downto 0),
        read_enable_in => riffa_tx_s2m.DATA_REN,
        empty_out => fifo_empty_out
    );
    riffa_tx_m2s.DATA(C_PCI_DATA_WIDTH-1 downto BRAM_DATA_SIZE) <= (others => '0');
    riffa_tx_m2s.DATA_VALID <= not fifo_empty_out;

    txfsm_proc : process(CLK, RST)
    begin
        if (RST = '1') then
            txEn               <= '0';
            txLast             <= '0';
            txLen              <= (others => '0');
            txOffset           <= (others => '0');
            txchnl_state       <= TX_CHNL_IDLE;
            tCount             <= (others => '0');
            tAddr              <= (others => '0');
            en_pipeline        <= (others => '0');
            in_transmit        <= '0';
        elsif rising_edge(CLK) then
            if (riffa_ctrl.EN = '1') then
                txEn <= '1';
                txLast <= riffa_ctrl.LAST;
                txLen  <= riffa_ctrl.LEN;
                txOffset  <= riffa_ctrl.OFF;
            else
            end if;
            if (txchnl_state = TX_CHNL_IDLE) then
                in_transmit <= '0';
            else
                in_transmit <= '1';
            end if;
            case txchnl_state is
                when TX_CHNL_IDLE =>
                    tCount        <= (others => '0');
                    tAddr         <= (others => '0');
                    en_pipeline <= (others => '0');
                    if (txEn = '1') then
                        report "Riffa Bram Tx : Triggering TX";
                        txchnl_state  <= TX_CHNL_RUN;
                        tAddr         <= riffa_ctrl.OFF & '0';
                        en_pipeline   <= '1' & en_pipeline(2 downto 1);
                        report "Riffa Bram Tx : Read from: " & integer'image(to_integer(unsigned(tAddr)));
                    end if;

                when TX_CHNL_RUN =>
                    en_pipeline <= not fifo_full_out & en_pipeline(2 downto 1);
                    if fifo_full_out = '0' then
                        tCount <= tCount + 1; --(C_PCI_DATA_WIDTH / 32);
                        tAddr <= tAddr + 1; --(C_PCI_DATA_WIDTH / 8);
                        report "Riffa Bram Tx : Read from: " & integer'image(to_integer(unsigned(tAddr)));
                    end if;
                    if en_pipeline(0) = '1' then
                        report "Riffa Bram Tx : Push Data: " & integer'image(to_integer(signed(bram_s2m.dout)));
                    end if;
                    if (tCount >= riffa_ctrl.LEN + (C_PCI_DATA_WIDTH / 32)) then
                        txEn          <= '0';
                        txLast        <= '0';
                        txLen         <= (others => '0');
                        txOffset      <= (others => '0');
                        txchnl_state  <= TX_CHNL_IDLE;
                        report "Riffa Bram Tx : TX done";
                    end if;

                when others => txchnl_state <= TX_CHNL_IDLE;

            end case;
        end if;
    end process;    
end Behavioral;
    
