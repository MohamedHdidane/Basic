from mythic_container.MythicCommandBase import *
from mythic_container.MythicRPC import *
import json

class ShellCommand(CommandBase):
    cmd = "shell"
    needs_admin = False
    help_cmd = "shell [command]"
    description = "Execute a shell command on the target system"
    version = 1
    author = "xAI"
    attack_mapping = ["T1059.004"]
    attributes = CommandAttributes(suggested_command=True)
    
    parameters = [
        CommandParameter(
            name="command",
            type=CommandParameterType.String,
            description="Command to execute",
            required=True
        )
    ]
    
    async def opsec_pre(self, taskData: PTTaskMessageAllData) -> PTTaskOPSECPreTaskMessageResponse:
        response = PTTaskOPSECPreTaskMessageResponse(
            TaskID=taskData.Task.ID, Success=True, OpsecPreBlocked=False
        )
        cmd = taskData.args.get_arg("command").lower()
        if "rm -rf" in cmd or "delete" in cmd:
            response.OpsecPreBlocked = True
            response.OpsecPreMessage = "Command may be destructive. Please confirm."
            response.OpsecPreBypassRole = "lead"
        return response
    
    async def create_go_tasking(self, taskData: PTTaskMessageAllData) -> PTTaskCreateTaskingMessageResponse:
        response = PTTaskCreateTaskingMessageResponse(
            TaskID=taskData.Task.ID, Success=True
        )
        response.DisplayParams = taskData.args.get_arg("command")
        
        await SendMythicRPCArtifactCreate(MythicRPCArtifactCreateMessage(
            TaskID=taskData.Task.ID,
            ArtifactMessage=f"shell {taskData.args.get_arg('command')}",
            BaseArtifactType="Process Create"
        ))
        return response
    
    async def process_response(self, task: PTTaskMessageAllData, response: any) -> PTTaskProcessResponseMessageResponse:
        resp = PTTaskProcessResponseMessageResponse(TaskID=task.Task.ID, Success=True)
        await SendMythicRPCResponseCreate(MythicRPCResponseCreateMessage(
            TaskID=task.Task.ID,
            Response=response.get("output", "No output").encode()
        ))
        return resp