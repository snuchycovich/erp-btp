import { useEffect, useState } from "react"
import type { QuoteDetailResponse } from "./types"
import { getQuoteById } from "../../api/quotes";
import { formatCurrency, formatDate, formatStatus } from "./formatters";
import { Link } from "react-router-dom";

type QuoteDetailProps = {
    quoteId: string
}

export function QuoteDetail({ quoteId }: QuoteDetailProps) {
    const [quote, setQuote] = useState<QuoteDetailResponse | null>(null);
    const [isLoading, setIsLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    const [retryKey, setRetryKey] = useState(0);

    useEffect(() => {
        let isCurrent = true;

        async function loadQuote(): Promise<void> {
            setIsLoading(true);
            setError(null);
            setQuote(null);

            try {
                const result = await getQuoteById(quoteId);
                if (isCurrent) {
                    setQuote(result);
                }
            } catch(caughtError: unknown) {
                if (isCurrent) {
                    setError(
                        caughtError instanceof Error
                        ? caughtError.message
                        : "An unexpected error has occurred."
                    );
                }
            } finally {
                if (isCurrent) {
                    setIsLoading(false);
                }
            }
        }

        void loadQuote();

        return () => {
            isCurrent = false;
        };
    }, [quoteId, retryKey])

    return (
        <main>
            <nav aria-label="Navigation du devis">
                <Link to="/quotes">Retour à la liste</Link>
            </nav>

            <h1>Détail du devis</h1>

            {isLoading && <output>Chargement du devis…</output>}

            {error && (
                <p role="alert">
                    {error}{" "}
                    <button
                        type="button"
                        onClick={() => setRetryKey((key) => key + 1)}
                    >
                        Réessayer
                    </button>
                </p>
            )}

            {quote && (
                <>
                    <p>
                        <Link to={`/quotes/${encodeURIComponent(quote.id)}/edit`}>
                            Modifier le devis
                        </Link>
                    </p>
                    <dl>
                        <dt>Identifiant</dt>
                        <dd>
                            <code>{quote.id}</code>
                        </dd>

                        <dt>Créé le</dt>
                        <dd>{formatDate(quote.created_at)}</dd>
                    </dl>

                    <h2>Historique des révisions</h2>

                    {quote.revisions.map((revision) => (
                        <section key={revision.version}>
                            <h3>Révision {revision.version}</h3>

                            <dl>
                                <dt>Statut</dt>
                                <dd>{formatStatus(revision.status)}</dd>

                                <dt>Date</dt>
                                <dd>{formatDate (revision.created_at)}</dd>

                                <dt>Total HT</dt>
                                <dd>
                                    {formatCurrency(revision.total_ht)}
                                </dd>
                            </dl>

                             <table>
                                <caption>
                                    Articles de la révision {revision.version}
                                </caption>
                                <thead>
                                    <tr>
                                        <th scope="col">Description</th>
                                        <th scope="col">Quantité</th>
                                        <th scope="col">Prix unitaire</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {revision.items.map((item, index) => (
                                        <tr
                                            key={`${revision.version}-${index}`}
                                        >
                                            <th scope="row">
                                                {item.description}
                                            </th>
                                            <td>{item.quantity}</td>
                                            <td>
                                                {formatCurrency(item.unit_price)}
                                            </td>
                                        </tr>
                                    ))}
                                </tbody>
                            </table>
                        </section>
                    ))}
                </>
            )}
        </main>
    );
}
