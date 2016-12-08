//----------------------------------------------------------------------------
// Filename:			blackbox_components.v
//
//-----------------------------------------------------------------------------

(*black_box*)module riffa_endpoint #(
	parameter C_PCI_DATA_WIDTH = 9'd64,
	parameter C_NUM_CHNL = 4'd4,
	parameter C_MAX_READ_REQ_BYTES = 512,	// Max size of read requests (in bytes)
	parameter C_TAG_WIDTH = 5, 				// Number of outstanding requests 
	parameter C_ALTERA = 1'b0				// 1 if Altera, 0 if Xilinx
)
(
	input CLK,
	input RST_IN,
	output RST_OUT,

	input [C_PCI_DATA_WIDTH-1:0] M_AXIS_RX_TDATA,
	input [(C_PCI_DATA_WIDTH/8)-1:0] M_AXIS_RX_TKEEP,
	input M_AXIS_RX_TLAST,
	input M_AXIS_RX_TVALID,
	output M_AXIS_RX_TREADY,
	input [4:0] IS_SOF,
	input [4:0] IS_EOF,
	input RERR_FWD,
	
	output [C_PCI_DATA_WIDTH-1:0] S_AXIS_TX_TDATA,
	output [(C_PCI_DATA_WIDTH/8)-1:0] S_AXIS_TX_TKEEP,
	output S_AXIS_TX_TLAST,
	output S_AXIS_TX_TVALID,
	output S_AXIS_SRC_DSC,
	input S_AXIS_TX_TREADY,
	
	input [15:0] COMPLETER_ID,
	input CFG_BUS_MSTR_ENABLE,	
	input [5:0] CFG_LINK_WIDTH,			// cfg_lstatus[9:4] (from Link Status Register): 000001=x1, 000010=x2, 000100=x4, 001000=x8, 001100=x12, 010000=x16, 100000=x32, others=? 
	input [1:0] CFG_LINK_RATE,			// cfg_lstatus[1:0] (from Link Status Register): 01=2.5GT/s, 10=5.0GT/s, others=?
	input [2:0] MAX_READ_REQUEST_SIZE,	// cfg_dcommand[14:12] (from Device Control Register): 000=128B, 001=256B, 010=512B, 011=1024B, 100=2048B, 101=4096B
	input [2:0] MAX_PAYLOAD_SIZE, 		// cfg_dcommand[7:5] (from Device Control Register): 000=128B, 001=256B, 010=512B, 011=1024B
	input CFG_INTERRUPT_MSIEN,			// 1 if MSI interrupts are enable, 0 if only legacy are supported
	input CFG_INTERRUPT_RDY,			// High when interrupt is able to be sent
	output CFG_INTERRUPT,				// High to request interrupt, when both CFG_INTERRUPT_RDY and CFG_INTERRUPT are high, interrupt is sent
    input 				       RCB,
    input [11:0] 			       MAX_RC_CPLD, // Receive credit limit for data (be sure fc_sel == 001)
    input [7:0] 			       MAX_RC_CPLH, // Receive credit limit for headers (be sure fc_sel == 001)
	
    // Altera Signals
    input [C_PCI_DATA_WIDTH-1:0] RX_ST_DATA,
    input [0:0] RX_ST_EOP,
    input [0:0] RX_ST_SOP, 
    input [0:0] RX_ST_VALID,
    output RX_ST_READY,
    input [0:0] RX_ST_EMPTY,

    output [C_PCI_DATA_WIDTH-1:0] TX_ST_DATA,
    output [0:0] TX_ST_VALID,
    input TX_ST_READY,
    output [0:0] TX_ST_EOP,
    output [0:0] TX_ST_SOP,
    output [0:0] TX_ST_EMPTY,
    input [31:0] TL_CFG_CTL,
    input [3:0] TL_CFG_ADD,
    input [52:0] TL_CFG_STS,
    input [7:0] 			       KO_CPL_SPC_HEADER,
    input [11:0] 			       KO_CPL_SPC_DATA,

    input APP_MSI_ACK,
    output APP_MSI_REQ,

    // RIFFA Signals
	input [C_NUM_CHNL-1:0] CHNL_RX_CLK, 
	output [C_NUM_CHNL-1:0] CHNL_RX, 
	input [C_NUM_CHNL-1:0] CHNL_RX_ACK, 
	output [C_NUM_CHNL-1:0] CHNL_RX_LAST, 
	output [(C_NUM_CHNL*32)-1:0] CHNL_RX_LEN, 
	output [(C_NUM_CHNL*31)-1:0] CHNL_RX_OFF, 
	output [(C_NUM_CHNL*C_PCI_DATA_WIDTH)-1:0] CHNL_RX_DATA, 
	output [C_NUM_CHNL-1:0] CHNL_RX_DATA_VALID, 
	input [C_NUM_CHNL-1:0] CHNL_RX_DATA_REN,
	
	input [C_NUM_CHNL-1:0] CHNL_TX_CLK, 
	input [C_NUM_CHNL-1:0] CHNL_TX, 
	output [C_NUM_CHNL-1:0] CHNL_TX_ACK,
	input [C_NUM_CHNL-1:0] CHNL_TX_LAST, 
	input [(C_NUM_CHNL*32)-1:0] CHNL_TX_LEN, 
	input [(C_NUM_CHNL*31)-1:0] CHNL_TX_OFF, 
	input [(C_NUM_CHNL*C_PCI_DATA_WIDTH)-1:0] CHNL_TX_DATA, 
	input [C_NUM_CHNL-1:0] CHNL_TX_DATA_VALID, 
	output [C_NUM_CHNL-1:0] CHNL_TX_DATA_REN
);

