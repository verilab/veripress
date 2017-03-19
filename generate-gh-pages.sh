if [ "$TRAVIS_BRANCH" = "master" -a "$TRAVIS_PULL_REQUEST" = "false" ]; then
    npm install git-update-ghpages;
    ./node_modules/.bin/git-update-ghpages veripress/demo veripress_demo_instance/_deploy;
fi