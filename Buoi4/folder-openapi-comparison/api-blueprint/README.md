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
