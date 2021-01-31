`include "constants.vh"

module example (
      input  wire                  clk
    , input  wire                  rst
    , input  wire [`BUS_WIDTH-1:0] in_data
    , input  wire                  in_valid
    , output wire [`BUS_WIDTH-1:0] out_data
    , output wire                  out_valid
);


`ifdef NO_DELAY
    assign out_data  = in_data;
    assign out_valid = in_valid;
`else
    reg [`BUS_WIDTH:0] m_delay [`DELAY_LEN-1:0];

    assign {out_data, out_valid} = m_delay[`DELAY_LEN-1];

    always @(posedge clk, posedge rst) begin : p_delay
        integer i;
        if (rst) begin
            for (i = 0; i < `DELAY_LEN; i = (i + 1)) begin
                m_delay <= {(`BUS_WIDTH+1){1'b0}};
            end
        end else begin
            for (i = 0; i < `DELAY_LEN; i = (i + 1)) begin
                if (i == 0) begin
                    m_delay[i] <= {in_data, in_valid};
                end else begin
                    m_delay[i] <= m_delay[i-1];
                end
            end
        end
    end
`endif // NO_DELAY

endmodule
