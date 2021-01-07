# Nassau Network

## I want to use!

*Princeton's voguish directory*

Nassau Network (https://nassau.network) is the hit new directory for Princeton undergrads. Just sign in with your netid and start searching.

## I want to code!

### Welcome to Traxler!

Thanks for your interest Traxler, the code that powers https://nassau.network. This code base allows you to contribute to Nassau Network and even host your own version of the website if you want to.

To start, clone this repo with the clone button above.

#### Setup
If you have just cloned the repo or pulled a new version that requires new python packages, run:
```bash
setup --full
```

Otherwise, you must run 
```bash
setup
```
when you want to begin working on Traxler to set up your environment. This version (without `--full`) skips the package installation and should be much faster.

#### Development
We want to make this app super simple to develop and contain as little bloat as possible. To that end, we try to:
1. Make it really easy to make changes.
2. Reduce the number of unnecessary files.
3. No node_modules folder, pls ;)

If you are on bash, start typing: `tx-` and press TAB to see the autocomplete list. You should see a bunch of options that start with `tx-`. These scripts are there to help you code Traxler.

To run the website locally at http://localhost:8000, use the command:
```bash
tx-dev
```
