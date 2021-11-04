1. Set the site domain to a docker address in: http://127.0.0.1:9000/site-settings. 

On MacOS this will be `host.docker.internal:8000` on Linux `172.17.0.1:8000`

2. Restart Saleor to refresh that value (it's cached)

```
docker-compose restart api
```

3. Create an entry for the local Saleor in Saleor-Algolia

```
docker-compose run --rm --no-deps saleor_algolia saleor-algolia add-domain host.docker.internal:8000
```

4. Install the Saleor-Algolia app by going to: http://127.0.0.1:9000/apps/install?manifestUrl=http://host.docker.internal:8082/configuration/manifest

5. Navigate to Saleor Algolia settings http://127.0.0.1:9000/apps/

6. Fill out the form to configure your instance

Algolia Application ID and Admin or Write API Key from https://www.algolia.com/account/api-keys/all

Transformation service URL: `http://host_docker.internal:8083`
Transformation service API Key: `test`

Language: `EN` 

Webhook types accordingly

![](algolia_setup.png)

