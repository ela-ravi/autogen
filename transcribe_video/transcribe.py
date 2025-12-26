import autogen
import dotenv

from functions import recognize_transcript_from_video, translate_transcript, generate_recap, extract_video_clips

dotenv.load_dotenv()

config_list = autogen.config_list_from_dotenv(
    dotenv_file_path=".",
    filter_dict={
        "model": ["gpt-4"],
    }
)

llm_config = {
    "functions": [
        {
            "name": "recognize_transcript_from_video",
            "description": "recognize the speech from video and transfer into a txt file",
            "parameters": {
                "type": "object",
                "properties": {
                    "audio_filepath": {
                        "type": "string",
                        "description": "path of the video file",
                    }
                },
                "required": ["audio_filepath"],
            },
        },
        {
            "name": "translate_transcript",
            "description": "using translate_text function to translate the script",
            "parameters": {
                "type": "object",
                "properties": {
                    "source_language": {
                        "type": "string",
                        "description": "source language",
                    },
                    "target_language": {
                        "type": "string",
                        "description": "target language",
                    }
                },
                "required": ["source_language", "target_language"],
            },
        },
        {
            "name": "generate_recap",
            "description": "Generate a 30-second recap text and suggest optimal clip timings from the transcription",
            "parameters": {
                "type": "object",
                "properties": {
                    "target_duration_seconds": {
                        "type": "integer",
                        "description": "target duration for the recap in seconds (default: 30)",
                    }
                },
                "required": [],
            },
        },
        {
            "name": "extract_video_clips",
            "description": "Extract and combine video clips based on the recap generator's suggestions",
            "parameters": {
                "type": "object",
                "properties": {
                    "video_filepath": {
                        "type": "string",
                        "description": "path to the original video file",
                    }
                },
                "required": ["video_filepath"],
            },
        },
    ],
    "config_list": config_list,
    "timeout": 120,
}

chatbot = autogen.AssistantAgent(
    name="chatbot",
    system_message="You are a helpful AI assistant that can transcribe videos, translate transcripts, and create video recaps. "
                   "Use the functions you have been provided with. Reply TERMINATE when the task is done.",
    llm_config=llm_config,
    code_execution_config={"work_dir": "scripts"},
)

user_proxy = autogen.UserProxyAgent(
    name="user_proxy",
    is_termination_msg=lambda x: x.get("content", "") and x.get("content", "").rstrip().endswith("TERMINATE"),
    human_input_mode="NEVER",
    max_consecutive_auto_reply=10,
    code_execution_config={"work_dir": "scripts", "use_docker": False},
)

user_proxy.register_function(
    function_map={
        "recognize_transcript_from_video": recognize_transcript_from_video,
        "translate_transcript": translate_transcript,
        "generate_recap": generate_recap,
        "extract_video_clips": extract_video_clips,
    }
)


def initiate_chat():
    target_video = input("What is your target video path?: ")
    source_language = input("What is the source language? (i.e. English): ")
    target_language = input("What is destination language? (i.e. French): ")
    create_recap = input("Do you want to create a 30-second recap video? (yes/no): ").strip().lower()

    if create_recap in ['yes', 'y']:
        user_proxy.initiate_chat(
            chatbot,
            message=f"For the video located in {target_video}, please do the following tasks in order:\n"
                    f"1. Recognize the speech and transfer it into a transcription file\n"
                    f"2. Translate the transcription from {source_language} to {target_language}\n"
                    f"3. Generate a 30-second recap with clip timing suggestions\n"
                    f"4. Extract and combine the video clips to create the recap video\n"
                    f"Reply TERMINATE when all tasks are complete.",
        )
    else:
        user_proxy.initiate_chat(
            chatbot,
            message=f"For the video located in {target_video}, recognize the speech and transfer it into a script file, "
                    f"then translate from {source_language} text to a {target_language} video subtitle text. "
                    f"Reply TERMINATE when done.",
        )


initiate_chat()