import { useEffect, useState } from "react"
import type { KeyboardEvent } from "react";
import type { QuoteDetailResponse, QuoteRevisionDetail } from "./types"
import { getQuoteById } from "../../api/quotes";
import { formatCurrency, formatDate, formatStatus } from "./formatters";
import { Link } from "react-router-dom";

type QuoteDetailProps = {
    readonly quoteId: string
}

type RevisionCardProps = {
    readonly revision: QuoteRevisionDetail;
}

function RevisionCard({ revision }: RevisionCardProps) {
    let statusTone = "bg-copper-soft text-copper-dark";
    if (revision.status === "accepted") {
        statusTone = "bg-forest-soft text-forest";
    } else if (revision.status === "rejected") {
        statusTone = "bg-danger-soft text-danger";
    }

    return (
        <section className="overflow-hidden rounded-sm border border-line bg-surface">
            <div className="flex flex-col gap-5 border-b border-line p-5 sm:flex-row sm:items-center sm:justify-between sm:px-6">
                <div className="flex items-center gap-3">
                    <span className="grid size-10 shrink-0 place-items-center rounded-sm bg-ink font-mono text-sm text-surface">{String(revision.version).padStart(2, "0")}</span>
                    <div>
                        <h3 className="text-sm font-semibold text-ink">Révision {revision.version}</h3>
                        <p className="mt-1 text-xs tabular-nums text-muted">{formatDate(revision.created_at)}</p>
                    </div>
                </div>
                <div className="flex items-center justify-between gap-4 sm:justify-end sm:gap-8">
                    <span className={`inline-flex rounded-full px-2.5 py-1 text-xs font-medium ${statusTone}`}>
                        {formatStatus(revision.status)}
                    </span>
                    <div className="text-right">
                        <p className="text-[10px] font-semibold uppercase tracking-[0.12em] text-muted">Total HT</p>
                        <p className="mt-1 font-mono text-sm font-medium tabular-nums text-ink">{formatCurrency(revision.total_ht)}</p>
                    </div>
                </div>
            </div>
            <div className="overflow-x-auto">
                <table className="w-full min-w-[520px] border-collapse text-left">
                    <caption className="sr-only">Articles de la révision {revision.version}</caption>
                    <thead className="bg-paper/70 text-[10px] font-semibold uppercase tracking-[0.12em] text-muted">
                        <tr>
                            <th scope="col" className="px-5 py-3 font-semibold sm:px-6">Prestation</th>
                            <th scope="col" className="px-5 py-3 text-right font-semibold">Quantité</th>
                            <th scope="col" className="px-5 py-3 text-right font-semibold sm:px-6">Prix unitaire</th>
                        </tr>
                    </thead>
                    <tbody className="divide-y divide-line">
                        {revision.items.map((item, index) => (
                            <tr key={`${revision.version}-${index}`}>
                                <th scope="row" className="px-5 py-3.5 text-sm font-medium text-ink sm:px-6">{item.description}</th>
                                <td className="px-5 py-3.5 text-right font-mono text-xs tabular-nums text-muted">{item.quantity}</td>
                                <td className="px-5 py-3.5 text-right font-mono text-xs tabular-nums text-ink sm:px-6">{formatCurrency(item.unit_price)}</td>
                            </tr>
                        ))}
                    </tbody>
                </table>
            </div>
        </section>
    );
}

