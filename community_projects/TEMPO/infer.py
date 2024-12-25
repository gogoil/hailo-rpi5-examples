#!/usr/bin/env python3
import numpy as np
import wget
from hailo_platform import (HEF, VDevice, HailoStreamInterface, InferVStreams, ConfigureParams, InputVStreamParams, OutputVStreamParams, FormatType)
from PIL import Image, ImageDraw, ImageFont
import os
import random

with VDevice() as target:
    configure_params = ConfigureParams.create_from_hef(hef, interface=HailoStreamInterface.PCIe)
    network_group = target.configure(hef, configure_params)[0]
    network_group_params = network_group.create_params()
    input_vstream_info = hef.get_input_vstream_infos()[0]
    input_vstreams_params = InputVStreamParams.make_from_network_group(network_group, quantized=False, format_type=FormatType.UINT8)
    output_vstreams_params = OutputVStreamParams.make_from_network_group(network_group, quantized=False, format_type=FormatType.FLOAT32)
    with InferVStreams(network_group, input_vstreams_params, output_vstreams_params) as infer_pipeline:
        input_data = {input_vstream_info.name: np.expand_dims(resized_image, axis=0).astype(np.uint8)}    
        with network_group.activate(network_group_params):
            infer_results = infer_pipeline.infer(input_data)