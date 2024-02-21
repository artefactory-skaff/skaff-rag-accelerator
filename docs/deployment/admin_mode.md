Once you start deploying to a cloud, you may end up having to publicly expose your backend and frontend to the internet. In this case you will need to disable the admin mode on the deployed components.

Just deploy with the `ADMIN_MODE` env var as disabled. This could be in your Dockerfile, or any other deployment config.
```shell
ADMIN_MODE=0
```

This will disable the signup endpoint, preventing people stumbling upon the API from creating an account and using your LLM tokens.
