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
        <form onSubmit={handleSubmit}>
            <h1>{quoteId ? "Modifier le devis" : "Créer un devis"}</h1>
            {isLoadingQuote && <output>Chargement du devis…</output>}
            {quoteId && !isLoadingQuote && error && (
                <p role="alert">
                    {error} <Link to={`/quotes/${encodeURIComponent(quoteId)}`}>Retour au devis</Link>
                </p>
            )}
            {!isLoadingQuote && !(quoteId && error) && (
                <>
            <fieldset disabled={isSubmitting}>
                <legend>Lignes du devis</legend>
            {items.map((item, index) => (
                <div key={item.id}>
                    <input
                        aria-label={`Description ${index +1}`}
                        required
                        value={item.description}
                        onChange={(event) =>
                         updateItem(item.id, "description", event.target.value)
                        }
                    />
                    <input
                        aria-label={`Quantité ${index + 1}`}
                        type="number"
                        required
                        min="0.001"
                        step="any"
                        value={item.quantity}
                        onChange={(event) =>
                        updateItem(item.id, "quantity", event.target.value)
                        }
                    />

                    <input
                        aria-label={`Prix unitaire ${index + 1}`}
                        type="number"
                        required
                        min="0"
                        step="any"
                        value={item.unit_price}
                        onChange={(event) =>
                        updateItem(item.id, "unit_price", event.target.value)
                        }
                    />
                    {items.length > 1 && (
                        <button
                            type="button"
                            aria-label={`Supprimer la ligne ${index + 1}`}
                            onClick={() => removeItem(item.id)}
                        >
                            Supprimer
                        </button>
                    )}
                </div>
            ))}
            <button type="button" onClick={addItem}>Ajouter une ligne</button>
            </fieldset>

            <button type="submit" disabled={isSubmitting || items.length === 0}>
                {submitLabel}
            </button>

            {error && !quoteId && <p role="alert">{error}</p>}

            {createdId && (
                <output>
                    Devis créé avec succès : {createdId}
                </output>
            )}
                </>
            )}
        </form>
    );
}
