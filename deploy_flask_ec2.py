import boto3
from botocore.exceptions import ClientError

# -------- SETTINGS --------
REGION = "us-east-1"                      # your AWS region
KEY_NAME = "new-key-2"            # replace with your EC2 key pair name (no .pem)
GITHUB_REPO = "https://github.com/YourGitHubUsername/FOOD_ORDERING_APP.git"  # replace with your repo URL
SECURITY_GROUP_NAME = "flask-sg"          # security group name
INSTANCE_TYPE = "t3.micro"                # Free-tier eligible
AMI_ID = "ami-0c7217cdde317cfec"          # Ubuntu 22.04 LTS
# -----------------------------------------

ec2 = boto3.client("ec2", region_name=REGION)

# 1️⃣ Create or reuse security group
try:
    response = ec2.create_security_group(
        GroupName=SECURITY_GROUP_NAME,
        Description="Allow SSH and Flask traffic"
    )
    sg_id = response["GroupId"]
    ec2.authorize_security_group_ingress(
        GroupId=sg_id,
        IpPermissions=[
            {
                "IpProtocol": "tcp",
                "FromPort": 22,
                "ToPort": 22,
                "IpRanges": [{"CidrIp": "0.0.0.0/0"}]
            },
            {
                "IpProtocol": "tcp",
                "FromPort": 5000,
                "ToPort": 5000,
                "IpRanges": [{"CidrIp": "0.0.0.0/0"}]
            }
        ]
    )
    print(f"✅ Created new security group: {sg_id}")

except ClientError as e:
    if "InvalidGroup.Duplicate" in str(e):
        # Get existing SG ID
        sg_list = ec2.describe_security_groups(GroupNames=[SECURITY_GROUP_NAME])
        sg_id = sg_list["SecurityGroups"][0]["GroupId"]
        print(f"✅ Reusing existing security group: {sg_id}")
    else:
        raise

# 2️⃣ User data script (runs on instance startup)
user_data_script = f"""#!/bin/bash
sudo apt update -y
sudo apt install python3-pip git -y
cd /home/ubuntu
git clone {GITHUB_REPO}
cd FOOD_ORDERING_APP
pip3 install -r requirements.txt
nohup python3 app.py &
"""

# 3️⃣ Launch EC2 instance
print("🚀 Launching EC2 instance...")
instance = ec2.run_instances(
    ImageId=AMI_ID,
    InstanceType=INSTANCE_TYPE,
    MinCount=1,
    MaxCount=1,
    KeyName=KEY_NAME,
    SecurityGroupIds=[sg_id],
    UserData=user_data_script
)

instance_id = instance["Instances"][0]["InstanceId"]
print(f"🆔 Instance ID: {instance_id}")

# 4️⃣ Wait until running
ec2_resource = boto3.resource("ec2", region_name=REGION)
ec2_instance = ec2_resource.Instance(instance_id)
print("⏳ Waiting for instance to start...")
ec2_instance.wait_until_running()

# 5️⃣ Get public IP
ec2_instance.reload()
public_ip = ec2_instance.public_ip_address

print("\n✅ Deployment complete!")
print(f"🌍 Flask app is being served at: http://{public_ip}:5000")
print(f"🔑 Connect via SSH: ssh -i {KEY_NAME}.pem ubuntu@{public_ip}")
