# Schema Planner

An LLM planning tool for generating complex JSON response as per user requested 
schema by breaking down dependent and independent parts of the schema and evaluating
them optimally. It plays an essential role especially in integration of tool calls 
in any chatbot, since all API calls require JSON payload.

**Input**: User Text | JSON Schema

**Output**: Output JSON

### Features
 - Multipass optimal generation and edit of generated JSON (by maintaining persistent states).
 - Easy pluggable capability of any APIs through OpenAPI spec yaml file.
 - Extremely fast response by maximizing parallelization.
 - Solving complex tasks by small LLMs through task decomposition.
 - Flexibly switching between LLM models for evaluating different parts of JSON based on complexity of requests.

