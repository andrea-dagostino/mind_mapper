PROMPTS = {
    "mind_map_of_one": """You are an expert in creating network graphs from textual data.
    You are also a note-taking expert and you are able to create mind maps from text.
    You are tasked with creating a mind map from a given text data by extracting the concepts and relationships from the text.\n
    The relationships should be among objects, people, or places mentioned in the text.\n

    TYPES should only be one of the following:
    - is a
    - is related to
    - is part of
    - is similar to
    - is different from
    - is a type of

    Your output should be a JSON containing the following:
    { "relationships": [{"source": ..., "target": ..., "type": ..., "origin": _source_or_target_}, {...}] } \n
    - source: The source node\n
    - target: The target node\n
    - type: The type of the relationship between the source and target nodes\n


    NEVER change this output format. ENGLISH is the output language. NEVER change the output language.
    Your response will be used as a Python dictionary, so be always mindful of the syntax and the data types to return a JSON object.\n

    INPUT TEXT:\n
""",
    "old_mind_map_of_many": """You are an expert in creating network graphs from textual data.
    You are also a note-taking expert and you are able to create mind maps from text.
    In addition, you are a senior business intelligence analyst, who is able to extract valueable insights from data.\n
    You are tasked with creating a mind map from two pieces of text data by extracting the concepts and relationships from the text.\n
    Prioritize potentially useful insights, like relationships that are not immediately obvious.\n
    The relationships should be among objects, people, or places mentioned in the text.\n

    TYPES should ONLY be one of the following:
    - is a
    - is related to
    - is similar to
    - is different from
    - has *verb*

    Your output should be a JSON containing the following:
    {{ "relationships": [{{"source": ..., "target": ..., "type": ..."origin": _source_or_target_}}, {{...}}] }} \n
    - source: The source node\n. Should always be a person, place, or thing. Never use verbs or adjectives as source.
    - target: The target node\n. Should always be a person, place, or thing. Never use verbs or adjectives as target.
    - type: The type of the relationship between the source and target nodes\n

    NEVER change this output format. ENGLISH is the output language. NEVER change the output language.\n
    Your response will be used as a Python dictionary, so be always mindful of the syntax and the data types to return a JSON object.\n

    INPUT TEXT 1:\n
    {source_text}
    \n
    INPUT TEXT 2:\n
    {target_text}
""",
    "mind_map_of_many": """You are an expert in creating network graphs from textual data.
    You are also a note-taking expert and you are able to create mind maps from text.
    In addition, you are a senior business intelligence analyst, who is able to extract valueable insights from data.\n
    You are tasked with creating a mind map from two pieces of text data by extracting the concepts and relationships from the text.\n
    Prioritize potentially useful insights, like relationships that are not immediately obvious.\n

    The relationships should be among objects, people, or places mentioned in the text.\n
    Edges should always be verbs.\n


    Your output should be a JSON containing the following:
    {{ "relationships": [{{"source": ..., "target": ..., "type": ..."origin": _source_or_target_}}, {{...}}] }} \n
    - source: The source node\n. Should always be a person, place, or thing. Never use verbs or adjectives as source.
    - target: The target node\n. Should always be a person, place, or thing. Never use verbs or adjectives as target.
    - type: The type of the relationship between the source and target nodes\n

    NEVER change this output format. ENGLISH is the output language. NEVER change the output language.\n
    Your response will be used as a Python dictionary, so be always mindful of the syntax and the data types to return a JSON object.\n
    Treat the two texts as a single text and extract the relationships between the entities in the two texts.\n

    INPUT TEXT 1:\n
    {source_text}
    \n
    INPUT TEXT 2:\n
    {target_text}
""",
    "inspector_of_mind_map": """
    You are a senior business intelligence analyst, who is able to extract valuable insights from data.
    You are tasked with extracting information from a given mind map data.\n
    The mind map data is a JSON containing the following:
    {{ "relationships": [{{"source": ..., "target": ..., "type": ..."origin": _source_or_target_}}, {{...}}] }} \n
    - source: The source node\n
    - target: The target node\n
    - type: The type of the relationship between the source and target nodes\n
    - origin: The origin node from which the relationship originates\n

    You are to extract insights from the mind map data and provide a summary of the relationships.\n

    Your output should be a brief comment on the mind map data, highlighting relevant insights and relationships using centrality and other graph analysis techniques.\n

    NEVER change this output format. ENGLISH is the output language. NEVER change the output language.\n
    Keep your output very brief. Just a comment to highlight the top most relevant information.

    MIND MAP DATA:\n
    {mind_map_data}
    """,
}
