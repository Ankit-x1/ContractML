# scripts/create_dummy_model.py
import numpy as np
import onnx
from onnx import helper, TensorProto

# Create a simple model: y = 2x + 1
input = helper.make_tensor_value_info('input', TensorProto.FLOAT, [1, 2])
weights = helper.make_tensor('weights', TensorProto.FLOAT, [2, 1], [2.0, 1.0])
bias = helper.make_tensor('bias', TensorProto.FLOAT, [1, 1], [1.0])
output = helper.make_tensor_value_info('output', TensorProto.FLOAT, [1, 1])

# Create nodes
matmul_node = helper.make_node(
    'MatMul',
    inputs=['input', 'weights'],
    outputs=['matmul_output'],
    name='matmul_node'
)

add_node = helper.make_node(
    'Add',
    inputs=['matmul_output', 'bias'],
    outputs=['output'],
    name='add_node'
)

# Create graph
graph = helper.make_graph(
    [matmul_node, add_node],
    'simple_model',
    [input],
    [output],
    [weights, bias]
)

# Create model
model = helper.make_model(graph, producer_name='contractml')

# Save
onnx.save(model, 'models/telemetry/v2/model.onnx')