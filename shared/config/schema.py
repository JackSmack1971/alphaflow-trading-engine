"""JSON schema for configuration files."""

CONFIG_SCHEMA = {
    "type": "object",
    "properties": {
        "app": {
            "type": "object",
            "properties": {
                "name": {"type": "string"},
                "log_level": {"type": "string"},
            },
            "required": ["name", "log_level"],
        },
        "database": {
            "type": "object",
            "properties": {
                "host": {"type": "string"},
                "port": {"type": "integer"},
                "name": {"type": "string"},
            },
            "required": ["host", "port", "name"],
        },
        "redis": {
            "type": "object",
            "properties": {
                "host": {"type": "string"},
                "port": {"type": "integer"},
            },
            "required": ["host", "port"],
        },
    },
    "required": ["app", "database", "redis"],
}
