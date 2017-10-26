# Python 3.6
## AWS CloudFormation: Looking up Amazon Machine Image IDs

## Instructions
- Clone this repository.
- When committing code to **any** branch, `./.gitlab-ci.yml` will automatically package and upload to S3.
- `./data/config.json` is **REQUIRED** to be updated and has to match the Parameter WindowsVersion value i.e. *cwFrontEnd* from the AWS CloudFormation Template.
- AWS Walkthrough: Looking Up Amazon Machine Image IDs:
  - https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/walkthrough-custom-resources-lambda-lookup-amiids.html


## Structure Overview
- Folders
  - `./vscode/`: vscode, project workspace settings.
  - `./lib`: contains the project's main code.
  - `./data`: contains data files.
  - `./scripts`: debug scripts.
- Files
  - `config.json`: data file.
  - `./lib/ami_lookup.py`: main project code.
  - `./handler.py`: lambda handler that calls ami_lookup.py.

## The Request
When CloudFormation invokes a custom resource it sends a request. The **ResponseURL** is what will be used to return the data back to AWS CloudFormation:

```
{
  "RequestType": "Create",
  "ServiceToken": "arn:aws:lambda:...:function:AMIInfoFunction...",
  "ResponseURL": "https://cloudformation-custom-resource...",
  "StackId": "arn:aws:cloudformation:us-east-1:...",
  "RequestId": "afd8d7c5-9376-4013-8b3b-307517b8719e...",
  "LogicalResourceId": "AMIInfo",
  "ResourceType": "AWS::CloudFormation::CustomResource",
  "ResourceProperties": {
    "ServiceToken": "arn:aws:lambda:...:function:AMIInfoFunction...",
    "Region": "us-east-1",
    "OSName": "cwFrontEnd"
  }
}
```

## The Response
To send the response back to AWS CloudFormation we PUT some JSON body to the `ResponseURL` provided in the request. The response looks like this:

```
{
  "StackId": "arn:aws:cloudformation:us-east-1:...",
  "RequestId": 'e4d1ab88-1b2c-402f-b083-1966f5806064',
  "LogicalResourceId": 'AMIInfo',
  "PhysicalResourceId": '2015/05/28/00395b017f72444791fb12b988f4aeab',
  "Status": 'SUCCESS',
  "Reason": ' Details in CloudWatch Log: 2015/05/28/...',
  "Data":  {
    "Id": 'ami-43795473'
  }
}
```

## Using the Parameters / Properties in CloudFormation

### Parameters
- The *cwFrontEnd* is **REQUIRED** to be updated to match `./data/config.json` 

```
{
  "Parameters": {
    "WindowsVersion": {
        "Description": "Windows Version.",
        "Type": "String",
        "Default": "cwFrontEnd",
        "AllowedValues": [
            "cwFrontEnd"
        ],
        "ConstraintDescription": "Must be a valid Windows version."
    },
    "ModuleName": {
        "Description": "The name of the Python file",
        "Type": "String",
        "Default": "handler"
    },
    "S3Bucket": {
        "Description": "The name of the bucket that contains your packaged source.",
        "Type": "String",
        "Default": "test-cloudformation-template"
    },
    "S3Key": {
        "Description": "The name of the ZIP package",
        "Type": "String",
        "Default": "ami_lookup.zip"
    }
}
```

### EC2Instance - AWS::EC2::Instance
The ImageId property is using the *Fn::GetAtt* method to get the Id from the **AMIInfo** CustomResource.

```
"EC2Instance": {
  "Type": "AWS::EC2::Instance",
  "Properties": {
    "IamInstanceProfile": {
      "Ref": "IAMRole"
    },
    "AvailabilityZone": "us-east-1d",
    "NetworkInterfaces": [
      {
        "AssociatePublicIpAddress": "true",
        "DeviceIndex": "0",
        "SubnetId": {
          "Ref": "EC2Subnet"
        },
        "GroupSet": {
          "Ref": "EC2SecurityGroup"
        }
      }
    ],
    "ImageId": {
      "Fn::GetAtt": [
        "AMIInfo",
        "Id"
      ]
    }
  }
}
```

### AMIInfo - AWS::CloudFormation::CustomResource
The following CustomResource references the Lambda resource, Region, and WindowsVersion  which are passed in as a parameter.

```
"AMIInfo": {
  "Type": "AWS::CloudFormation::CustomResource",
  "Properties": {
    "ServiceToken": {
      "Fn::GetAtt": [
        "AMIInfoFunction",
        "Arn"
      ]
    },
    "Region": {
      "Ref": "AWS::Region"
    },
    "OSName": {
      "Ref": "WindowsVersion"
    }
  }
}
```

### AMIInfoFunction - AWS::Lambda::Function
* `S3Bucket` bucket location for the packaged Python Code. 
* `S3Key` name of the packaged Python Code. 
* `ModuleName` name of the Python file *handler.py*.
* `.lambda_handler` name of the function *lambda_handler*.
* `Role` Lambda permissions to DescribeImages.

```
"AMIInfoFunction": {
  "Type": "AWS::Lambda::Function",
  "Properties": {
    "Code": {
      "S3Bucket": {
        "Ref": "S3Bucket"
      },
      "S3Key": {
        "Ref": "S3Key"
      }
    },
    "Handler": {
      "Fn::Join": [
        "",
        [
          {
            "Ref": "ModuleName"
          },
          ".lambda_handler"
        ]
      ]
    },
    "Role": {
      "Fn::GetAtt": [
        "LambdaExecutionRole",
        "Arn"
      ]
    },
    "Runtime": "python3.6",
    "Timeout": "30"
  }
}
```

### LambdaExecutionRole - AWS::IAM::Role
The following is an IAM Role that the Lambda resource references to POST Logs and DescribeImages.

```
"LambdaExecutionRole": {
  "Type": "AWS::IAM::Role",
  "Properties": {
    "AssumeRolePolicyDocument": {
      "Version": "2012-10-17",
      "Statement": [
        {
          "Effect": "Allow",
          "Principal": {
            "Service": [
              "lambda.amazonaws.com"
            ]
          },
          "Action": [
            "sts:AssumeRole"
          ]
        }
      ]
    },
    "Path": "/",
    "Policies": [
      {
        "PolicyName": "root",
        "PolicyDocument": {
          "Version": "2012-10-17",
          "Statement": [
            {
              "Effect": "Allow",
              "Action": [
                "logs:CreateLogGroup",
                "logs:CreateLogStream",
                "logs:PutLogEvents"
              ],
              "Resource": "arn:aws:logs:*:*:*"
            },
            {
              "Effect": "Allow",
              "Action": [
                "ec2:DescribeImages"
              ],
              "Resource": "*"
            }
          ]
        }
      }
    ]
  }
}
```