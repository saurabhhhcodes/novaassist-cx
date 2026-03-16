import requests
import json
import time
import base64

API_URL = "http://127.0.0.1:8002/support/voice"
EMAIL = "saurabh@exclusive.com"

def test_voice_latency():
    print(f"\n--- World-Class Voice Latency Audit ---")
    
    # Simulate a voice upload (using the mock transcription "Help me with my order")
    # We use a dummy webm file content
    dummy_audio = b"dummy_webm_content"
    
    files = {'file': ('voice.webm', dummy_audio, 'audio/webm')}
    data = {'email': EMAIL}
    
    start_time = time.time()
    response = requests.post(API_URL, files=files, data=data)
    latency = time.time() - start_time
    
    res_json = response.json()
    
    print(f"Status: {response.status_code}")
    print(f"Total Turnaround Latency: {latency:.2f}s")
    print(f"Transcription: {res_json.get('transcription')}")
    print(f"Agent Response: {res_json.get('response')}")
    print(f"Audio Returned: {'YES' if res_json.get('audio') else 'NO'}")
    
    # Check if AgentBrain handled it (should have thinking block if real-loop was used)
    if "<thinking>" in res_json.get('response'):
        print("✅ SUCCESS: Voice path is AGENTIC (Brain used).")
    else:
        print("❌ FAILURE: Voice path is still non-agentic.")

    if latency < 5.0: # 5s is high-end for job-based Transcribe, but with 500ms polling it should be better
        print(f"✅ PERFORMANCE: Latency is within world-class limits for Job-based API.")
    else:
        print(f"⚠️ ADVISORY: Latency {latency:.2f}s suggests further streaming optimization may be needed for real-time needs.")

if __name__ == "__main__":
    test_voice_latency()
