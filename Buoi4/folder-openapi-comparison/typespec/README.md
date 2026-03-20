# TypeSpec

## Prerequisites
- [Node.js and npm](https://nodejs.org/) installed on your machine.

## Installation

TypeSpec compiles into standard formats (like OpenAPI) before rendering. First, make sure you have the required TypeSpec dependencies installed locally.

Inside this specific `typespec` directory, run:

```bash
# Initialize a package.json if not present
npm init -y 

# Install the compiler and standard HTTP/OpenAPI libraries
npm install @typespec/compiler @typespec/http @typespec/openapi @typespec/openapi3
```

## Compilation

After installing the compiler, generate the OpenAPI YAML file from your `.tsp` file:

```bash
npx tsp compile main.tsp
```

This generates an OpenAPI 3.0 specification inside a new folder structure: `tsp-output/@typespec/openapi3/openapi.yaml`.

## Rendering on Localhost

Now that you have the compiled OpenAPI YAML file, you can view it on your localhost server using the `redocly` previewer:

```bash
npx @redocly/cli preview-docs tsp-output/@typespec/openapi3/openapi.yaml
```

This spins up a local server. Open the displayed URL (like `http://127.0.0.1:8080`) in your web browser to browse your API's documentation!
