from mythic_container.MythicCommandBase import *
from mythic_container.MythicRPC import *
import json

class DownloadCommand(CommandBase):
    cmd = "download"
    needs_admin = False
    help_cmd = "download [path]"
    description = "Download a file from the target system"
    version = 1
    author = "xAI"
    attack_mapping = ["T1105"]
    
    parameters = [
        CommandParameter(
            name="path",
            type=CommandParameterType.ChooseOne,
            description="File path to download",
            dynamic_query_function="get_files"
        )
    ]
    
    async def get_files(self, inputMsg: PTRPCDynamicQueryFunctionMessage) -> list:
        # Simulated file list; replace with RPC call to fetch actual files
        files = ["file1.txt", "file2.txt"]
        return files
    
    async def opsec_pre(self, taskData: PTTaskMessageAllData) -> PTTaskOPSECPreTaskMessageResponse:
        response = PTTaskOPSECPreTaskMessageResponse(
            TaskID=taskData.Task.ID, Success=True, OpsecPreBlocked=False
        )
        path = taskData.args.get_arg("path")
        if "/etc/passwd" in path or "/etc/shadow" in path:
            response.OpsecPreBlocked = True
            response.OpsecPreMessage = "Attempting to access sensitive files."
            response.OpsecPreBypassRole = "lead"
        return response
    
    async def create_go_tasking(self, taskData: PTTaskMessageAllData) -> PTTaskCreateTaskingMessageResponse:
        response = PTTaskCreateTaskingMessageResponse(
            TaskID=taskData.Task.ID, Success=True
        )
        response.DisplayParams = taskData.args.get_arg("path")
        
        await SendMythicRPCArtifactCreate(MythicRPCArtifactCreateMessage(
            TaskID=taskData.Task.ID,
            ArtifactMessage=f"download {taskData.args.get_arg('path')}",
            BaseArtifactType="File Read"
        ))
        return response
    
    async def process_response(self, task: PTTaskMessageAllData, response: any) -> PTTaskProcessResponseMessageResponse:
        resp = PTTaskProcessResponseMessageResponse(TaskID=task.Task.ID, Success=True)
        if "file_data" in response:
            await SendMythicRPCFileCreate(MythicRPCFileCreateMessage(
                TaskID=task.Task.ID,
                FileContents=response["file_data"],
                Filename=task.args.get_arg("path").split("/")[-1]
            ))
        return resp