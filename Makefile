.PHONY: reqs
reqs:
	pip install -r requirements.txt
	pip install -r requirements-dev.txt


.PHONY: test
test:
	pytest -v --cov --cov-report=term --cov-report=html


.PHONY: deploy_dev
deploy_dev:
	sls deploy --stage dev


.PHONY: deploy_staging
deploy_staging:
	sls deploy --stage staging


.PHONY: deploy_production
deploy_production:
	sls deploy --stage production
