import numpy as np
from hailo_platform import VDevice, HailoSchedulingAlgorithm

timeout_ms = 1000

params = VDevice.create_params()
params.scheduling_algorithm = HailoSchedulingAlgorithm.ROUND_ROBIN

# The vdevice is used as a context manager ("with" statement) to ensure it's released on time.
with VDevice(params) as vdevice:

    # Create an infer model from an HEF:
    infer_model = vdevice.create_infer_model('../hefs/resnet_v1_18.hef')

    # Configure the infer model and create bindings for it
    with infer_model.configure() as configured_infer_model:
        bindings = configured_infer_model.create_bindings()

        # Set input and output buffers
        buffer = np.empty(infer_model.input().shape).astype(np.uint8)
        bindings.input().set_buffer(buffer)

        buffer = np.empty(infer_model.output().shape).astype(np.uint8)
        bindings.output().set_buffer(buffer)

        # Run synchronous inference and access the output buffers
        configured_infer_model.run([bindings], timeout_ms)
        buffer = bindings.output().get_buffer()

        # Run asynchronous inference
        job = configured_infer_model.run_async([bindings])
        job.wait(timeout_ms)
