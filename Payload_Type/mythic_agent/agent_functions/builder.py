from mythic_container.PayloadBuilder import *
from mythic_container.MythicCommandBase import *
import json
import os
import pathlib

class MythicAgent(PayloadType):
    name = "mythic_agent"
    file_extension = "py"
    author = "xAI"
    supported_os = [SupportedOS.Linux]
    wrapper = False
    wrapped_payloads = []
    description = "A Python-based Linux agent with HTTP C2"
    supports_dynamic_loading = True
    c2_profiles = ["http"]
    mythic_encrypts = True
    translation_container = None
    build_parameters = [
        BuildParameter(
            name="c2_url",
            parameter_type=BuildParameterType.String,
            description="URL of the C2 server (e.g., http://example.com:8080)",
            required=True
        ),
        BuildParameter(
            name="encryption_key",
            parameter_type=BuildParameterType.String,
            description="AES encryption key (32 bytes)",
            required=True,
            default_value="x" * 32
        )
    ]
    agent_path = pathlib.Path(".") / "mythic_agent"
    agent_code_path = agent_path / "agent_code"
    build_steps = [
        BuildStep(step_name="Gathering Files", step_description="Collecting source files"),
        BuildStep(step_name="Configuring", step_description="Embedding C2 parameters")
    ]

    async def build(self) -> BuildResponse:
        resp = BuildResponse(status=BuildStatus.Success)
        try:
            c2_url = self.get_parameter("c2_url")
            encryption_key = self.get_parameter("encryption_key")
            agent_code_path = str(self.agent_code_path / "agent.py")
            
            # Replace placeholders in agent.py
            with open(agent_code_path, "r") as f:
                code = f.read()
            code = code.replace("{{C2_URL}}", c2_url)
            code = code.replace("{{ENCRYPTION_KEY}}", encryption_key)
            
            # Save the configured agent script
            output_path = str(self.agent_code_path / "mythic_agent.py")
            with open(output_path, "w") as f:
                f.write(code)
            
            # Read the configured script as the payload
            with open(output_path, "rb") as f:
                resp.payload = f.read()
        
        except Exception as e:
            resp.status = BuildStatus.Error
            resp.message = str(e)
        
        return resp