endmodule


(*black_box*)module v6_pcie_v2_5 # (
  parameter        ALLOW_X8_GEN2 = "FALSE",
  parameter        BAR0 = 32'hFFFFFC00,
  parameter        BAR1 = 32'h00000000,
  parameter        BAR2 = 32'h00000000,
  parameter        BAR3 = 32'h00000000,
  parameter        BAR4 = 32'h00000000,
  parameter        BAR5 = 32'h00000000,

  parameter        CARDBUS_CIS_POINTER = 32'h00000000,
  parameter        CLASS_CODE = 24'h050000,
  parameter        CMD_INTX_IMPLEMENTED = "TRUE",
  parameter        CPL_TIMEOUT_DISABLE_SUPPORTED = "FALSE",
  parameter        CPL_TIMEOUT_RANGES_SUPPORTED = 4'h2,

  parameter        DEV_CAP_ENDPOINT_L0S_LATENCY = 0,
  parameter        DEV_CAP_ENDPOINT_L1_LATENCY = 7,
  parameter        DEV_CAP_EXT_TAG_SUPPORTED = "FALSE",
  parameter        DEV_CAP_MAX_PAYLOAD_SUPPORTED = 2,
  parameter        DEV_CAP_PHANTOM_FUNCTIONS_SUPPORT = 0,
  parameter        DEVICE_ID = 16'h6018,

  parameter        DISABLE_LANE_REVERSAL = "TRUE",
  parameter        DISABLE_SCRAMBLING = "FALSE",
  parameter        DSN_BASE_PTR = 12'h100,
  parameter        DSN_CAP_NEXTPTR = 12'h000,
  parameter        DSN_CAP_ON = "TRUE",

  parameter        ENABLE_MSG_ROUTE = 11'b00000000000,
  parameter        ENABLE_RX_TD_ECRC_TRIM = "FALSE",
  parameter        EXPANSION_ROM = 32'h00000000,
  parameter        EXT_CFG_CAP_PTR = 6'h3F,
  parameter        EXT_CFG_XP_CAP_PTR = 10'h3FF,
  parameter        HEADER_TYPE = 8'h00,
  parameter        INTERRUPT_PIN = 8'h1,

  parameter        LINK_CAP_DLL_LINK_ACTIVE_REPORTING_CAP = "FALSE",
  parameter        LINK_CAP_LINK_BANDWIDTH_NOTIFICATION_CAP = "FALSE",
  parameter        LINK_CAP_MAX_LINK_SPEED = 4'h1,
  parameter        LINK_CAP_MAX_LINK_WIDTH = 6'h08,
  parameter        LINK_CAP_SURPRISE_DOWN_ERROR_CAPABLE = "FALSE",

  parameter        LINK_CTRL2_DEEMPHASIS = "FALSE",
  parameter        LINK_CTRL2_HW_AUTONOMOUS_SPEED_DISABLE = "FALSE",
  parameter        LINK_CTRL2_TARGET_LINK_SPEED = 4'h0,
  parameter        LINK_STATUS_SLOT_CLOCK_CONFIG = "FALSE",

  parameter        LL_ACK_TIMEOUT = 15'h0000,
  parameter        LL_ACK_TIMEOUT_EN = "FALSE",
  parameter        LL_ACK_TIMEOUT_FUNC = 0,
  parameter        LL_REPLAY_TIMEOUT = 15'h0026,
  parameter        LL_REPLAY_TIMEOUT_EN = "TRUE",
  parameter        LL_REPLAY_TIMEOUT_FUNC = 1,

  parameter        LTSSM_MAX_LINK_WIDTH = 6'h08,
  parameter        MSI_CAP_MULTIMSGCAP = 0,
  parameter        MSI_CAP_MULTIMSG_EXTENSION = 0,
  parameter        MSI_CAP_ON = "TRUE",
  parameter        MSI_CAP_PER_VECTOR_MASKING_CAPABLE = "FALSE",
  parameter        MSI_CAP_64_BIT_ADDR_CAPABLE = "TRUE",

  parameter        MSIX_CAP_ON = "FALSE",
  parameter        MSIX_CAP_PBA_BIR = 0,
  parameter        MSIX_CAP_PBA_OFFSET = 29'h0,
  parameter        MSIX_CAP_TABLE_BIR = 0,
  parameter        MSIX_CAP_TABLE_OFFSET = 29'h0,
  parameter        MSIX_CAP_TABLE_SIZE = 11'h0,

  parameter        PCIE_CAP_DEVICE_PORT_TYPE = 4'b0000,
  parameter        PCIE_CAP_INT_MSG_NUM = 5'h1,
  parameter        PCIE_CAP_NEXTPTR = 8'h00,
  parameter        PCIE_DRP_ENABLE = "FALSE",
  parameter        PIPE_PIPELINE_STAGES = 0,                // 0 - 0 stages, 1 - 1 stage, 2 - 2 stages

  parameter        PM_CAP_DSI = "FALSE",
  parameter        PM_CAP_D1SUPPORT = "FALSE",
  parameter        PM_CAP_D2SUPPORT = "FALSE",
  parameter        PM_CAP_NEXTPTR = 8'h48,
  parameter        PM_CAP_PMESUPPORT = 5'h0F,
  parameter        PM_CSR_NOSOFTRST = "TRUE",

  parameter        PM_DATA_SCALE0 = 2'h0,
  parameter        PM_DATA_SCALE1 = 2'h0,
  parameter        PM_DATA_SCALE2 = 2'h0,
  parameter        PM_DATA_SCALE3 = 2'h0,
  parameter        PM_DATA_SCALE4 = 2'h0,
  parameter        PM_DATA_SCALE5 = 2'h0,
  parameter        PM_DATA_SCALE6 = 2'h0,
  parameter        PM_DATA_SCALE7 = 2'h0,

  parameter        PM_DATA0 = 8'h00,
  parameter        PM_DATA1 = 8'h00,
  parameter        PM_DATA2 = 8'h00,
  parameter        PM_DATA3 = 8'h00,
  parameter        PM_DATA4 = 8'h00,
  parameter        PM_DATA5 = 8'h00,
  parameter        PM_DATA6 = 8'h00,
  parameter        PM_DATA7 = 8'h00,

  parameter        REF_CLK_FREQ = 2,                        // 0 - 100 MHz, 1 - 125 MHz, 2 - 250 MHz
  parameter        REVISION_ID = 8'h00,
  parameter        SPARE_BIT0 = 0,
  parameter        SUBSYSTEM_ID = 16'h0007,
  parameter        SUBSYSTEM_VENDOR_ID = 16'h10EE,

  parameter        TL_RX_RAM_RADDR_LATENCY = 0,
  parameter        TL_RX_RAM_RDATA_LATENCY = 2,
  parameter        TL_RX_RAM_WRITE_LATENCY = 0,
  parameter        TL_TX_RAM_RADDR_LATENCY = 0,
  parameter        TL_TX_RAM_RDATA_LATENCY = 2,
  parameter        TL_TX_RAM_WRITE_LATENCY = 0,

  parameter        UPCONFIG_CAPABLE = "TRUE",
  parameter        USER_CLK_FREQ = 3,
  parameter        VC_BASE_PTR = 12'h0,
  parameter        VC_CAP_NEXTPTR = 12'h000,
  parameter        VC_CAP_ON = "FALSE",
  parameter        VC_CAP_REJECT_SNOOP_TRANSACTIONS = "FALSE",

  parameter        VC0_CPL_INFINITE = "TRUE",
  parameter        VC0_RX_RAM_LIMIT = 13'h7FF,
  parameter        VC0_TOTAL_CREDITS_CD = 850,
  parameter        VC0_TOTAL_CREDITS_CH = 72,
  parameter        VC0_TOTAL_CREDITS_NPH = 4,
  parameter        VC0_TOTAL_CREDITS_PD = 64,
  parameter        VC0_TOTAL_CREDITS_PH = 4,
  parameter        VC0_TX_LASTPACKET = 29,

  parameter        VENDOR_ID = 16'h10EE,
  parameter        VSEC_BASE_PTR = 12'h0,
  parameter        VSEC_CAP_NEXTPTR = 12'h000,
  parameter        VSEC_CAP_ON = "FALSE",

  parameter        AER_BASE_PTR = 12'h128,
  parameter        AER_CAP_ECRC_CHECK_CAPABLE = "FALSE",
  parameter        AER_CAP_ECRC_GEN_CAPABLE = "FALSE",
  parameter        AER_CAP_ID = 16'h0001,
  parameter        AER_CAP_INT_MSG_NUM_MSI = 5'h0a,
  parameter        AER_CAP_INT_MSG_NUM_MSIX = 5'h15,
  parameter        AER_CAP_NEXTPTR = 12'h160,
  parameter        AER_CAP_ON = "FALSE",
  parameter        AER_CAP_PERMIT_ROOTERR_UPDATE = "TRUE",
  parameter        AER_CAP_VERSION = 4'h1,

  parameter        CAPABILITIES_PTR = 8'h40,
  parameter        CRM_MODULE_RSTS = 7'h00,
  parameter        DEV_CAP_ENABLE_SLOT_PWR_LIMIT_SCALE = "TRUE",
  parameter        DEV_CAP_ENABLE_SLOT_PWR_LIMIT_VALUE = "TRUE",
  parameter        DEV_CAP_FUNCTION_LEVEL_RESET_CAPABLE = "FALSE",
  parameter        DEV_CAP_ROLE_BASED_ERROR = "TRUE",
  parameter        DEV_CAP_RSVD_14_12 = 0,
  parameter        DEV_CAP_RSVD_17_16 = 0,
  parameter        DEV_CAP_RSVD_31_29 = 0,
  parameter        DEV_CONTROL_AUX_POWER_SUPPORTED = "FALSE",

  parameter        DISABLE_ASPM_L1_TIMER = "FALSE",
  parameter        DISABLE_BAR_FILTERING = "FALSE",
  parameter        DISABLE_ID_CHECK = "FALSE",
  parameter        DISABLE_RX_TC_FILTER = "FALSE",
  parameter        DNSTREAM_LINK_NUM = 8'h00,

  parameter        DSN_CAP_ID = 16'h0003,
  parameter        DSN_CAP_VERSION = 4'h1,
  parameter        ENTER_RVRY_EI_L0 = "TRUE",
  parameter        INFER_EI = 5'h0c,
  parameter        IS_SWITCH = "FALSE",

  parameter        LAST_CONFIG_DWORD = 10'h3FF,
  parameter        LINK_CAP_ASPM_SUPPORT = 1,
  parameter        LINK_CAP_CLOCK_POWER_MANAGEMENT = "FALSE",
  parameter        LINK_CAP_L0S_EXIT_LATENCY_COMCLK_GEN1 = 7,
  parameter        LINK_CAP_L0S_EXIT_LATENCY_COMCLK_GEN2 = 7,
  parameter        LINK_CAP_L0S_EXIT_LATENCY_GEN1 = 7,
  parameter        LINK_CAP_L0S_EXIT_LATENCY_GEN2 = 7,
  parameter        LINK_CAP_L1_EXIT_LATENCY_COMCLK_GEN1 = 7,
  parameter        LINK_CAP_L1_EXIT_LATENCY_COMCLK_GEN2 = 7,
  parameter        LINK_CAP_L1_EXIT_LATENCY_GEN1 = 7,
  parameter        LINK_CAP_L1_EXIT_LATENCY_GEN2 = 7,
  parameter        LINK_CAP_RSVD_23_22 = 0,
  parameter        LINK_CONTROL_RCB = 0,

  parameter        MSI_BASE_PTR = 8'h48,
  parameter        MSI_CAP_ID = 8'h05,
  parameter        MSI_CAP_NEXTPTR = 8'h60,
  parameter        MSIX_BASE_PTR = 8'h9c,
  parameter        MSIX_CAP_ID = 8'h11,
  parameter        MSIX_CAP_NEXTPTR = 8'h00,
  parameter        N_FTS_COMCLK_GEN1 = 255,
  parameter        N_FTS_COMCLK_GEN2 = 254,
  parameter        N_FTS_GEN1 = 255,
  parameter        N_FTS_GEN2 = 255,

  parameter        PCIE_BASE_PTR = 8'h60,
  parameter        PCIE_CAP_CAPABILITY_ID = 8'h10,
  parameter        PCIE_CAP_CAPABILITY_VERSION = 4'h2,
  parameter        PCIE_CAP_ON = "TRUE",
  parameter        PCIE_CAP_RSVD_15_14 = 0,
  parameter        PCIE_CAP_SLOT_IMPLEMENTED = "FALSE",
  parameter        PCIE_REVISION = 2,
  parameter        PGL0_LANE = 0,
  parameter        PGL1_LANE = 1,
  parameter        PGL2_LANE = 2,
  parameter        PGL3_LANE = 3,
  parameter        PGL4_LANE = 4,
  parameter        PGL5_LANE = 5,
  parameter        PGL6_LANE = 6,
  parameter        PGL7_LANE = 7,
  parameter        PL_AUTO_CONFIG = 0,
  parameter        PL_FAST_TRAIN = "FALSE",

  parameter        PM_BASE_PTR = 8'h40,
  parameter        PM_CAP_AUXCURRENT = 0,
  parameter        PM_CAP_ID = 8'h01,
  parameter        PM_CAP_ON = "TRUE",
  parameter        PM_CAP_PME_CLOCK = "FALSE",
  parameter        PM_CAP_RSVD_04 = 0,
  parameter        PM_CAP_VERSION = 3,
  parameter        PM_CSR_BPCCEN = "FALSE",
  parameter        PM_CSR_B2B3 = "FALSE",

  parameter        RECRC_CHK = 0,
  parameter        RECRC_CHK_TRIM = "FALSE",
  parameter        ROOT_CAP_CRS_SW_VISIBILITY = "FALSE",
  parameter        SELECT_DLL_IF = "FALSE",
  parameter        SLOT_CAP_ATT_BUTTON_PRESENT = "FALSE",
  parameter        SLOT_CAP_ATT_INDICATOR_PRESENT = "FALSE",
  parameter        SLOT_CAP_ELEC_INTERLOCK_PRESENT = "FALSE",
  parameter        SLOT_CAP_HOTPLUG_CAPABLE = "FALSE",
  parameter        SLOT_CAP_HOTPLUG_SURPRISE = "FALSE",
  parameter        SLOT_CAP_MRL_SENSOR_PRESENT = "FALSE",
  parameter        SLOT_CAP_NO_CMD_COMPLETED_SUPPORT = "FALSE",
  parameter        SLOT_CAP_PHYSICAL_SLOT_NUM = 13'h0000,
  parameter        SLOT_CAP_POWER_CONTROLLER_PRESENT = "FALSE",
  parameter        SLOT_CAP_POWER_INDICATOR_PRESENT = "FALSE",
  parameter        SLOT_CAP_SLOT_POWER_LIMIT_SCALE = 0,
  parameter        SLOT_CAP_SLOT_POWER_LIMIT_VALUE = 8'h00,
  parameter        SPARE_BIT1 = 0,
  parameter        SPARE_BIT2 = 0,
  parameter        SPARE_BIT3 = 0,
  parameter        SPARE_BIT4 = 0,
  parameter        SPARE_BIT5 = 0,
  parameter        SPARE_BIT6 = 0,
  parameter        SPARE_BIT7 = 0,
  parameter        SPARE_BIT8 = 0,
  parameter        SPARE_BYTE0 = 8'h00,
  parameter        SPARE_BYTE1 = 8'h00,
  parameter        SPARE_BYTE2 = 8'h00,
  parameter        SPARE_BYTE3 = 8'h00,
  parameter        SPARE_WORD0 = 32'h00000000,
  parameter        SPARE_WORD1 = 32'h00000000,
  parameter        SPARE_WORD2 = 32'h00000000,
  parameter        SPARE_WORD3 = 32'h00000000,

  parameter        TL_RBYPASS = "FALSE",
  parameter        TL_TFC_DISABLE = "FALSE",
  parameter        TL_TX_CHECKS_DISABLE = "FALSE",
  parameter        EXIT_LOOPBACK_ON_EI  = "TRUE",
  parameter        UPSTREAM_FACING = "TRUE",
  parameter        UR_INV_REQ = "TRUE",

  parameter        VC_CAP_ID = 16'h0002,
  parameter        VC_CAP_VERSION = 4'h1,
  parameter        VSEC_CAP_HDR_ID = 16'h1234,
  parameter        VSEC_CAP_HDR_LENGTH = 12'h018,
  parameter        VSEC_CAP_HDR_REVISION = 4'h1,
  parameter        VSEC_CAP_ID = 16'h000b,
  parameter        VSEC_CAP_IS_LINK_VISIBLE = "TRUE",
  parameter        VSEC_CAP_VERSION = 4'h1
)
(
  //-------------------------------------------------------
  // 1. PCI Express (pci_exp) Interface
  //-------------------------------------------------------

  // Tx
  output  [(LINK_CAP_MAX_LINK_WIDTH - 1):0]     pci_exp_txp,
  output  [(LINK_CAP_MAX_LINK_WIDTH - 1):0]     pci_exp_txn,

  // Rx
  input   [(LINK_CAP_MAX_LINK_WIDTH - 1):0]     pci_exp_rxp,
  input   [(LINK_CAP_MAX_LINK_WIDTH - 1):0]     pci_exp_rxn,

  //-------------------------------------------------------
  // 2. AXI-S Interface
  //-------------------------------------------------------

  // Common
  output                                        user_clk_out,
  output                                        user_reset_out,
  output                                        user_lnk_up,

  // Tx
  output  [5:0]                                 tx_buf_av,
  output                                        tx_err_drop,
  output                                        tx_cfg_req,
  output                                        s_axis_tx_tready,
  input  [63:0]                                 s_axis_tx_tdata,
  input  [7:0]                                  s_axis_tx_tkeep,
  input  [3:0]                                  s_axis_tx_tuser,
  input                                         s_axis_tx_tlast,
  input                                         s_axis_tx_tvalid,
  input                                         tx_cfg_gnt,

  // Rx
  output  [63:0]                                m_axis_rx_tdata,
  output  [7:0]                                 m_axis_rx_tkeep,
  output                                        m_axis_rx_tlast,
  output                                        m_axis_rx_tvalid,
  input                                         m_axis_rx_tready,
  output    [21:0]                              m_axis_rx_tuser,
  input                                         rx_np_ok,

  // Flow Control
  output [11:0]                                 fc_cpld,
  output  [7:0]                                 fc_cplh,
  output [11:0]                                 fc_npd,
  output  [7:0]                                 fc_nph,
  output [11:0]                                 fc_pd,
  output  [7:0]                                 fc_ph,
  input   [2:0]                                 fc_sel,


  //-------------------------------------------------------
  // 3. Configuration (CFG) Interface
  //-------------------------------------------------------

  output [31:0]                                 cfg_do,
  output                                        cfg_rd_wr_done,
  input  [31:0]                                 cfg_di,
  input   [3:0]                                 cfg_byte_en,
  input   [9:0]                                 cfg_dwaddr,
  input                                         cfg_wr_en,
  input                                         cfg_rd_en,

  input                                         cfg_err_cor,
  input                                         cfg_err_ur,
  input                                         cfg_err_ecrc,
  input                                         cfg_err_cpl_timeout,
  input                                         cfg_err_cpl_abort,
  input                                         cfg_err_cpl_unexpect,
  input                                         cfg_err_posted,
  input                                         cfg_err_locked,
  input  [47:0]                                 cfg_err_tlp_cpl_header,
  output                                        cfg_err_cpl_rdy,
  input                                         cfg_interrupt,
  output                                        cfg_interrupt_rdy,
  input                                         cfg_interrupt_assert,
  input  [7:0]                                  cfg_interrupt_di,
  output [7:0]                                  cfg_interrupt_do,
  output [2:0]                                  cfg_interrupt_mmenable,
  output                                        cfg_interrupt_msienable,
  output                                        cfg_interrupt_msixenable,
  output                                        cfg_interrupt_msixfm,
  input                                         cfg_turnoff_ok,
  output                                        cfg_to_turnoff,
  input                                         cfg_trn_pending,
  input                                         cfg_pm_wake,
  output  [7:0]                                 cfg_bus_number,
  output  [4:0]                                 cfg_device_number,
  output  [2:0]                                 cfg_function_number,
  output [15:0]                                 cfg_status,
  output [15:0]                                 cfg_command,
  output [15:0]                                 cfg_dstatus,
  output [15:0]                                 cfg_dcommand,
  output [15:0]                                 cfg_lstatus,
  output [15:0]                                 cfg_lcommand,
  output [15:0]                                 cfg_dcommand2,
  output  [2:0]                                 cfg_pcie_link_state,
  input  [63:0]                                 cfg_dsn,
  output                                        cfg_pmcsr_pme_en,
  output                                        cfg_pmcsr_pme_status,
  output  [1:0]                                 cfg_pmcsr_powerstate,

  //-------------------------------------------------------
  // 4. Physical Layer Control and Status (PL) Interface
  //-------------------------------------------------------

  output [2:0]                                  pl_initial_link_width,
  output [1:0]                                  pl_lane_reversal_mode,
  output                                        pl_link_gen2_capable,
  output                                        pl_link_partner_gen2_supported,
  output                                        pl_link_upcfg_capable,
  output [5:0]                                  pl_ltssm_state,
  output                                        pl_received_hot_rst,
  output                                        pl_sel_link_rate,
  output [1:0]                                  pl_sel_link_width,
  input                                         pl_directed_link_auton,
  input  [1:0]                                  pl_directed_link_change,
  input                                         pl_directed_link_speed,
  input  [1:0]                                  pl_directed_link_width,
  input                                         pl_upstream_prefer_deemph,

  //-------------------------------------------------------
  // 5. System  (SYS) Interface
  //-------------------------------------------------------

  input                                         sys_clk,
  input                                         sys_reset


);

endmodule