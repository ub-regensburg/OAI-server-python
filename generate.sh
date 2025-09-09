openapi-generator-cli generate -g python -o oai_pmh -i oai-pmh.openapi.json -c ./oai_pmh/generator-config.json --global-property withXml
rm -rf ./oai_pmh/generated/models
mv -f ./oai_pmh/oai_pmh/generated/models ./oai_pmh/generated/models
rm -rf ./oai_pmh/oai_pmh