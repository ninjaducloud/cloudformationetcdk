
from aws_cdk import core as cdk, aws_ec2 as ec2, aws_iam as iam

# For consistency with other languages, `cdk` is the preferred import name for
# the CDK's core module.  The following line also imports it as `core` for use
# with examples from the CDK Developer's Guide, which are in the process of
# being updated to use `cdk`.  You may delete this import if you don't need it.
from aws_cdk import core


class CdkStack(cdk.Stack):
    def __init__(self, scope: cdk.Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # The code that defines your stack goes here

        vpc_cidr = self.node.try_get_context("vpc_cidr")

        # Creation VPC
        vpc = ec2.Vpc(
            self,
            "VPC-Demo-Mois-DevOps",
            max_azs=1,
            cidr=vpc_cidr,
            subnet_configuration=[
                ec2.SubnetConfiguration(
                    subnet_type=ec2.SubnetType.PUBLIC,
                    name="Public-Subnet-Demo-Mois-DevOps",
                    cidr_mask=22,
                ),
                ec2.SubnetConfiguration(
                    subnet_type=ec2.SubnetType.PRIVATE,
                    name="Private-Subnet1-Demo-Mois-DevOps",
                    cidr_mask=22,
                ),
                ec2.SubnetConfiguration(
                    subnet_type=ec2.SubnetType.PRIVATE,
                    name="Private-Subnet2-Demo-Mois-DevOps",
                    cidr_mask=22,
                ),
            ],
            nat_gateways=1,
        )

        # Role
        ec2_role = iam.Role(
            self,
            "SSM-Role",
            assumed_by=iam.ServicePrincipal("ec2.amazonaws.com"),
            description="Role pour SSM",
            managed_policies=[
                iam.ManagedPolicy.from_managed_policy_arn(
                    self,
                    "managedpolicy",
                    managed_policy_arn="arn:aws:iam::aws:policy/AmazonSSMManagedInstanceCore",
                )
            ],
        )

        # AMI
        amzn_linux = ec2.MachineImage.latest_amazon_linux(
            generation=ec2.AmazonLinuxGeneration.AMAZON_LINUX_2,
            edition=ec2.AmazonLinuxEdition.STANDARD,
            virtualization=ec2.AmazonLinuxVirt.HVM,
            storage=ec2.AmazonLinuxStorage.GENERAL_PURPOSE,
        )

        # EC2
        instance = ec2.Instance(
            self,
            "VMLinux-Demo-Mois-DevOps",
            instance_type=ec2.InstanceType("t3.small"),
            machine_image=amzn_linux,
            vpc=vpc,
            vpc_subnets=ec2.SubnetSelection(subnet_type=ec2.SubnetType.PRIVATE),
            role=ec2_role,
        )

        # Groupe de securite
        instance.connections.allow_from_any_ipv4(ec2.Port.tcp(22), "Access SSH")


