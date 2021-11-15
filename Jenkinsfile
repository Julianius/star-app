MASTER = "master"
RELEASE = "release"
PUSHED_BRANCH_NAME = ''
PUSHED_BRANCH_NUM = ''

def getPushedBranchName (String pushed_branch) {
    if(pushed_branch.contains('master'))
        return 'master'
    else if(pushed_branch.contains('release'))
        return 'release'
    return 'feature'
}


def getPushedBranchNum = { String branchName -> branchName.substring(8) }

pipeline {
    agent any

    environment {
        AWS_ACCESS_KEY_ID     = credentials('jenkins-aws-secret-key-id')
        AWS_SECRET_ACCESS_KEY = credentials('jenkins-aws-secret-access-key')
        ECR_NAME              = "751307794059.dkr.ecr.eu-west-3.amazonaws.com"
        REPO_NAME             = "star-app"
    }

    stages {

        stage('clone') {
            steps {
                script {
                    sh """
                        git checkout -b main origin/master
                    """
                    PUSHED_BRANCH_NAME = getPushedBranchName(env.BRANCH_NAME)
                    if(PUSHED_BRANCH_NAME.equals(RELEASE)) {
                        PUSHED_BRANCH_NUM = getPushedBranchNum(env.GIT_BRANCH)
                        sh """
                            echo "Checking out branch 'release/$PUSHED_BRANCH_NUM'."
                            git checkout release/$PUSHED_BRANCH_NUM
                            echo "Getting tags."
                            git fetch --tags 
                        """
                    }
                    /*
                    if(env.BRANCH_NAME.equals(MASTER)) {
                        echo 'This is master'
                    } else if(){
                        echo 'This is not master'
                    }
                    */
                }
            }
        }

        stage('build') {
            steps {
                script {
                    BUILD_STRING = ''
                    if(PUSHED_BRANCH_NAME.equals(RELEASE)) {
                        BUILD_STRING="$ECR_NAME/$REPO_NAME:$PUSHED_BRANCH_NUM"
                    } else {
                        BUILD_STRING="$ECR_NAME/$REPO_NAME"
                    }
                    sh """
                        docker build -t $BUILD_STRING
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
                            sed -i "s%$ECR_NAME/$REPO_NAME%$BUILD_STRING%" docker-compose.yml
                            docker-compose -p jenkins up -d --build
                            sleep 15
                        """
                        final String url = 'http://nginx:80/star'
                        final String response = sh(script: "curl -s -o /dev/null -w '%{http_code}' $url", returnStdout: true).trim()
                        echo response
                        if(!response.equals("200")) {                      
                            error "Tests failed"
                        }
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
                        docker push $BUILD_STRING
                    """
                }
            }
        }

    }

    post {

        always {
            sh '''
                docker-compose -p jenkins down || true
            '''
        }

    }
}