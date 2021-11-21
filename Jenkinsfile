MASTER = "master"
RELEASE = "release"
DEV = "dev"
PUSHED_BRANCH_NAME = ''
PUSHED_BRANCH_NUM = ''
NEXT_TAG = ''

def getPushedBranchName (String pushed_branch) {
    if(pushed_branch.contains('master'))
        return 'master'
    else if(pushed_branch.contains('release'))
        return 'release'
    else if(pushed_branch.contains('dev'))
        return 'dev'
    return 'feature'
}

def getPushedBranchNum = { String branchName -> branchName.substring(8) }

def getNextTag (String version) {
    Integer check_if_tags_exist = sh(returnStatus: true, script: "git describe --tags --abbrev=0 2>/dev/null")
    if(check_if_tags_exist == 0) {
        int last_dig = sh(returnStdout: true, script: "git tag --merged release/$version | cut -d '.' -f3 | sort -n --reverse | head -n 1").split()[0]
        ++last_dig
        return "$version.$last_dig"
    }
    return "$version" + ".0"
}

pipeline {
    agent any

    environment {
        AWS_ACCESS_KEY_ID     = credentials('jenkins-aws-secret-key-id')
        AWS_SECRET_ACCESS_KEY = credentials('jenkins-aws-secret-access-key')
        ECR_NAME              = "751307794059.dkr.ecr.eu-west-3.amazonaws.com"
        REPO_NAME_STAR_APP    = "star-app"
        REPO_NAME_NGINX       = "star-app-nginx"
        GIT_URL               = "git@github.com:Julianius/star-app-gitops.git"
    }

    stages {

        stage('Clone') {
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
                    } else if(PUSHED_BRANCH_NAME.equals(RELEASE)) {
                        sh """
                            git checkout dev
                        """
                    }
                }
            }
        }

        stage('Build') {
            steps {
                script {
                    BUILD_STRING_STAR_APP = ''
                    BUILD_STRING_NGINX = ''
                    NEXT_TAG = getNextTag(PUSHED_BRANCH_NUM)

                    if(PUSHED_BRANCH_NAME.equals(RELEASE)) {
                        BUILD_STRING_STAR_APP = "$ECR_NAME/$REPO_NAME_STAR_APP:$RELEASE-$NEXT_TAG"
                        BUILD_STRING_NGINX    = "$ECR_NAME/$REPO_NAME_NGINX:$RELEASE-$NEXT_TAG"
                    } else if(PUSHED_BRANCH_NAME.equals(DEV)){
                        BUILD_STRING_STAR_APP = "$ECR_NAME/$REPO_NAME_STAR_APP:$DEV"
                        BUILD_STRING_NGINX    = "$ECR_NAME/$REPO_NAME_NGINX:$DEV"
                    } else {
                        BUILD_STRING_STAR_APP = "$ECR_NAME/$REPO_NAME_STAR_APP"
                        BUILD_STRING_NGINX    = "$ECR_NAME/$REPO_NAME_NGINX"
                    }

                    sh """
                        cp -r ./static ./nginx/
                        docker build -t $BUILD_STRING_NGINX ./nginx
                        docker build -t $BUILD_STRING_STAR_APP .
                    """

                }
            }
        }

        stage('E2E Test') {
            steps {
                script {
                        final String url = 'http://nginx:80/star'
                        sh """
                            docker container rm -f app
                            mkdir /var/jenkins_home/testing_files/ || true
                            cp -a nginx /var/jenkins_home/testing_files/
                            sed -i "s%./nginx/static%/home/julian/jenkins_files/nginx/static/%" docker-compose.yml
                            sed -i "s%./nginx/nginx.conf%/home/julian/jenkins_files/nginx/nginx.conf%" docker-compose.yml
                            sed -i "s%$ECR_NAME/$REPO_NAME_NGINX%$BUILD_STRING_NGINX%" docker-compose.yml
                            sed -i "s%$ECR_NAME/$REPO_NAME_STAR_APP%$BUILD_STRING_STAR_APP%" docker-compose.yml
                            docker-compose -p jenkins up -d --build
                        """
                        Integer counter = 5
                        String response = "-1"
                        while(counter > 0) {
                            sh 'sleep 5'
                            response = sh(script: "curl -s -o /dev/null -w '%{http_code}' $url", returnStdout: true).trim()
                            echo response
                            if (response.equals("200")) {
                                break
                            }
                            --counter
                        }
                        if(counter == 0) {
                            error "Tests failed"
                        }
                }
            }
        }

        stage('Publish') {
            steps {
                script {
                    sh """
                        aws configure set aws_access_key_id $AWS_ACCESS_KEY_ID
                        aws configure set aws_secret_access_key $AWS_SECRET_ACCESS_KEY
                        aws ecr get-login-password --region eu-west-3 | docker login --username AWS --password-stdin $ECR_NAME
                        docker push $BUILD_STRING_STAR_APP
                        docker push $BUILD_STRING_NGINX
                    """
                    if(PUSHED_BRANCH_NAME.equals(RELEASE)) {
                        sh """
                            git clean -f
                            git tag $NEXT_TAG -m "New version!"
                            git push origin $NEXT_TAG || true   
                        """
                    }
                }
            }
        }

        stage('Deploy') {
            when {
                expression {
                    return PUSHED_BRANCH_NAME.equals(RELEASE);
                }
            }

            steps {
                script {
                    String sed_params_app = ""
                    String sed_params_nginx = ""
                    String sed_path_app = ""
                    String sed_path_nginx = ""
                    
                    if(PUSHED_BRANCH_NAME.equals(RELEASE)) {
                        sed_params_app = "\"s/release-.*/release-$NEXT_TAG/\""
                        sed_path_app = "./gitops/charts/app/release.values.yaml"
                        sed_params_nginx = "\"s/release-.*/release-$NEXT_TAG/\""
                        sed_path_nginx = "./gitops/charts/nginx/release.values.yaml"
                    } else {

                    }
                    sh """
                        mkdir gitops
                        git clone $GIT_URL ./gitops
                        sed -i $sed_params_app $sed_path_app
                        sed -i $sed_params_nginx $sed_path_nginx
                        git -C "./gitops" add . 
                        git -C "./gitops" commit -m "New app version $NEXT_TAG"
                        git -C "./gitops" push
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