
# Welcome to AWS Wickr Infrastructure - CDK Python project 


This is AWS CDK Python to deploy AWS Wickr on EC2 in a secure and highly available environment

The `cdk.json` file tells the CDK Toolkit how to execute your app.

This project is set up like a standard Python project.  The initialization
process also creates a virtualenv within this project, stored under the `.venv`
directory.  To create the virtualenv it assumes that there is a `python3`
(or `python` for Windows) executable in your path with access to the `venv`
package. If for any reason the automatic creation of the virtualenv fails,
you can create the virtualenv manually.

To manually create a virtualenv on MacOS and Linux:

```
$ python3 -m venv .venv
```

After the init process completes and the virtualenv is created, you can use the following
step to activate your virtualenv.

```
$ source .venv/bin/activate
```

If you are a Windows platform, you would activate the virtualenv like this:

```
% .venv\Scripts\activate.bat
```

Once the virtualenv is activated, you can install the required dependencies.

```
$ pip install -r requirements.txt
```


Now setup the boostrap of CDK if you are using CDK for first time in a region or account

```
$ cdk boostrap
```


At this point you can now synthesize the CloudFormation template for this code.

```
$ cdk synth
```

Now use the below command for the deployment (Note: Replace IP with your public ip for SSH and keyPair of your own)
```
$ cdk deploy --parameters sshIp=43.225.20.162/32 --parameters keyPair="vamsi-chunduru"
```

To add additional dependencies, for example other CDK libraries, just add
them to your `setup.py` file and rerun the `pip install -r requirements.txt`
command.


## Cleanup
Run (Note: Replace IP with your public ip for SSH and keyPair of your own)
```
$ cdk destroy --parameters sshIp=49.204.105.46/32 --parameters keyPair="vamsi-chunduru"

```

## Useful commands

 * `cdk ls`          list all stacks in the app
 * `cdk synth`       emits the synthesized CloudFormation template
 * `cdk deploy`      deploy this stack to your default AWS account/region
 * `cdk diff`        compare deployed stack with current state
 * `cdk docs`        open CDK documentation
 * 
 

Ref: https://github.com/aws-samples/wickr-enterprise-amazon-ec2-cdk

Enjoy!
