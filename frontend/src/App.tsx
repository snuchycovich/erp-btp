import { useEffect, useState } from "react";
import { QuoteForm } from "./features/quotes/QuoteForm";
import { QuotesList } from "./features/quotes/QuotesList";

type Page = "quotes" | "create"

function getPageFromHash(): Page {
  return window.location.hash == "#create-quote" ? "create" : "quotes";
}
export default function App() {
  const [page, setPage] = useState<Page>(getPageFromHash);

  useEffect(() => {
    function handleHasChange(): void {
      setPage(getPageFromHash);
    }

    window.addEventListener("hashchange", handleHasChange);
    return () => window.removeEventListener("hashchange", handleHasChange)
  }, [])

  if (page === "create") {
        return (
            <main id="create-quote">
                <nav aria-label="Navigation">
                    <a href="#quotes">Retour à la liste des devis</a>
                </nav>
                <QuoteForm />
            </main>
        );
    }

    return (
        <div id="quotes">
            <QuotesList />
        </div>
    );
}
