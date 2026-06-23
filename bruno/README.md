# PocketBloom Bruno collection

1. Start the API with `make db-up`, `make migrate`, and `make run`.
2. Open this `bruno` directory as a collection in Bruno.
3. Select the `Local` environment.
4. Run `Signup`, then `Login`.
5. Run the category requests in sequence.
6. Run `Create Budget`, then the remaining budget requests in sequence.

Login stores the bearer token in memory. Create Category stores the returned
category ID for later requests. Create Budget stores the returned budget ID
for get, update, patch, and delete requests.
