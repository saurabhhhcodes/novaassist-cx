import os
import subprocess
from dotenv import load_dotenv

def run_command(cmd, env=None):
    print(f"Running: {cmd}")
    result = subprocess.run(cmd, shell=True, env=env)
    if result.returncode != 0:
        print(f"Command failed with code {result.returncode}")
        return False
    return True

def main():
    load_dotenv()
    
    aws_access_key = os.getenv("AWS_ACCESS_KEY_ID")
    aws_secret_key = os.getenv("AWS_SECRET_ACCESS_KEY")
    region = "us-east-1"
    
    env = os.environ.copy()
    env["AWS_ACCESS_KEY_ID"] = aws_access_key
    env["AWS_SECRET_ACCESS_KEY"] = aws_secret_key
    env["AWS_DEFAULT_REGION"] = region
    env["PATH"] = env["PATH"] + ":/home/saurabh/.local/bin"
    
    # Get Account ID
    try:
        account_id = subprocess.check_output("aws sts get-caller-identity --query Account --output text", shell=True, env=env).decode().strip()
        print(f"Account ID: {account_id}")
    except Exception as e:
        print(f"Failed to get account ID: {e}")
        return

    repo_name = "nova-unified"
    repo_uri = f"{account_id}.dkr.ecr.{region}.amazonaws.com/{repo_name}"

    # 1. Create Repo (ignore error if exists)
    subprocess.run(f"aws ecr create-repository --repository-name {repo_name} --region {region}", shell=True, env=env)

    # 2. Login
    login_cmd = f"aws ecr get-login-password --region {region} | docker login --username AWS --password-stdin {account_id}.dkr.ecr.{region}.amazonaws.com"
    if not run_command(login_cmd, env=env): return

    # 3. Build
    if not run_command("docker build -t nova-unified .", env=env): return

    # 4. Tag
    if not run_command(f"docker tag nova-unified:latest {repo_uri}:latest", env=env): return

    # 5. Push
    if not run_command(f"docker push {repo_uri}:latest", env=env): return

    print("✅ PUSH SUCCESSFUL")

if __name__ == "__main__":
    main()
