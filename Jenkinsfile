pipeline {
  agent {
    docker {
      image 'python:3.7-buster'
    }
  }
  stages {
    stage('Testing') {
      steps {
        sh 'pip install tox'
        sh 'tox'
      }
    }
  }
}
