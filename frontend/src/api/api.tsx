// Fetch Verilog Code
export const fetchVerilogCode = async (inputMessage: string) => {
    const response = await fetch('http://localhost:8001/v1/verilog/run', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ question: inputMessage }), // Correctly pass the `question` parameter
    });
  
    if (!response.ok) throw new Error('Error obtaining the verilog code.');
  
    const data = await response.json(); // Parse the JSON response
    return data.answer; // Extract the `answer` field containing the Verilog code
  };
  
  // Fetch UCF File
  export const fetchUcfFile = async (inputMessage: string) => {
    const response = await fetch('http://localhost:8001/v1/rag/ucf/run', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ question: inputMessage }), // Correctly pass the `question` parameter
    });
  
    if (!response.ok) throw new Error('Error fetching UCF file.');
  
    const data = await response.json(); // Parse the JSON response
    return data.answer; // Extract the `answer` field containing the UCF name
  };
  
  // Fetch Cello Processing
  export const fetchCelloProcessing = async (verilogCode: string, ucfIndex: number) => {
    const response = await fetch('http://localhost:8000/v1/run', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        verilogCode,
        ucfIndex,
        options: {
          verbose: true,
          log_overwrite: false,
          print_iters: false,
          exhaustive: false,
          test_configs: false,
        },
      }),
    });
  
    if (!response.ok) throw new Error('Cello processing failed.');
  
    const data = await response.json(); // Parse the JSON response
    return data; // Return the complete data, including `output_files` and `folder_name`
  };
  