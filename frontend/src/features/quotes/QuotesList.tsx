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
        <main className="page-enter">
            <header className="mb-8 flex flex-col gap-6 border-b border-line pb-7 sm:mb-10 sm:flex-row sm:items-end sm:justify-between">
                <div>
                    <p className="mb-3 text-xs font-semibold uppercase tracking-[0.18em] text-copper">Pilotage commercial</p>
                    <h1 className="font-display text-5xl font-medium leading-[0.92] text-ink sm:text-6xl">Devis</h1>
                    <p className="mt-4 max-w-xl text-sm leading-6 text-muted">Retrouvez vos propositions et suivez leur avancement.</p>
                </div>
                <nav aria-label="Actions sur les devis" className="flex items-center gap-3">
                    <button
                        type="button"
                        onClick={() => setRefreshKey((key) => key + 1)}
                        disabled={isLoading}
                        className="inline-flex min-h-11 items-center gap-2 rounded-sm border border-line bg-surface px-4 text-sm font-medium text-ink transition-colors hover:border-ink disabled:cursor-wait disabled:opacity-50"
                    >
                        <span aria-hidden="true" className="text-lg leading-none">↻</span>
                        Actualiser
                    </button>
                    <Link to="/quotes/new" className="inline-flex min-h-11 items-center rounded-sm bg-copper px-4 text-sm font-semibold text-white transition-colors hover:bg-copper-dark">
                        Créer un devis <span className="ml-2 text-lg leading-none" aria-hidden="true">+</span>
                    </Link>
                </nav>
            </header>

            {isLoading && (
                <output className="flex min-h-40 items-center justify-center gap-3 rounded-sm border border-line bg-surface text-sm text-muted">
                    <span aria-hidden="true" className="size-4 animate-spin rounded-full border-2 border-line border-t-copper" />
                    Chargement des devis…
                </output>
            )}

            {error && (
                <div role="alert" className="flex flex-col gap-4 rounded-sm border border-danger/20 bg-danger-soft p-5 text-sm text-danger sm:flex-row sm:items-center sm:justify-between">
                    <p>{error}</p>
                    <button
                        type="button"
                        onClick={() => setRefreshKey((key) => key + 1)}
                        className="min-h-10 shrink-0 self-start rounded-sm border border-danger/30 px-4 font-semibold transition-colors hover:bg-white/60 sm:self-auto"
                    >
                        Réessayer
                    </button>
                </div>
            )}

            {!isLoading && !error && quotes.length === 0 && (
                <section className="flex min-h-72 flex-col items-center justify-center border border-dashed border-line bg-surface px-6 py-12 text-center">
                    <span aria-hidden="true" className="mb-5 grid size-12 place-items-center rounded-full bg-copper-soft font-display text-3xl italic text-copper">A</span>
                    <h2 className="font-display text-3xl font-medium text-ink">Aucun devis pour le moment</h2>
                    <p className="mt-2 text-sm text-muted">Votre première proposition peut commencer ici.</p>
                    <Link to="/quotes/new" className="mt-6 inline-flex min-h-11 items-center rounded-sm bg-ink px-5 text-sm font-semibold text-surface transition-colors hover:bg-copper">
                        Créer un devis <span className="ml-2 text-lg leading-none" aria-hidden="true">+</span>
                    </Link>
                </section>
            )}

            {!isLoading && !error && quotes.length > 0 && (
                <section className="overflow-hidden rounded-sm border border-line bg-surface">
                    <div className="flex items-center justify-between border-b border-line px-5 py-4 sm:px-6">
                        <div>
                            <h2 className="text-sm font-semibold text-ink">Tous les devis</h2>
                            <p className="mt-1 text-xs text-muted">{quotes.length} {quotes.length === 1 ? "proposition" : "propositions"}</p>
                        </div>
                        <span className="font-mono text-xs text-muted">{String(quotes.length).padStart(2, "0")}</span>
                    </div>
                    <div className="overflow-x-auto">
                        <table className="w-full min-w-[640px] border-collapse text-left">
                            <caption className="sr-only">Liste des devis</caption>
                            <thead className="bg-paper/70 text-[11px] font-semibold uppercase tracking-[0.12em] text-muted">
                                <tr>
                                    <th scope="col" className="px-5 py-3 font-semibold sm:px-6">Identifiant</th>
                                    <th scope="col" className="px-5 py-3 font-semibold">Statut</th>
                                    <th scope="col" className="px-5 py-3 text-right font-semibold">Total HT</th>
                                    <th scope="col" className="px-5 py-3 text-right font-semibold sm:px-6">Détail</th>
                                </tr>
                            </thead>
                            <tbody className="divide-y divide-line">
                                {quotes.map((quote) => {
                                    const statusTone = quote.status === "accepted"
                                        ? "bg-forest-soft text-forest"
                                        : quote.status === "rejected"
                                            ? "bg-danger-soft text-danger"
                                            : "bg-copper-soft text-copper-dark";

                                    return (
                                        <tr key={quote.id} className="group transition-colors hover:bg-paper/50">
                                            <th scope="row" className="px-5 py-4 font-medium sm:px-6">
                                                <code className="font-mono text-xs text-ink">{quote.id}</code>
                                            </th>
                                            <td className="px-5 py-4">
                                                <span className={`inline-flex rounded-full px-2.5 py-1 text-xs font-medium ${statusTone}`}>
                                                    {formatStatus(quote.status)}
                                                </span>
                                            </td>
                                            <td className="px-5 py-4 text-right font-mono text-sm tabular-nums text-ink">{formatCurrency(quote.total_ht)}</td>
                                            <td className="px-5 py-4 text-right sm:px-6">
                                                <Link to={`/quotes/${encodeURIComponent(quote.id)}`} className="text-sm font-semibold text-copper transition-colors hover:text-copper-dark">
                                                    Voir <span aria-hidden="true">↗</span>
                                                </Link>
                                            </td>
                                        </tr>
                                    );
                                })}
                            </tbody>
                        </table>
                    </div>
                </section>
            )}
        </main>
    );
}
