import { useEffect, useState } from "react";
import type { QuoteSummary } from "./types";
import { listQuotes } from "../../api/quotes";
import { formatCurrency, formatStatus } from "./formatters";
import { Link } from "react-router-dom";

export function QuotesList() {
    const [quotes, setQuotes] = useState<QuoteSummary[]>([])
    const [isLoading, setIsLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    const [refreshKey, setRefreshKey] = useState(0)

    useEffect(() => {
        let isCurrent = true;

        async function loadQuotes(): Promise<void> {
            setIsLoading(true);
            setError(null);

            try {
                const result = await listQuotes();
                if (isCurrent) {
                    setQuotes(result)
                }
            } catch (caughtError: unknown) {
                if (isCurrent) {
                    setError(
                        caughtError instanceof Error
                        ? caughtError.message
                        : "An unexpected error has occurred."
                    )
                }

            } finally {
                if (isCurrent) {
                    setIsLoading(false);
                }
            }
        }
        void loadQuotes();

        return () => {
            isCurrent = false;
        };
    }, [refreshKey]);

    return (
        <main>
            <header>
                <h1>Devis</h1>
                <nav aria-label="Actions sur les devis">
                    <Link to="/quotes/new">Créer un devis</Link>
                    <button
                        type="button"
                        onClick={() => setRefreshKey((key) => key + 1)}
                        disabled={isLoading}
                    >
                        Actualiser
                    </button>
                </nav>
            </header>

            {isLoading && <output>Chargement des devis…</output>}

            {error && (
                <p role="alert">
                    {error}{" "}
                    <button
                        type="button"
                        onClick={() => setRefreshKey((key) => key + 1)}
                    >
                        Réessayer
                    </button>
                </p>
            )}

            {!isLoading && !error && quotes.length === 0 && (
                <p>Aucun devis pour le moment.</p>
            )}

            {!isLoading && !error && quotes.length > 0 && (
                <div>
                    <table>
                        <caption>Liste des devis</caption>
                        <thead>
                            <tr>
                                <th scope="col">Identifiant</th>
                                <th scope="col">Statut</th>
                                <th scope="col">Total HT</th>
                                <th>Détail</th>
                            </tr>
                        </thead>
                        <tbody>
                            {quotes.map((quote) => (
                                <tr key={quote.id}>
                                    <th scope="row">
                                        <code>{quote.id}</code>
                                    </th>
                                    <td>{formatStatus(quote.status)}</td>
                                    <td>{formatCurrency(quote.total_ht)}</td>
                                    <td>
                                        <Link to={`/quotes/${encodeURIComponent(quote.id)}`}>
                                            Voir le devis
                                        </Link>
                                    </td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </div>
            )}
        </main>
    );
}
