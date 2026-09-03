# 10-Minute Code Walkthrough

Use this only as a study checklist. Explain the code in your own words.

1. `app.py` loads settings and asks the app factory to create Flask.
2. `app_factory.py` wires repositories, provider, and service together.
3. `routes.py` exposes the two POST endpoints and maps expected failures to HTTP codes.
4. `PromptService` owns validation and orchestration.
5. `_load_template()` reads the MongoDB prompt and confirms `{{userInput}}` exists.
6. `_render()` performs the assignment's required placeholder substitution.
7. `_process_one()` calls the configured AI provider and stores the request/response pair.
8. `generate_many()` creates one coroutine per input and uses `asyncio.gather()`.
9. `MongoHistoryRepository` inserts one history record per AI call.
10. Tests inject fakes so correctness can be checked without MongoDB/OpenAI.

Questions you should be able to answer before using this design in an assessment:

- Why is `asyncio.to_thread()` used around PyMongo calls?
- What happens if one call in `asyncio.gather()` raises an exception?
- Why does `gather()` still preserve result order?
- Why does each batch item have an `item_index`?
- What would you change if prompts were selected dynamically by domain?
- What HTTP status should an upstream AI failure return, and why?
