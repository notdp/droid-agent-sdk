"""Tests for protocol module."""

import json

from droid_agent_sdk.protocol import (
    JsonRpcRequest,
    JsonRpcResponse,
    JsonRpcNotification,
    add_user_message_request,
    initialize_session_request,
    load_session_request,
    parse_message,
)


def test_jsonrpc_request():
    req = JsonRpcRequest(method="test.method", params={"key": "value"}, id="test-1")
    data = json.loads(req.to_json())
    
    assert data["jsonrpc"] == "2.0"
    assert data["type"] == "request"
    assert data["factoryApiVersion"] == "1.0.0"
    assert data["method"] == "test.method"
    assert data["params"] == {"key": "value"}
    assert data["id"] == "test-1"


def test_jsonrpc_response():
    resp = JsonRpcResponse.from_json({
        "id": "test-1",
        "result": {"sessionId": "abc-123"},
    })
    
    assert resp.id == "test-1"
    assert resp.result == {"sessionId": "abc-123"}
    assert resp.is_error is False


def test_jsonrpc_response_error():
    resp = JsonRpcResponse.from_json({
        "id": "test-1",
        "error": {"code": -32603, "message": "Internal error"},
    })
    
    assert resp.is_error is True
    assert resp.error["code"] == -32603


def test_initialize_session_request():
    req = initialize_session_request("my-machine", "/tmp/test")
    data = json.loads(req.to_json())
    
    assert data["method"] == "droid.initialize_session"
    assert data["params"]["machineId"] == "my-machine"
    assert data["params"]["cwd"] == "/tmp/test"


def test_load_session_request():
    req = load_session_request("session-123")
    data = json.loads(req.to_json())
    
    assert data["method"] == "droid.load_session"
    assert data["params"]["sessionId"] == "session-123"


def test_add_user_message_request():
    req = add_user_message_request("Hello, world!")
    data = json.loads(req.to_json())
    
    assert data["method"] == "droid.add_user_message"
    assert data["params"]["text"] == "Hello, world!"


def test_parse_response():
    line = json.dumps({
        "jsonrpc": "2.0",
        "type": "response",
        "factoryApiVersion": "1.0.0",
        "id": "init",
        "result": {"sessionId": "abc"},
    })
    
    msg = parse_message(line)
    assert isinstance(msg, JsonRpcResponse)
    assert msg.result["sessionId"] == "abc"


def test_parse_notification():
    line = json.dumps({
        "jsonrpc": "2.0",
        "type": "notification",
        "factoryApiVersion": "1.0.0",
        "method": "droid.session_notification",
        "params": {"notification": {"type": "text_delta", "text": "Hello"}},
    })
    
    msg = parse_message(line)
    assert isinstance(msg, JsonRpcNotification)
    assert msg.method == "droid.session_notification"
