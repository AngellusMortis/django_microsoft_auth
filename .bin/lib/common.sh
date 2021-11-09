#!/bin/bash

function setRoot() {
    ROOT_PATH=$PWD
    while [[ $ROOT_PATH != / ]]; do
        output=$(find "$ROOT_PATH" -maxdepth 1 -mindepth 1 -name "pyproject.toml")
        if [[ -n $output ]]; then
            break
        fi
        # Note: if you want to ignore symlinks, use "$(realpath -s "$path"/..)"
        ROOT_PATH="$(readlink -f "$ROOT_PATH"/..)"
    done

    if [[ $ROOT_PATH == / ]]; then
        ROOT_PATH=$( realpath $( dirname "${BASH_SOURCE[0]}" )/../../ )
        echo "Could not find \`pyproject.toml\`, following back to $( basename $ROOT_PATH )"
    else
        echo "Using project $( basename $ROOT_PATH )"
    fi
}

function setLintModules() {
    setRoot

    BANDIT_MODULES=""
    PYLINT_MODULES=""

    if [[ -f "$ROOT_PATH/conftest.py" ]]; then
        echo "Found \`conftest.py\`"
        BANDIT_MODULES="conftest"
        PYLINT_MODULES="conftest.py"
    fi

    if [[ -d "$ROOT_PATH/tests" ]]; then
        echo "Found \`tests\`"
        PYLINT_MODULES="$PYLINT_MODULES tests"
    fi

    MODULE_NAME=$( cat "$ROOT_PATH/pyproject.toml" | grep -e "^name =" | sed 's/name = "\(.*\)"/\1/' )
    echo "Found module \`$MODULE_NAME\`"

    BANDIT_MODULES=$( echo "$BANDIT_MODULES $MODULE_NAME" | xargs )
    PYLINT_MODULES=$( echo "$PYLINT_MODULES $MODULE_NAME" | xargs )
}
