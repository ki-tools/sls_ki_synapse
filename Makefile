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


.PHONY: deploy_development
deploy_development:
	sls deploy --stage development


.PHONY: deploy_dev
deploy_dev: deploy_development


.PHONY: remove_development
remove_development:
	sls remove --stage development


.PHONY: remove_dev
remove_dev: remove_development


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


.PHONY: man_test_all
man_test_all:
	JSON=$$(./scripts/json_to_gql.py tests/handlers/test_json/create_syn_project.json name="Manual Test Project `date +%s`" | sls invoke -f graphql --stage development); \
	echo "$$JSON"; \
	ID=$$(echo $$JSON | python -c "import json,sys;obj=json.loads(' '.join(sys.stdin.read().split(')', maxsplit=1)[1:]));print(json.loads(obj['body'])['data']['createSynProject']['synProject']['id']);"); \
	./scripts/json_to_gql.py tests/handlers/test_json/update_syn_project.json id=$$ID name="Manual Test Project UPDATED `date +%s`" | sls invoke -f graphql --stage development; \
	./scripts/json_to_gql.py tests/handlers/test_json/get_syn_project.json id=$$ID | sls invoke -f graphql --stage development; \
	./scripts/json_to_gql.py tests/handlers/test_json/create_slide_deck.json | sls invoke -f graphql --stage development;


.PHONY: man_test_create_syn_project
man_test_create_syn_project:
	./scripts/json_to_gql.py tests/handlers/test_json/create_syn_project.json name="Manual Test Project `date +%s`" | sls invoke -f graphql --stage development


.PHONY: man_test_create_slide_deck
man_test_create_slide_deck:
	./scripts/json_to_gql.py tests/handlers/test_json/create_slide_deck.json | sls invoke -f graphql --stage development



