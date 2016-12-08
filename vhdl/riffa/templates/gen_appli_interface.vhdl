library IEEE;
use IEEE.STD_LOGIC_1164.ALL;

use IEEE.NUMERIC_STD.ALL;
use IEEE.STD_LOGIC_UNSIGNED.ALL;

library UNISIM;
use UNISIM.VComponents.all;

library work;
use work.poroto_pkg.all;

entity %%%NAME%%% is
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
                -- BRAM BUS Interface
        bram_app_m2s : in poroto_bram_m2sT;
        bram_app_s2m : out poroto_bram_s2mT);
end %%%NAME%%%;

architecture behavioral of %%%NAME%%% is

    component bram is
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
    end component;

    signal wea    : std_logic;
    signal addra  : std_logic_vector(8-1 downto 0);
    signal dina   : std_logic_vector(C_PCI_DATA_WIDTH-1 downto 0);
    signal douta  : std_logic_vector(C_PCI_DATA_WIDTH-1 downto 0);
    signal web    : std_logic;
    signal addrb  : std_logic_vector(8-1 downto 0);
    signal dinb   : std_logic_vector(C_PCI_DATA_WIDTH-1 downto 0);
    signal doutb  : std_logic_vector(C_PCI_DATA_WIDTH-1 downto 0);
    
    -- global state
    signal in_receive    : std_logic;
    signal in_transmit   : std_logic;
    
    -- RX from RIFFA channel interface
    type rxchnl_state_type is (RX_CHNL_IDLE, RX_CHNL_READY, RX_CHNL_RUN);
    signal rxchnl_state : rxchnl_state_type;
    signal rCount       : std_logic_vector(31 downto 0);

    -- TX to RIFFA channel interface
    type txchnl_state_type is (TX_CHNL_IDLE, TX_CHNL_START, TX_CHNL_READY, TX_CHNL_RUN);
    signal txchnl_state : txchnl_state_type;
    signal tCount       : std_logic_vector(31 downto 0);

    -- Length of transaction = number of 4 bytes words TX
    constant TX_TRANS_LENGTH : integer := 32;
    -- where to start storing sent data in the PC thread's receive buffer
    constant TX_MEMOFFSET    : integer := 13;

    signal USER_RX_DATA : std_logic_vector(C_PCI_DATA_WIDTH - 1 downto 0);

    signal USER_TX      : std_logic;

    signal en_pipeline : STD_LOGIC_VECTOR(1 downto 0);

