pipeline {
    agent any
    
    environment{
        DOCKERHUB_CREDENTIALS = credentials('dockerhub-token')
    }
    
    stages {
        
        stage('Build') {
            steps {
                echo 'Building..'
            }
        }
        stage('Login') {
            steps {
                sh '#!/bin/sh'
                sh 'ENTRYPOINT ["sh", "durable-9d64bc00/script.sh"]'
                sh 'echo $DOCKERHUB_CREDENTIALS_PSW | docker login -u $DOCKERHUB_CREDENTIALS_USR --password-stdin'
            }
        }
        
        stage('Test') {
            steps {
                echo 'Testing..'
            }
        }
        
        stage('Push') {
            steps {
                sh 'docker push hankystyle/demo-jenkins:lastest'
            }
        }
        
        
        stage('Deploy') {
            steps {
                echo 'Deploying....'
            }
        }
    }
    post{
        always{
            sh 'docker logout'
         }
    }
}
