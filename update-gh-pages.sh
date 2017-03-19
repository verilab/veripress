if [ "$TRAVIS_BRANCH" = "master" -a "$TRAVIS_PULL_REQUEST" = "false" ]; then
    npm install git-update-ghpages;
    ./node_modules/.bin/git-update-ghpages -e veripress/demo veripress_demo_instance/_deploy;
    ./node_modules/.bin/git-update-ghpages -e veripress/docs veripress_docs/_deploy;
fi