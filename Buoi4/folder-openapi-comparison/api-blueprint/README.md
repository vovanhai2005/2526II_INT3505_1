# API Blueprint

## Prerequisites
- [Node.js and npm](https://nodejs.org/) installed on your machine.

## Installation

We will use `aglio`, a very popular API Blueprint renderer, which includes a built-in live-reloading development server.

Install `aglio` globally using npm:

```bash
npm install -g aglio
```

## Rendering on Localhost

Run the following command in this directory to start the `aglio` local server:

```bash
aglio -i api.apib --server
```

This will parse your API Blueprint structure and host it. Open your browser and navigate to the address shown in the terminal (usually `http://127.0.0.1:3000`) to view the complete rendered documentation.

## Code Generation (Server Stubs & Client SDKs)

Since API Blueprint is heavily focused on documentation, we first convert it into an OpenAPI (Swagger) format before generating functional server or client code.

1. **Convert API Blueprint to Swagger/OpenAPI:**
   We use the `apib2swagger` utility to convert the `.apib` markdown file into a standard `swagger.yaml` document.
   ```bash
   npx apib2swagger -i api.apib -o swagger.yaml --yaml
   ```

2. **Generate Python Flask Server Code:**
   Use the OpenAPI Generator CLI to build the actual application code from the generated Swagger file. The code will be exported out to the `generated-server/` directory.
   ```bash
   npx @openapitools/openapi-generator-cli generate -i swagger.yaml -g python-flask -o ./generated-server
   ```
