#!/usr/bin/env bash
set -euo pipefail

PROTO_DIR="shared/proto"
OUT_PY="shared/generated/python"
OUT_GO="shared/generated/go"
OUT_TS="shared/generated/ts"

PY_PROTO_INCLUDE=$(python -c 'import pkg_resources,grpc_tools;print(pkg_resources.resource_filename("grpc_tools","_proto"))')
mkdir -p "$OUT_PY" "$OUT_GO" "$OUT_TS"

python -m grpc_tools.protoc \
    -I "$PROTO_DIR" -I "$PY_PROTO_INCLUDE" \
    --python_out="$OUT_PY" \
    --grpc_python_out="$OUT_PY" \
    "$PROTO_DIR"/*.proto

protoc -I "$PROTO_DIR" -I "$PY_PROTO_INCLUDE" \
    --go_out="$OUT_GO" \
    --go_opt=paths=source_relative \
    "$PROTO_DIR"/*.proto

protoc -I "$PROTO_DIR" -I "$PY_PROTO_INCLUDE" \
    --plugin="protoc-gen-ts_proto=$(which protoc-gen-ts_proto)" \
    --ts_proto_out="$OUT_TS" \
    "$PROTO_DIR"/*.proto

echo "Protobuf generation complete."
