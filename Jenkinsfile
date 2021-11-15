MASTER = "master"

pipeline {
    agent any

    environment {
        AWS_ACCESS_KEY_ID     = credentials('jenkins-aws-secret-key-id')
        AWS_SECRET_ACCESS_KEY = credentials('jenkins-aws-secret-access-key')
        ECR_NAME              = "751307794059.dkr.ecr.eu-west-3.amazonaws.com"
        REPO_NAME             = "star-app"
    }

    stages {

        stage('git') {
            steps {
                script {
                    sh """
                        echo $env.BRANCH_NAME
                        echo "Switching to 'origin/master' branch."
                        git checkout -b main origin/master
                    """
                    if(env.BRANCH_NAME.equals(MASTER)) {
                        echo 'This is master'
                    } else {
                        echo 'This is not master'
                    }
                }
            }
        }

        stage('build') {
            steps {
                script {
                    sh """
                        docker build -t $ECR_NAME/$REPO_NAME .
                    """
                }
            }
        }

        stage('test') {
            steps {
                script {
                        sh """
                            docker container rm -f app
                            mkdir /var/jenkins_home/testing_files/ || true
                            cp -a nginx /var/jenkins_home/testing_files/
                            sed -i "s%./nginx/static%/home/julian/jenkins_files/nginx/static/%" docker-compose.yml
                            sed -i "s%./nginx/nginx.conf%/home/julian/jenkins_files/nginx/nginx.conf%" docker-compose.yml
                            docker-compose -p jenkins up -d --build
                            sleep 15
                        """
                        final String url = 'http://nginx:80/star'
                        final String response = sh(script: "curl -s -o /dev/null -w '%{http_code}' $url", returnStdout: true).trim()
                        echo response
                        if(!response.equals("200")) {                      
                            error "Tests failed"
                        }
                        sh '''
                            docker-compose -p jenkins down || true
                        '''
                }
            }
        }

        stage('publish') {
            steps {
                script {
                    sh """
                        aws configure set aws_access_key_id $AWS_ACCESS_KEY_ID
                        aws configure set aws_secret_access_key $AWS_SECRET_ACCESS_KEY
                        aws ecr get-login-password --region eu-west-3 | docker login --username AWS --password-stdin $ECR_NAME
                        docker push $ECR_NAME/$REPO_NAME
                    """
                }
            }
        }

    }

    post {

        always {
            sh '''
                docker-compose -p jenkins down
            '''
        }

    }
}