begin
    bram_i: bram
    generic map (DATA => C_PCI_DATA_WIDTH)
    port map(
        clka => CLK,
        wea => wea,
        addra => addra,
        dina => dina,
        douta => douta,
        clkb => CLK,
        web => '0',
        addrb => addrb,
        dinb => dinb,
        doutb => doutb
    );
    
    bram_proc : process(CLK, RST)
    begin
        if (RST = '1') then
            wea <= '0';
            addra <= (others => '0');
            dina <= (others => '0');
            CHNL_TX_DATA <= (others => '0');
        elsif rising_edge(CLK) then
            if (in_receive = '1') then
                if (CHNL_RX_DATA_VALID = '1') then
                    wea <= '1';
                    addra <= rCount(7 downto 0);
                    dina <= CHNL_RX_DATA;
                else
                    wea <= '0';
                    addra <= (others => '0');
                    dina <= (others => '0');
                end if;
                CHNL_TX_DATA <= (others => '0');
            elsif (in_transmit = '1') then
                wea <= '0';
                addra <= tCount(7 downto 0);
                CHNL_TX_DATA <= douta + 100;
            else
                wea <= '0';
                addra <= (others => '0');
                dina <= (others => '0');                
                CHNL_TX_DATA <= (others => '0');
            end if;
        end if;
    end process;
    
    -- RX from RIFFA channel interface & to user interface --
    CHNL_RX_CLK <= CLK;

    rxfsm_proc : process(CLK, RST)
    begin
        if (RST = '1') then
            rxchnl_state     <= RX_CHNL_IDLE;
            CHNL_RX_ACK      <= '0';
            CHNL_RX_DATA_REN <= '0';
            USER_TX          <= '0';
            in_receive       <= '0';
        elsif rising_edge(CLK) then
            if (rxchnl_state = RX_CHNL_IDLE) then
                in_receive <= '0';
            else
                in_receive <= '1';
            end if;
            case rxchnl_state is
                when RX_CHNL_IDLE =>
                    CHNL_RX_ACK      <= '0';
                    CHNL_RX_DATA_REN <= '0';
                    rCount           <= (others => '0');

                    if (CHNL_RX = '1') then
                        CHNL_RX_ACK  <= '1';
                        rxchnl_state <= RX_CHNL_READY;
                    end if;

                when RX_CHNL_READY =>
                    CHNL_RX_ACK  <= '0';
                    rxchnl_state <= RX_CHNL_RUN;

                when RX_CHNL_RUN =>
                    CHNL_RX_DATA_REN <= '1';
                    if (CHNL_RX_DATA_VALID = '1') then
                        USER_RX_DATA <= CHNL_RX_DATA;
                        rCount       <= rCount + (C_PCI_DATA_WIDTH / 32);
                    end if;
                    if (CHNL_RX = '0' and CHNL_RX_DATA_VALID = '0') then
                        rxchnl_state <= RX_CHNL_IDLE;
                        USER_TX <= '1';
                    end if;

                when others => rxchnl_state <= RX_CHNL_IDLE;
            end case;
        end if;
    end process;

    -- TX from user interface & to RIFFA channel interface --
    CHNL_TX_CLK <= CLK;

    txfsm_proc : process(CLK, RST)
    begin
        if (RST = '1') then
            CHNL_TX            <= '0';
            CHNL_TX_LAST       <= '0';
            CHNL_TX_LEN        <= (others => '0');
            CHNL_TX_OFF        <= (others => '0');
            txchnl_state       <= TX_CHNL_IDLE;
            CHNL_TX_DATA_VALID <= '0';
            tCount             <= (others => '0');
            en_pipeline        <= (others => '0');
            in_transmit        <= '0';
        elsif rising_edge(CLK) then
            if (USER_TX = '1') then
                CHNL_TX      <= '1';
                CHNL_TX_LAST <= '1';
                CHNL_TX_LEN  <= std_logic_vector(to_unsigned(TX_TRANS_LENGTH, 32));
                CHNL_TX_OFF  <= std_logic_vector(to_unsigned(TX_MEMOFFSET, 31));
            else
                CHNL_TX      <= '0';
                CHNL_TX_LAST <= '0';
                CHNL_TX_LEN  <= (others => '0');
                CHNL_TX_OFF  <= (others => '0');
            end if;
            if (txchnl_state = TX_CHNL_IDLE) then
                in_transmit <= '0';
            else
                in_transmit <= '1';
            end if;
            case txchnl_state is
                when TX_CHNL_IDLE =>
                    tCount <= (others => '0');
                    en_pipeline <= (others => '0');
                    CHNL_TX_DATA_VALID <= '0';
                    if (USER_TX = '1') then
                        txchnl_state <= TX_CHNL_RUN;
                    end if;

                when TX_CHNL_RUN =>
                    --TODO: Must be replaced by a FIFO
                    CHNL_TX_DATA_VALID  <= en_pipeline(0);
                    en_pipeline <= CHNL_TX_DATA_REN & en_pipeline(1 downto 1);                
                    if (CHNL_TX_DATA_REN = '1') then
                        tCount <= tCount + (C_PCI_DATA_WIDTH / 32);
                    end if;
                    if (tCount >= TX_TRANS_LENGTH + (C_PCI_DATA_WIDTH / 32)) then
                        txchnl_state <= TX_CHNL_IDLE;
                    end if;

                when others => txchnl_state <= TX_CHNL_IDLE;

            end case;
        end if;
    end process;
    
    --rstb   : in std_logic;
    --enb    : in std_logic;
    web    <= bram_app_m2s.we;
    addrb  <= bram_app_m2s.addr_w(7 downto 0) when bram_app_m2s.we = '1' else bram_app_m2s.addr_r(7 downto 0);
    dinb   <= bram_app_m2s.din;
    bram_app_s2m.dout <= doutb;
    
end Behavioral;
	
