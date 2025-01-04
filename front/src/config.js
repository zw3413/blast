const config = {
    backendUrl: 'http://localhost:8000',
    backendUrlWs:'ws://localhost:8000/ws',
     operationParamter :{
      stab_vid:[
        {
          name: 'input_path',
          type: 'input',
          required: true,
          description: 'The video file to be stabilized'
        },
        {
          name:'output_path',
          type: 'input',
          required: true,
          description: 'The output file path'
        }
      ],
      crop_roi:[
        {
          name: 'input_path',
          type: 'input',
          required: true,
          description: 'The video file to be stabilized'
        },
        {
          name:'output_path',
          type: 'input',
          required: true,
          description: 'The output file path'
        },
        {
          name:'shape',
          type: 'input',
          required: true,
          description: 'The shape of the region of interest'
        }
      ],
      set_pixel:[
        {
          name:'drill_hole_data',
          type: 'input',
          required: true,
          description: 'The drill hole data'
        }
      ],
      slungshot:[
        {
          name:'input_path',
          type: 'input',
          required: true,
          description: 'The video file to be stabilized'
        }
      ]
    }
};

export default config;