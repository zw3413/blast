const config = {
  backendUrl: 'http://localhost:8000',
  backendUrlWs: 'ws://localhost:8000/ws',
  operationParamter: {
    stab_vid: [
      {
        name: 'input_path',
        type: 'input',
        required: true,
        description: 'The video file to be stabilized'
      }
    ],
    crop_roi: [
      {
        name: 'input_path',
        type: 'input',
        required: true,
        description: 'The video file to be stabilized'
      },
      {
        name: 'shape_str',
        type: 'input',
        required: true,
        description: 'The shape of the region of interest'
      },
      {
        name: 'withROI',
        type: 'combobox',
        options: [false, true],
        required: true,
        description: 'with ROI'
      }
    ],
    set_pixel: [
      {
        name: 'input_path',
        type: 'input',
        required: true,
        description: 'The drill hole data'
      }
    ],
    slungshot: [
      {
        name: 'input_path',
        type: 'input',
        required: true,
        description: 'The video file to be detect'
      },
      {
        name: 'algorithm_detect',
        type: 'combobox',
        options: ['OpticalFlow', 'FrameDiff'],
        required: true,
        description: 'Detection Algorithm '
      },
      {
        name: 'algorithm_track',
        type: 'combobox',
        options: ['ByteTrack', 'StrongSORT', 'DISABLE'],
        required: true,
        description: 'Track Algorithm'
      }
    ]
  }
};

export default config;