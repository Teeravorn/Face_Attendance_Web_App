import onnxruntime as ort

session_options = ort.SessionOptions()

# Use QNN EP with GPU backend instead of HTP (DSP)
providers = [
    ('QNNExecutionProvider', {
        'backend_path': 'libQnnGpu.so',   # ← GPU instead of libQnnHtp.so
    }),
    'CPUExecutionProvider'
]

session = ort.InferenceSession("/home/ubuntu/.insightface/models/buffalo_l/1k3d68.onnx", 
                                sess_options=session_options,
                                providers=providers)