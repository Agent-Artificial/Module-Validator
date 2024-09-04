#!/bin/bash

module_name=$1
if [ -z "$module_name" ]; then
    module_name=sylliba
fi

cp .sylliba.env module_validator/subnet_modules/sylliba.env

module_path=module_validator/subnet_modules/$module_name
sed -i 's/class TranslationRequest(Translate):/class TranslationRequest(Translation):/g' "${PWD}/module_validator/modules/translation/translation.py"
cd "$module_path" || exit 1
source .env
echo $(printenv)
exit 1
bash launch.sh

