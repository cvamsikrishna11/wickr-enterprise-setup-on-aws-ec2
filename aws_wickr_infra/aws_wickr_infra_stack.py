from aws_cdk import (
    Duration,
    Stack,
    CfnParameter,
    CfnOutput,
    aws_ec2 as ec2,
    aws_iam as iam
)
from constructs import Construct

class AwsWickrInfraStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)


        # Parameters
        messVoiceVidAZ = CfnParameter(self, "messVoiceVidAZ",
            type="String",
            description="The AZ used for your Messaging and VoiceVideo instances.",
            default="us-east-1a"
        )
        
        complianceAZ = CfnParameter(self, "complianceAZ",
            type="String",
            description="The AZ used for your Compliance instance.",
            default="us-east-1b"
        )
        
        sshIp = CfnParameter(self, "sshIp",
            type="String",
            description="The IP that you will administer the instances from via SSH."
        )
        
        keyPair = CfnParameter(self, "keyPair",
            type="String",
            description="The keypair that you will use for SSH into your instances."
        )
        
        EBSsize = CfnParameter(self, "EBSsize",
            type="Number",
            description="The size in GB of the instances (120G minimum required).",
            default=120
        )
        
        
        
        
        # User Data
        with open('./user-data-scripts/compliance-config.sh', 'r') as file:
            complianceUserData = file.read()
        with open('./user-data-scripts/messaging-config-v1.sh', 'r') as file:
            messagingUserData = file.read()
        with open('./user-data-scripts/voicevideo-config.sh', 'r') as file:
            voicevideoUserData = file.read()
        
        # VPC
        vpc = ec2.Vpc(self, 'VPC', 
            availability_zones=[messVoiceVidAZ.value_as_string, complianceAZ.value_as_string]
        )
        
        
        # IAM Role
        role = iam.Role(self, 'ec2Role',
            assumed_by=iam.ServicePrincipal('ec2.amazonaws.com')
        )
        role.add_managed_policy(iam.ManagedPolicy.from_aws_managed_policy_name('AmazonSSMManagedInstanceCore'))
        
        
        # Security Groups
        complianceSecurityGroup = ec2.SecurityGroup(self, 'Compliance Security Group', 
            vpc=vpc, 
            description='Ingress rules required for Wickr Compliance Server',
            security_group_name='Compliance Ingress',
            allow_all_outbound=True
        )
        
        messagingSecurityGroup = ec2.SecurityGroup(self, 'Messaging Security Group', 
            vpc=vpc, 
            description='Ingress rules required for Wickr Messaging Server',
            security_group_name='Messaging Ingress',
            allow_all_outbound=True
        )

        voicevideoSecurityGroup = ec2.SecurityGroup(self, 'Voice and Video Security Group', 
            vpc=vpc, 
            description='Ingress rules required for Wickr Voice and Video Server',
            security_group_name='Voice and Video Ingress',
            allow_all_outbound=True
        )
        
        # EIP
        messagingEip = ec2.CfnEIP(self, "Messaging EIP")
        voicevideoEip = ec2.CfnEIP(self, "VoiceVideo EIP")
        
        # AMI
        ami = ec2.AmazonLinuxImage(
            generation=ec2.AmazonLinuxGeneration.AMAZON_LINUX_2,
            cpu_type=ec2.AmazonLinuxCpuType.X86_64
        )
        
        #Compliance EC2 instance
        complianceEc2Instance = ec2.Instance(self, 'Retention',
            vpc=vpc,
            instance_type=ec2.InstanceType.of(ec2.InstanceClass.T3, ec2.InstanceSize.LARGE),
            vpc_subnets={
                'subnet_type': ec2.SubnetType.PRIVATE_WITH_NAT,
                'availability_zones': [complianceAZ.value_as_string]
            },
            machine_image=ami,
            block_devices=[
                ec2.BlockDevice(
                    device_name='/dev/xvda',
                    volume=ec2.BlockDeviceVolume.ebs(
                        EBSsize.value_as_number, 
                        delete_on_termination=True,
                        encrypted=True
                    )
                )
            ],
            security_group=complianceSecurityGroup,
            key_name=keyPair.value_as_string,
            role=role,
            user_data=ec2.UserData.custom(complianceUserData)
        )


        
        
        # Voice and Video EC2 instance
        voicevideoEc2Instance = ec2.Instance(self, 'VoiceVideo',
            vpc=vpc,
            instance_type=ec2.InstanceType.of(ec2.InstanceClass.T3, ec2.InstanceSize.LARGE),
            vpc_subnets={
                'subnet_type': ec2.SubnetType.PUBLIC,
                'availability_zones': [messVoiceVidAZ.value_as_string]
            },
            machine_image=ami,
            block_devices=[
                ec2.BlockDevice(
                    device_name='/dev/xvda',
                    volume=ec2.BlockDeviceVolume.ebs(EBSsize.value_as_number, 
                        delete_on_termination=True,
                        encrypted=True
                    )
                )
            ],
            security_group=voicevideoSecurityGroup,
            key_name=keyPair.value_as_string,
            role=role,
            user_data=ec2.UserData.custom(voicevideoUserData)
        )
        # Associate EIP to Messaging EC2 instance
        voicevideoEipAssoc = ec2.CfnEIPAssociation(self, "VoiceVideoEIPAssociation",
            eip=voicevideoEip.ref,
            instance_id=voicevideoEc2Instance.instance_id
        )
    
        
        # Voicevideo Server Security Group Ingress Rules
        voicevideoSecurityGroup.add_ingress_rule(
            ec2.Peer.ipv4(sshIp.value_as_string), 
            ec2.Port.tcp(22), 
            'Allow SSH Access'
        )
        voicevideoSecurityGroup.add_ingress_rule(
            ec2.Peer.any_ipv4(), 
            ec2.Port.udp_range(16384, 17384), 
            'Audio and Video'
        )
        voicevideoSecurityGroup.add_ingress_rule(
            messagingSecurityGroup, 
            ec2.Port.tcp(444), 
            'Messaging Server'
        )
        voicevideoSecurityGroup.add_ingress_rule(
            ec2.Peer.any_ipv4(), 
            ec2.Port.tcp(8001), 
            'SOCKS Proxy'
        )
        voicevideoSecurityGroup.add_ingress_rule(
            ec2.Peer.any_ipv4(), 
            ec2.Port.tcp(443), 
            'TCP Proxy'
        )
        
        

        # Messaging EC2 instance
        messagingEc2Instance = ec2.Instance(self, 'Messaging',
            vpc=vpc,
            instance_type=ec2.InstanceType.of(ec2.InstanceClass.T3, ec2.InstanceSize.LARGE),
            vpc_subnets={
                'subnet_type': ec2.SubnetType.PUBLIC,
                'availability_zones': [messVoiceVidAZ.value_as_string]
            },
            machine_image=ami,
            block_devices=[
                ec2.BlockDevice(
                    device_name='/dev/xvda',
                    volume=ec2.BlockDeviceVolume.ebs(EBSsize.value_as_number, 
                    delete_on_termination=True,
                    encrypted=True
                    )
                )
            ],
            security_group=messagingSecurityGroup,
            key_name=keyPair.value_as_string,
            role=role,
            user_data=ec2.UserData.custom(messagingUserData)
        )
        
        
        # Associate EIP to Messaging EC2 instance
        messagingEipAssoc = ec2.CfnEIPAssociation(self, "MessagingEIPAssociation",
            eip=messagingEip.ref,
            instance_id=messagingEc2Instance.instance_id
        )
        
        # Messaging Server Security Group Ingress Rules
        messagingSecurityGroup.add_ingress_rule(
            ec2.Peer.any_ipv4(), 
            ec2.Port.tcp(22), 
            'SSH Access'
        )
        messagingSecurityGroup.add_ingress_rule(
            ec2.Peer.ipv4(sshIp.value_as_string), 
            ec2.Port.tcp(8800), 
            'Installer UI Admin Console'
        )
        messagingSecurityGroup.add_ingress_rule(
            ec2.Peer.any_ipv4(), 
            ec2.Port.tcp(443), 
            'Client'
        )
        messagingSecurityGroup.add_ingress_rule(
            voicevideoSecurityGroup, 
            ec2.Port.tcp_range(9870, 9881), 
            'Voice and Video'
        )
        messagingSecurityGroup.add_ingress_rule(
            complianceSecurityGroup, 
            ec2.Port.tcp(443), 
            'Compliance Server'
        )
        
        # Output
        CfnOutput(self, "Compliance Private IP (use SSM Session Manager/SSM SSH for access", value=complianceEc2Instance.instance_id)
        CfnOutput(self, "Messaging Public IP", value=messagingEc2Instance.instance_public_ip)
        CfnOutput(self, "Voice & Video Public IP", value=voicevideoEc2Instance.instance_public_ip)