export function QuoteDetail({ quoteId }: QuoteDetailProps) {
    const [quote, setQuote] = useState<QuoteDetailResponse | null>(null);
    const [isLoading, setIsLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    const [retryKey, setRetryKey] = useState(0);
    const [activeTab, setActiveTab] = useState<"current" | "history">("current");

    const currentRevision = quote?.revisions.reduce<QuoteRevisionDetail | null>(
        (latest, revision) => !latest || revision.version > latest.version ? revision : latest,
        null,
    ) ?? null;
    const historicalRevisions = quote && currentRevision
        ? quote.revisions
            .filter((revision) => revision.version < currentRevision.version)
            .sort((left, right) => right.version - left.version)
        : [];

    function handleTabKeyDown(event: KeyboardEvent<HTMLDivElement>): void {
        const tabs = Array.from(
            event.currentTarget.querySelectorAll<HTMLButtonElement>('[role="tab"]'),
        );
        const selectedIndex = tabs.findIndex((tab) => tab.getAttribute("aria-selected") === "true");
        let nextIndex = selectedIndex;

        if (event.key === "ArrowRight") {
            nextIndex = (selectedIndex + 1) % tabs.length;
        } else if (event.key === "ArrowLeft") {
            nextIndex = (selectedIndex - 1 + tabs.length) % tabs.length;
        } else if (event.key === "Home") {
            nextIndex = 0;
        } else if (event.key === "End") {
            nextIndex = tabs.length - 1;
        } else {
            return;
        }

        event.preventDefault();
        const nextTab = tabs[nextIndex];
        if (nextTab) {
            nextTab.focus();
            setActiveTab(nextTab.dataset.tab === "history" ? "history" : "current");
        }
    }

    useEffect(() => {
        let isCurrent = true;

        async function loadQuote(): Promise<void> {
            setIsLoading(true);
            setError(null);
            setQuote(null);
            setActiveTab("current");

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
        <main className="page-enter">
            <nav aria-label="Navigation du devis" className="mb-7">
                <Link to="/quotes" className="inline-flex items-center gap-2 text-sm font-medium text-muted transition-colors hover:text-copper">
                    <span aria-hidden="true">←</span> Retour à la liste
                </Link>
            </nav>

            {isLoading && (
                <output className="flex min-h-40 items-center justify-center gap-3 rounded-sm border border-line bg-surface text-sm text-muted">
                    <span aria-hidden="true" className="size-4 animate-spin rounded-full border-2 border-line border-t-copper" />
                    Chargement du devis…
                </output>
            )}

            {error && (
                <div role="alert" className="flex flex-col gap-4 rounded-sm border border-danger/20 bg-danger-soft p-5 text-sm text-danger sm:flex-row sm:items-center sm:justify-between">
                    <p>{error}</p>
                    <button
                        type="button"
                        onClick={() => setRetryKey((key) => key + 1)}
                        className="min-h-10 shrink-0 self-start rounded-sm border border-danger/30 px-4 font-semibold transition-colors hover:bg-white/60 sm:self-auto"
                    >
                        Réessayer
                    </button>
                </div>
            )}

            {quote && (
                <>
                    <header className="mb-8 flex flex-col gap-5 border-b border-line pb-7 sm:mb-10 sm:flex-row sm:items-end sm:justify-between">
                        <div className="min-w-0">
                            <p className="mb-3 text-xs font-semibold uppercase tracking-[0.18em] text-copper">Fiche commerciale</p>
                            <h1 className="font-display text-4xl font-medium leading-none text-ink sm:text-5xl">Détail du devis</h1>
                            <p className="mt-4 break-all font-mono text-xs text-muted">{quote.id}</p>
                        </div>
                        <Link to={`/quotes/${encodeURIComponent(quote.id)}/edit`} className="inline-flex min-h-11 shrink-0 items-center justify-center rounded-sm bg-ink px-5 text-sm font-semibold text-surface transition-colors hover:bg-copper">
                            Modifier le devis <span aria-hidden="true" className="ml-2">↗</span>
                        </Link>
                    </header>

                    <section aria-label="Informations du devis" className="mb-10 grid gap-5 border border-line bg-surface p-5 sm:grid-cols-2 sm:p-6">
                        <div>
                            <p className="text-[10px] font-semibold uppercase tracking-[0.14em] text-muted">Identifiant</p>
                            <code className="mt-2 inline-flex max-w-full break-all font-mono text-xs text-ink">{quote.id}</code>
                        </div>
                        <div className="sm:border-l sm:border-line sm:pl-6">
                            <p className="text-[10px] font-semibold uppercase tracking-[0.14em] text-muted">Créé le</p>
                            <p className="mt-2 text-sm font-medium tabular-nums text-ink">{formatDate(quote.created_at)}</p>
                        </div>
                    </section>

                    {currentRevision && (
                        <section aria-label="Révisions du devis">
                            {historicalRevisions.length > 0 && (
                                <div
                                    role="tablist"
                                    aria-label="Révisions du devis"
                                    onKeyDown={handleTabKeyDown}
                                    className="mb-6 flex gap-1 border-b border-line"
                                >
                                    <button
                                        id="current-revision-tab"
                                        type="button"
                                        role="tab"
                                        aria-selected={activeTab === "current"}
                                        aria-controls="current-revision-panel"
                                        data-tab="current"
                                        tabIndex={activeTab === "current" ? 0 : -1}
                                        onClick={() => setActiveTab("current")}
                                        className={`min-h-11 border-b-2 px-4 text-sm font-semibold transition-colors ${activeTab === "current" ? "border-copper text-copper" : "border-transparent text-muted hover:text-ink"}`}
                                    >
                                        Révision courante <span className="ml-1 font-mono text-xs">{currentRevision.version}</span>
                                    </button>
                                    <button
                                        id="revision-history-tab"
                                        type="button"
                                        role="tab"
                                        aria-selected={activeTab === "history"}
                                        aria-controls="revision-history-panel"
                                        data-tab="history"
                                        tabIndex={activeTab === "history" ? 0 : -1}
                                        onClick={() => setActiveTab("history")}
                                        className={`min-h-11 border-b-2 px-4 text-sm font-semibold transition-colors ${activeTab === "history" ? "border-copper text-copper" : "border-transparent text-muted hover:text-ink"}`}
                                    >
                                        Historique <span className="ml-1 font-mono text-xs">{historicalRevisions.length}</span>
                                    </button>
                                </div>
                            )}

                            {activeTab === "current" && (
                                <div
                                    id="current-revision-panel"
                                    role={historicalRevisions.length > 0 ? "tabpanel" : undefined}
                                    aria-labelledby={historicalRevisions.length > 0 ? "current-revision-tab" : undefined}
                                    tabIndex={historicalRevisions.length > 0 ? 0 : undefined}
                                    className="space-y-4 focus-visible:outline-2 focus-visible:outline-copper"
                                >
                                    <div className="flex items-end justify-between gap-4">
                                        <div>
                                            <p className="mb-2 text-[10px] font-semibold uppercase tracking-[0.14em] text-copper">Version active</p>
                                            <h2 className="font-display text-3xl font-medium text-ink sm:text-4xl">Révision courante</h2>
                                        </div>
                                        {historicalRevisions.length > 0 && (
                                            <span className="shrink-0 font-mono text-xs text-muted">{historicalRevisions.length} ancienne{historicalRevisions.length > 1 ? "s" : ""} version{historicalRevisions.length > 1 ? "s" : ""}</span>
                                        )}
                                    </div>
                                    <RevisionCard revision={currentRevision} />
                                </div>
                            )}

                            {activeTab === "history" && historicalRevisions.length > 0 && (
                                <div
                                    id="revision-history-panel"
                                    role="tabpanel"
                                    aria-labelledby="revision-history-tab"
                                    tabIndex={0}
                                    className="space-y-5 focus-visible:outline-2 focus-visible:outline-copper"
                                >
                                    <div className="mb-5 flex items-end justify-between gap-4">
                                        <div>
                                            <p className="mb-2 text-[10px] font-semibold uppercase tracking-[0.14em] text-copper">Versions précédentes</p>
                                            <h2 className="font-display text-3xl font-medium text-ink sm:text-4xl">Historique des révisions</h2>
                                        </div>
                                        <span className="shrink-0 font-mono text-xs text-muted">{String(historicalRevisions.length).padStart(2, "0")}</span>
                                    </div>
                                    {historicalRevisions.map((revision) => (
                                        <RevisionCard key={revision.version} revision={revision} />
                                    ))}
                                </div>
                            )}
                        </section>
                    )}
                </>
            )}
        </main>
    );
}
