from ddgs import DDGS


def web_search(query: str, max_results: int = 5):
    try:
        results = []

        print("SEARCHING WEB FOR:", query)

        with DDGS() as ddgs:

            search_results = ddgs.text(
                query,
                max_results=max_results
            )

            for result in search_results:

                title = result.get(
                    "title",
                    ""
                )

                url = result.get(
                    "href",
                    ""
                )

                description = result.get(
                    "body",
                    ""
                )

                if title and url:

                    results.append({
                        "title": title,
                        "url": url,
                        "description": description
                    })

        print(
            "WEB RESULTS FOUND:",
            len(results)
        )

        return results

    except Exception as error:

        print(
            "WEB SEARCH ERROR:",
            error
        )

        return []