 module top (input TetR, input LacI, input AHL, output YFP, output BFP);
    assign YFP = (TetR & LacI) & ~AHL;
    assign BFP = (TetR & ~LacI & AHL);
  endmodule