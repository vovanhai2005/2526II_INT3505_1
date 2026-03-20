import "@typespec/http";
import "@typespec/openapi";
import "@typespec/openapi3";
using TypeSpec.Http;
using TypeSpec.OpenAPI;

@service(#{
  title: "Book Management API"
})
@info(#{
  version: "1.0.0"
})
@doc("A simple API to manage a collection of books, for SOA courses demo.")
@server("http://127.0.0.1:5000", "Development server")
namespace BookApi;

model Book {
  @doc("The unique identifier of the book.")
  id: int32;
  @doc("The title of the book.")
  title: string;
  @doc("The author of the book.")
  author: string;
}

model NewBook {
  @doc("The title of the book.")
  title: string;
  @doc("The author of the book.")
  author: string;
}

@route("/api/books")
interface Books {
  @get
  @summary("Get all books")
  list(): Book[];

  @post
  @summary("Add a new book")
  create(@body book: NewBook): { @statusCode _: 201; @body body: Book } | { @statusCode _: 400; @body error: string };
}

@route("/api/books/{book_id}")
interface SingleBook {
  @get
  @summary("Get a book by its ID")
  read(@path book_id: int32): Book | { @statusCode _: 404; @body error: string };

  @put
  @summary("Update an existing book")
  update(@path book_id: int32, @body book: NewBook): Book | { @statusCode _: 400; @body error: string } | { @statusCode _: 404; @body error: string };

  @delete
  @summary("Delete a book")
  delete(@path book_id: int32): { @statusCode _: 204 } | { @statusCode _: 404; @body error: string };
}