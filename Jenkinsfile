pipeline {
    agent any

    options {
        gitLabConnection('Gitlab')
    }

    triggers {
        gitlab(triggerOnPush: true, triggerOnMergeRequest: true, branchFilterType: 'All')
    }

    environment {
        AWS_ACCESS_KEY_ID     = credentials('jenkins-aws-secret-key-id')
        AWS_SECRET_ACCESS_KEY = credentials('jenkins-aws-secret-access-key')
        REPO_NAME = "751307794059.dkr.ecr.eu-west-3.amazonaws.com/star"
    }

    stages {

        stage('git') {
            script {

            }
        }

        stage('build') {
            sh '''
                docker build -t $REPO_NAME .
            '''
        }

        stage('test') {
            sh '''
                docker run -p 5000:5000 --network=jenkins_star --name app -t -d $REPO_NAME
                sleep 5
            '''
            script {
                final String url = 'http://app:80'
                final String response = sh(script: "curl -s -o /dev/null -w '%{http_code}' $url", returnStdout: true).trim()
                echo response
                if(!response.equals("200")) {                      
                    error "Tests failed"
                }
            }
        }

        stage('publish') {
            sh '''
                docker build -t $REPO_NAME .
            '''
        }

    }  
}