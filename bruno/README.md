# PocketBloom Bruno collection

1. Start the API with `make db-up`, `make migrate`, and `make run`.
2. Open this `bruno` directory as a collection in Bruno.
3. Select the `Local` environment.
4. Run `Signup`, then `Login`.
5. Run the category requests in sequence.

Signup stores the returned user ID in memory. Login stores the bearer token in
memory. Create Category stores the returned category ID for update and delete.

The category requests currently include the temporary `user_id` query parameter.
Remove it after the API routes are switched to `get_current_user`.
