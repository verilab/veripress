if [ "$TRAVIS_BRANCH" = "master" -a "$TRAVIS_PULL_REQUEST" = "false" ]; then
    npm install git-update-ghpages;
    ./node_modules/.bin/git-update-ghpages -e veripress/demo veripress_demo/_deploy;
    ./node_modules/.bin/git-update-ghpages -e veripress/docs veripress_docs/_deploy;
fi

if [ "$TRAVIS_PULL_REQUEST" = "false" ]; then
    if [[ $TRAVIS_BRANCH =~ ^v[0-9.]+$ ]]; then docker tag $DOCKER_REPO:$TAG $DOCKER_REPO:latest; fi
    docker login -e $DOCKER_EMAIL -u $DOCKER_USER -p $DOCKER_PASS
    docker push $DOCKER_REPO
fi
