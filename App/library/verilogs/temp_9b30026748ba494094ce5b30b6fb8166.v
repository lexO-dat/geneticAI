 module top (input tetR, input lacI, input aTc, output YFP, output BFP);
    assign YFP = tetR & lacI & !aTc;
    assign BFP = tetR & !lacI & aTc;
  endmodule