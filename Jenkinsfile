pipeline {
    agent any

    environment {
        AWS_ACCESS_KEY_ID     = credentials('jenkins-aws-secret-key-id')
        AWS_SECRET_ACCESS_KEY = credentials('jenkins-aws-secret-access-key')
        REPO_NAME             = "751307794059.dkr.ecr.eu-west-3.amazonaws.com/star"
    }

    stages {

        stage('git') {
            steps {
                script {
                    sh """
                        echo "Switching to 'origin/master' branch."
                        git checkout -b main origin/master
                    """
                }
            }
        }

        stage('build') {
            steps {
                script {
                    sh '''
                        docker build -t $REPO_NAME .
                    '''
                }
            }
        }

        stage('test') {
            steps {
                script {
                    
                        //docker run -p 5000:5000 --network=jenkins_star --name app -t -d $REPO_NAME
                        sh """
                            docker container rm -f app
                            cp -a nginx /var/jenkins_home/testing_files/
                            sed -i "s%./nginx/static%/home/julian/jenkins_files/nginx/static/%" docker-compose.yml
                            sed -i "s%./nginx/nginx.conf%/home/julian/jenkins_files/nginx/nginx.conf%" docker-compose.yml
                            docker-compose up --build
                            sleep 5
                        """
                        if(false == true) {
                            final String url = 'http://app:5000'
                            final String response = sh(script: "curl -s -o /dev/null -w '%{http_code}' $url", returnStdout: true).trim()
                            echo response
                            if(!response.equals("200")) {                      
                                error "Tests failed"
                            }
                        }
                }
            }
        }

        stage('publish') {
            steps {
                script {
                    sh '''
                        aws configure set aws_access_key_id $AWS_ACCESS_KEY_ID
                        aws configure set aws_secret_access_key $AWS_SECRET_ACCESS_KEY
                        aws ecr get-login-password --region eu-west-3 | docker login --username AWS --password-stdin 751307794059.dkr.ecr.eu-west-3.amazonaws.com
                        docker push $REPO_NAME
                    '''
                }
            }
        }

    }  
}