
schema_examples = {
    "chart_type_schema": {
        "type": "object",
        "properties": {
            "chart_type": {
                "type": "string",
                "enum": ["Counter", "Table", "Column", "Bar", "Line", "Spline", "Pie"],
                "description": "The chart type name that can be used to plot the data for user query from the selected enums",
            }
        },
        "required": ["chart_type"],
    }
}
json_examples = [
    {
        "system_prompt": "You are a helpful assistant!",
        "prompt": "Dell retweet sentiment analysis!",
        "schema": schema_examples["chart_type_schema"]
    },
    {
        "prompt": "Change the filters",
        "response": {"chart_type": "Table"},
        "schema": schema_examples["chart_type_schema"]
    }
]
