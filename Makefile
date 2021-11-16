.PHONY: reqs
reqs:
	pip install -r requirements.txt
	pip install -r requirements-dev.txt


.PHONY: upgrade_reqs
upgrade_reqs:
	pip-upgrade requirements.txt
	pip-upgrade requirements-dev.txt


.PHONY: package
package:
	sls package


.PHONY: test
test:
	pytest -v --cov --cov-report=term --cov-report=html


.PHONY: deploy_dev
deploy_dev:
	sls deploy --stage dev


.PHONY: remove_dev
remove_dev:
	sls remove --stage dev


.PHONY: deploy_staging
deploy_staging:
	sls deploy --stage staging


.PHONY: remove_staging
remove_staging:
	sls remove --stage staging


.PHONY: deploy_production
deploy_production:
	sls deploy --stage production


.PHONY: remove_production
remove_production:
	sls remove --stage production


.PHONY: man_test_create_slide_deck
man_test_create_slide_deck:
	./scripts/json_to_gql.py tests/handlers/test_json/create_slide_deck.json | sls invoke -f graphql --stage dev
