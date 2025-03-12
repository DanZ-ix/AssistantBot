yandex_gpt_response_schema = {
    "json_schema":
        {
            "schema": "http://json-schema.org/draft-07/schema#",
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "action": {
                        "type": "string",
                        "enum": ["save_note", "general_question"]
                    },
                    "parameters": {
                        "type": "object",
                        "oneOf": [
                            {
                                "required": ["note_text"],
                                "properties": {
                                    "note_text": {
                                        "type": "string"
                                    }
                                }
                            },
                            {
                                "required": ["response"],
                                "properties": {
                                    "response": {
                                        "type": "string"
                                    }
                                }
                            }
                        ]
                    }
                },
                "required": ["action", "parameters"]
            }
        }
}
