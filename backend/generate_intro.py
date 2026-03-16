import boto3
import os
from dotenv import load_dotenv

load_dotenv()

def generate_intro():
    polly = boto3.client('polly', region_name=os.getenv("AWS_REGION", "us-east-1"))
    
    script = """
    Welcome to NovaAssist CX, the next generation of Enterprise Agentic Intelligence. 
    Built for the Amazon Nova AI Hackathon, this platform transforms customer support from reactive to autonomous.
    Utilizing the complete Amazon Nova model portfolio, NovaAssist uses Nova 2 Lite for millisecond-latency reasoning and vision analysis, 
    Nova 2 Sonic for world-class neural voice interactions, and Nova Act for direct workflow automation.
    Observe as Nova manages real-world logistics, synchronizes with enterprise CRM systems, and resolves multimodal technical issues 
    without any human intervention. 
    This is not just a demo. It is the future of autonomous enterprise operations.
    Designed and built by Saurabh Kumar Bajpai.
    """
    
    response = polly.synthesize_speech(
        Text=script,
        OutputFormat='mp3',
        VoiceId='Joanna',
        Engine='neural'
    )
    
    with open('/home/saurabh/.gemini/antigravity/scratch/novaassist-cx/frontend/public/intro.mp3', 'wb') as f:
        f.write(response['AudioStream'].read())
    
    print("Intro audio generated successfully at frontend/public/intro.mp3")

if __name__ == "__main__":
    generate_intro()
