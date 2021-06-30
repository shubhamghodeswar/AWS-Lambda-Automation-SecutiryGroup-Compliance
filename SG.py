import json
import boto3

def lambda_handler(event, context):
    
    tagKey = ''
    tagValue = ''
    tagFlag = 0
    
    client = boto3.client('ec2')
    
    eventName = str(event['detail']['eventName'])
    userName = str(event['detail']['userIdentity']['userName'])
    sgGroupId = str(event['detail']['requestParameters']['groupId'])
    ingressIp = str(event['detail']['requestParameters']['ipPermissions']['items'][0]['ipRanges']['items'][0]['cidrIp'])
    
    response = client.describe_security_groups(
        GroupIds = [sgGroupId]
        )
        
    for item in response['SecurityGroups'][0]:
        if(item == 'Tags'):
            tagFlag = 1
    
    if(tagFlag == 1):
        tagInfo = response['SecurityGroups'][0]['Tags']
        for i in tagInfo:
            if(i['Key'] == 'approved_by' and i['Value'] == 'wba-cso'):
                tagKey = i['Key']
                tagValue = i['Value']
        
    
    
    
    try:
        if(eventName == 'AuthorizeSecurityGroupIngress' and ingressIp == '0.0.0.0/0'):
            if(tagKey == 'approved_by' and tagValue == 'wba-cso'):
                #do nothing
            else:
                send_sg_mail(userName, ingressIp, sgGroupId)
                #change_ingress_ip(sgGroupId)
                
            
        
    except client.exceptions.ClientError as e:
        print("Error Occured")
        
    
        
def change_ingress_ip(sgId):
    
    ec2client = boto3.client('ec2')
    
    data = ec2client.authorize_security_group_ingress(
        GroupId=sgId,
        IpPermissions=[
            {'IpProtocol': 'tcp',
             'FromPort': 80,
             'ToPort': 80,
             'IpRanges': [{'CidrIp': '10.0.0.24/32'}]}
        ])



def send_sg_mail(userName, ip, sgId):
    
    sgStr = userName + ' added ' + ip + ' ingress rule to ' + sgId
    
    ses_client = boto3.client('ses')
    ses_client.send_email(
        Source = 'enter source email id',
        Destination = {
            'ToAddresses': ['enter list of recipient email ']
        },
        Message = {
            'Subject': {
                'Data': 'SG Notification',
                'Charset': 'utf-8'
            },
            'Body': {
                'Text': {
                    'Data': sgStr
                }
            }
        }
    )
        
    
