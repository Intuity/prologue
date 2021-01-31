

module example (
      input  wire                  clk
    , input  wire                  rst
    , input  wire [32-1:0] in_data
    , input  wire                  in_valid
    , output wire [32-1:0] out_data
    , output wire                  out_valid
);


    reg [32:0] m_delay [10-1:0];

    assign {out_data, out_valid} = m_delay[10-1];

    always @(posedge clk, posedge rst) begin : p_delay
        integer i;
        if (rst) begin
            for (i = 0; i < 10; i = (i + 1)) begin
                m_delay <= {(32+1){1'b0}};
            end
        end else begin
            for (i = 0; i < 10; i = (i + 1)) begin
                if (i == 0) begin
                    m_delay[i] <= {in_data, in_valid};
                end else begin
                    m_delay[i] <= m_delay[i-1];
                end
            end
        end
    end

endmodule
