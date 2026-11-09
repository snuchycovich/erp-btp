import { useEffect, useState } from "react"
import type { SubmitEvent } from "react"
import { Link, useNavigate } from "react-router-dom"

import { createQuote, getQuoteById, updateQuote } from "../../api/quotes"
import type { QuoteItemInput } from "./types"

type QuoteFormProps = {
    readonly quoteId?: string;
}

type EditableQuoteItem = QuoteItemInput & {
    readonly id: string;
}

const initialItems: QuoteItemInput[] = [
    { description: "Pose de carrelage", quantity: "10", unit_price: "45.50" },
    { description: "Installation électrique", quantity: "2", unit_price: "120.00" },
]

function createEditableItem(item: QuoteItemInput): EditableQuoteItem {
    return { ...item, id: crypto.randomUUID() };
}

export function QuoteForm({ quoteId }: QuoteFormProps) {
    const [items, setItems] = useState<EditableQuoteItem[]>(() =>
        quoteId ? [] : initialItems.map(createEditableItem)
    );
    const [isLoadingQuote, setIsLoadingQuote] = useState(Boolean(quoteId));
    const [isSubmitting, setIsSubmitting] = useState<boolean>(false);
    const [error, setError] = useState<string | null>(null);
    const [createdId, setCreatedId] = useState<string | null>(null);

    const navigate = useNavigate();

    useEffect(() => {
        if (!quoteId) return;

        const currentQuoteId = quoteId;
        let isCurrent = true;

        async function loadQuote(): Promise<void> {
            setIsLoadingQuote(true);
            setError(null);

            try {
                const quote = await getQuoteById(currentQuoteId);
                if (isCurrent) {
                    const firstRevision = quote.revisions[0];
                    if (!firstRevision) {
                        throw new Error("Ce devis ne contient aucune révision.");
                    }

                    const currentRevision = quote.revisions.reduce(
                        (latest, revision) =>
                            revision.version > latest.version ? revision : latest,
                        firstRevision,
                    );
                    setItems(currentRevision.items.map((item) =>
                        createEditableItem({
                            description: item.description,
                            quantity: item.quantity,
                            unit_price: item.unit_price,
                        })
                    ));
                }
            } catch (caughtError: unknown) {
                if (isCurrent) {
                    setError(
                        caughtError instanceof Error
                            ? caughtError.message
                            : "Impossible de charger le devis.",
                    );
                }
            } finally {
                if (isCurrent) {
                    setIsLoadingQuote(false);
                }
            }
        }

        void loadQuote();

        return () => {
            isCurrent = false;
        };
    }, [quoteId]);

    function updateItem(
        itemId: string,
        field: keyof QuoteItemInput,
        value: string
    ): void {
        setItems((previous) =>
            previous.map((item) =>
                item.id === itemId ? { ...item, [field]: value } : item
            )
        );
    }

    function addItem(): void {
        setItems((previous) => [
            ...previous,
            createEditableItem({ description: "", quantity: "1", unit_price: "0" }),
        ]);
    }

    function removeItem(itemId: string): void {
        setItems((previous) => previous.filter((item) => item.id !== itemId));
    }

    async function handleSubmit(event: SubmitEvent<HTMLFormElement>): Promise<void> {
        event.preventDefault();

        if (isSubmitting) return;

        setIsSubmitting(true);
        setError(null);
        setCreatedId(null);

        try {
            const payloadItems: QuoteItemInput[] = items.map(
                ({ description, quantity, unit_price }) => ({
                    description,
                    quantity,
                    unit_price,
                }),
            );

            if (quoteId) {
                await updateQuote(quoteId, { items: payloadItems });
                void navigate(`/quotes/${encodeURIComponent(quoteId)}`);
            } else {
                const quote = await createQuote({ items: payloadItems });
                setCreatedId(quote.id);
                void navigate(`/quotes/${encodeURIComponent(quote.id)}`);
            }
        } catch (error: unknown) {
            setError(
                error instanceof Error
                ? error.message
                : "An unexpected error ocurred"
            );
        } finally {
            setIsSubmitting(false)
        }


    }

    let submitLabel = "Créer le devis";
    if (quoteId) {
        submitLabel = "Enregistrer les modifications";
    }
    if (isSubmitting) {
        submitLabel = "Enregistrement…";
    }

    return (
        <main className="page-enter">
            <div className="mb-7">
                <Link to={quoteId ? `/quotes/${encodeURIComponent(quoteId)}` : "/quotes"} className="inline-flex items-center gap-2 text-sm font-medium text-muted transition-colors hover:text-copper">
                    <span aria-hidden="true">←</span> Retour {quoteId ? "au devis" : "à la liste"}
                </Link>
            </div>
            <header className="mb-8 border-b border-line pb-7 sm:mb-10">
                <p className="mb-3 text-xs font-semibold uppercase tracking-[0.18em] text-copper">Proposition commerciale</p>
                <h1 className="font-display text-4xl font-medium leading-none text-ink sm:text-5xl">{quoteId ? "Modifier le devis" : "Créer un devis"}</h1>
                <p className="mt-3 max-w-xl text-sm leading-6 text-muted">Détaillez les prestations et leur tarification.</p>
            </header>

            {isLoadingQuote && (
                <output className="flex min-h-40 items-center justify-center gap-3 rounded-sm border border-line bg-surface text-sm text-muted">
                    <span aria-hidden="true" className="size-4 animate-spin rounded-full border-2 border-line border-t-copper" />
                    Chargement du devis…
                </output>
            )}
            {quoteId && !isLoadingQuote && error && (
                <div role="alert" className="flex flex-col gap-3 rounded-sm border border-danger/20 bg-danger-soft p-5 text-sm text-danger sm:flex-row sm:items-center sm:justify-between">
                    <p>{error}</p>
                    <Link to={`/quotes/${encodeURIComponent(quoteId)}`} className="font-semibold underline underline-offset-4">Retour au devis</Link>
                </div>
            )}
            {!isLoadingQuote && !(quoteId && error) && (
                <form onSubmit={handleSubmit} className="space-y-6">
                    <fieldset disabled={isSubmitting} className="overflow-hidden rounded-sm border border-line bg-surface disabled:opacity-70">
                        <legend className="sr-only">Lignes du devis</legend>
                        <div className="border-b border-line px-5 py-4 sm:px-7">
                            <h2 className="text-sm font-semibold text-ink">Prestations</h2>
                            <p className="mt-1 text-xs text-muted">Ajoutez une ligne par prestation ou fourniture.</p>
                        </div>
                        <div className="px-5 sm:px-7">
                            <div className="hidden grid-cols-[minmax(0,1.8fr)_minmax(100px,.7fr)_minmax(130px,.8fr)_40px] gap-3 border-b border-line py-3 text-[10px] font-semibold uppercase tracking-[0.12em] text-muted sm:grid">
                                <span>Désignation</span><span>Quantité</span><span>Prix unitaire HT</span><span />
                            </div>
                            <div className="divide-y divide-line">
                                {items.map((item, index) => (
                                    <div key={item.id} className="grid gap-3 py-5 sm:grid-cols-[minmax(0,1.8fr)_minmax(100px,.7fr)_minmax(130px,.8fr)_40px] sm:items-end">
                                        <label className="grid gap-1.5 text-xs font-medium text-muted">
                                            <span className="sm:sr-only">Désignation de la ligne {index + 1}</span>
                                            <input
                                                aria-label={`Description ${index + 1}`}
                                                required
                                                placeholder="Ex. Pose de carrelage"
                                                value={item.description}
                                                onChange={(event) => updateItem(item.id, "description", event.target.value)}
                                                className="min-h-11 w-full rounded-sm border border-line bg-white px-3 text-sm text-ink outline-none transition focus:border-copper focus:ring-2 focus:ring-copper/15"
                                            />
                                        </label>
                                        <label className="grid gap-1.5 text-xs font-medium text-muted">
                                            <span className="sm:sr-only">Quantité ligne {index + 1}</span>
                                            <input
                                                aria-label={`Quantité ${index + 1}`}
                                                type="number"
                                                required
                                                min="0.001"
                                                step="any"
                                                value={item.quantity}
                                                onChange={(event) => updateItem(item.id, "quantity", event.target.value)}
                                                className="min-h-11 w-full rounded-sm border border-line bg-white px-3 text-sm tabular-nums text-ink outline-none transition focus:border-copper focus:ring-2 focus:ring-copper/15"
                                            />
                                        </label>
                                        <label className="grid gap-1.5 text-xs font-medium text-muted">
                                            <span className="sm:sr-only">Prix unitaire HT ligne {index + 1}</span>
                                            <span className="relative">
                                                <input
                                                    aria-label={`Prix unitaire ${index + 1}`}
                                                    type="number"
                                                    required
                                                    min="0"
                                                    step="any"
                                                    value={item.unit_price}
                                                    onChange={(event) => updateItem(item.id, "unit_price", event.target.value)}
                                                    className="min-h-11 w-full rounded-sm border border-line bg-white px-3 pr-10 text-sm tabular-nums text-ink outline-none transition focus:border-copper focus:ring-2 focus:ring-copper/15"
                                                />
                                                <span aria-hidden="true" className="pointer-events-none absolute right-3 top-1/2 -translate-y-1/2 text-xs text-muted">€</span>
                                            </span>
                                        </label>
                                        <div className="flex justify-end sm:justify-center">
                                            {items.length > 1 && (
                                                <button
                                                    type="button"
                                                    aria-label={`Supprimer la ligne ${index + 1}`}
                                                    title="Supprimer la ligne"
                                                    onClick={() => removeItem(item.id)}
                                                    className="grid size-10 place-items-center rounded-sm text-muted transition-colors hover:bg-danger-soft hover:text-danger focus-visible:outline-2 focus-visible:outline-copper"
                                                >
                                                    <span aria-hidden="true" className="text-2xl font-light leading-none">×</span>
                                                </button>
                                            )}
                                        </div>
                                    </div>
                                ))}
                            </div>
                            <div className="border-t border-line py-4">
                                <button type="button" onClick={addItem} className="inline-flex min-h-10 items-center gap-2 text-sm font-semibold text-copper transition-colors hover:text-copper-dark">
                                    <span aria-hidden="true" className="grid size-6 place-items-center rounded-full border border-copper/30 text-base leading-none">+</span>
                                    Ajouter une prestation
                                </button>
                            </div>
                        </div>
                    </fieldset>

                    {error && !quoteId && <p role="alert" className="rounded-sm border border-danger/20 bg-danger-soft px-4 py-3 text-sm text-danger">{error}</p>}
                    {createdId && <output className="block rounded-sm border border-forest/20 bg-forest-soft px-4 py-3 text-sm text-forest">Devis créé avec succès : {createdId}</output>}

                    <div className="flex flex-col-reverse gap-3 border-t border-line pt-5 sm:flex-row sm:items-center sm:justify-end">
                        <Link to={quoteId ? `/quotes/${encodeURIComponent(quoteId)}` : "/quotes"} className="inline-flex min-h-11 items-center justify-center rounded-sm px-5 text-sm font-medium text-muted transition-colors hover:bg-black/5 hover:text-ink">
                            Annuler
                        </Link>
                        <button type="submit" disabled={isSubmitting || items.length === 0} className="inline-flex min-h-11 items-center justify-center rounded-sm bg-copper px-5 text-sm font-semibold text-white transition-colors hover:bg-copper-dark disabled:cursor-not-allowed disabled:opacity-50">
                            {submitLabel}
                        </button>
                    </div>
                </form>
            )}
        </main>
    );
}
