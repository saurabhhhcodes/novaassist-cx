import boto3
import json
import base64
import os
from typing import List, Dict, Any, Optional

class NovaClient:
    def __init__(self, region_name: str = "us-east-1"):
        self.mock_mode = os.getenv("MOCK_SERVICES", "true").lower() == "true"
        if self.mock_mode:
            self.bedrock_runtime = None
            print("NovaClient: Running in MOCK MODE")
        else:
            self.bedrock_runtime = boto3.client(
                service_name="bedrock-runtime",
                region_name=region_name
            )
            self.polly = boto3.client(
                service_name="polly",
                region_name=region_name
            )
            self.transcribe = boto3.client(
                service_name="transcribe",
                region_name=region_name
            )
            self.s3 = boto3.client(
                service_name="s3",
                region_name=region_name
            )
    def get_embeddings(self, text: str) -> List[float]:
        """
        Generates text embeddings using Amazon Titan.
        """
        if self.mock_mode:
            return [0.1] * 1536
            
        model_id = "amazon.titan-embed-text-v1"
        body = json.dumps({"inputText": text})
        
        response = self.bedrock_runtime.invoke_model(
            body=body,
            modelId=model_id,
            accept="application/json",
            contentType="application/json"
        )
        
        response_body = json.loads(response.get("body").read())
        return response_body.get("embedding")
    def invoke_nova_lite(self, prompt: str, system_prompt: str = "") -> str:
        """
        Nova 2 Lite for reasoning and generated support responses.
        Uses Bedrock Converse API.
        """
        if self.mock_mode:
            return f"[MOCK] This is a simulated response for: {prompt[:50]}..."
        
        model_id = "us.amazon.nova-lite-v1:0"
        
        messages = [
            {"role": "user", "content": [{"text": prompt}]}
        ]
        
        system = [{"text": system_prompt}] if system_prompt else []
        
        response = self.bedrock_runtime.converse(
            modelId=model_id,
            messages=messages,
            system=system,
            inferenceConfig={"maxTokens": 1000, "temperature": 0.7}
        )
        
        return response["output"]["message"]["content"][0]["text"]

    def invoke_nova_sonic(self, prompt: str) -> str:
        """
        Nova 2 Sonic for faster processing/voice responses.
        Falling back to Lite if Sonic has compatibility issues.
        """
        if self.mock_mode:
            return f"[MOCK] Sonic response: {prompt[:50]}"
            
        # Using Lite for now as Sonic had ValidationErrors with Converse in this region
        model_id = "amazon.nova-lite-v1:0" 
        
        messages = [
            {"role": "user", "content": [{"text": prompt}]}
        ]
        
        response = self.bedrock_runtime.converse(
            modelId=model_id,
            messages=messages,
            inferenceConfig={"maxTokens": 500}
        )
        
        return response["output"]["message"]["content"][0]["text"]

    def analyze_image(self, image_bytes: bytes, prompt: str) -> str:
        """
        Nova Lite 2 for image understanding. Supports PNG and JPEG.
        """
        if self.mock_mode:
            return "[MOCK] Image analysis result."
            
        # Basic format detection
        img_format = "png"
        if image_bytes.startswith(b'\xff\xd8'):
            img_format = "jpeg"
        elif image_bytes.startswith(b'\x89PNG'):
            img_format = "png"
            
        model_id = "amazon.nova-lite-v1:0"
        
        messages = [
            {
                "role": "user",
                "content": [
                    {
                        "image": {
                            "format": img_format, 
                            "source": {"bytes": image_bytes}
                        }
                    },
                    {"text": prompt}
                ]
            }
        ]
        
        response = self.bedrock_runtime.converse(
            modelId=model_id,
            messages=messages,
            inferenceConfig={"maxTokens": 500}
        )
        
        return response["output"]["message"]["content"][0]["text"]

    def invoke_nova_act(self, prompt: str, tools: List[Dict[str, Any]], history: List[Dict[str, Any]] = None, system: str = "") -> Dict[str, Any]:
        """
        Nova Act for tool use and orchestration.
        Using Nova Lite with toolConfig in converse API.
        """
        if (self.mock_mode):
            return {
                "role": "assistant", 
                "content": [{"text": "<thinking>I will analyze the user's request and check the relevant tools to resolve the issue proactively.</thinking> Action completed successfully. How else can I help?"}]
            }

        model_id = "us.amazon.nova-lite-v1:0"
        
        # Use provided history or create new messages array
        messages = history if history else [{"role": "user", "content": [{"text": prompt}]}]
        
        # Converse API tool format
        converse_tools = []
        for tool in tools:
            converse_tools.append({
                "toolSpec": {
                    "name": tool["name"],
                    "description": tool["description"],
                    "inputSchema": {
                        "json": tool["parameters"]
                    }
                }
            })

        system_config = [{"text": system}] if system else []

        response = self.bedrock_runtime.converse(
            modelId=model_id,
            messages=messages,
            system=system_config,
            toolConfig={
                "tools": converse_tools
            }
        )
        return response["output"]["message"]

    def continue_agent_loop(self, messages: List[Dict[str, Any]], tools: List[Dict[str, Any]], system: str = "") -> Dict[str, Any]:
        """
        Continues the agent loop after a tool result has been added to messages.
        """
        model_id = "us.amazon.nova-lite-v1:0"
        
        # Converse API tool format
        converse_tools = []
        for tool in tools:
            converse_tools.append({
                "toolSpec": {
                    "name": tool["name"],
                    "description": tool["description"],
                    "inputSchema": {
                        "json": tool["parameters"]
                    }
                }
            })
        
        system_config = [{"text": system}] if system else []

        response = self.bedrock_runtime.converse(
            modelId=model_id,
            messages=messages,
            system=system_config,
            toolConfig={
                "tools": converse_tools
            }
        )
        return response["output"]["message"]

    def generate_speech(self, text: str) -> bytes:
        """
        Generates speech from text using Amazon Polly.
        """
        if self.mock_mode:
            return b"MOCK_AUDIO_DATA"
            
        response = self.polly.synthesize_speech(
            Text=text,
            OutputFormat="mp3",
            VoiceId="Joanna",
            Engine="neural" # World-class neural engine for faster, human-like speech
        )
        return response["AudioStream"].read()

    def transcribe_audio(self, audio_bytes: bytes, file_name: str) -> str:
        """
        Transcribes audio using Amazon Transcribe.
        Note: Practical production apps usually use Transcribe Streaming, 
        but for this MVP we use the Job-based API for reliability in standard regions.
        """
        if (self.mock_mode):
            import time
            time.sleep(0.5) # Slight delay to feel real but much faster than 13s
            return "Help me with my order status or refund."

        import time
        import requests
        
        bucket = os.getenv("S3_BUCKET_NAME")
        s3_key = f"voice/{int(time.time())}_{file_name}"
        
        # 1. Upload audio to S3
        self.s3.put_object(Bucket=bucket, Key=s3_key, Body=audio_bytes)
        
        # 2. Start Job
        job_name = f"voice_{int(time.time())}"
        self.transcribe.start_transcription_job(
            TranscriptionJobName=job_name,
            Media={'MediaFileUri': f"s3://{bucket}/{s3_key}"},
            MediaFormat='webm',
            LanguageCode='en-US'
        )
        
        # 3. Wait (Optimized Polling)
        while True:
            status = self.transcribe.get_transcription_job(TranscriptionJobName=job_name)
            if status['TranscriptionJob']['TranscriptionJobStatus'] in ['COMPLETED', 'FAILED']:
                break
            time.sleep(0.5) # Reduced polling interval from 1s to 500ms for faster turnaround
            
        if status['TranscriptionJob']['TranscriptionJobStatus'] == 'COMPLETED':
            result_url = status['TranscriptionJob']['Transcript']['TranscriptFileUri']
            content = requests.get(result_url).json()
            return content['results']['transcripts'][0]['transcript']
        
        return "Sorry, I couldn't understand that."
