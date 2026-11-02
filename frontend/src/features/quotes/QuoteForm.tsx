import { useState } from "react"
import type { SubmitEvent } from "react"
import { useNavigate } from "react-router-dom"

import { createQuote } from "../../api/quotes"

type QuoteItem = {
    description: string;
    quantity: string;
    unit_price: string;
}

const initialItems: QuoteItem[] = [
    { description: "Pose de carrelage", quantity: "10", unit_price: "45.50" },
    { description: "Installation électrique", quantity: "2", unit_price: "120.00" },
]

export function QuoteForm() {
    const [items, setItems] = useState<QuoteItem[]>(initialItems);
    const [isSubmitting, setIsSubmitting] = useState<boolean>(false);
    const [error, setError] = useState<string | null>(null);
    const [createdId, setCreatedId] = useState<string | null>(null);

    const navigate = useNavigate();

    function updateItem(
        index: number,
        field: keyof QuoteItem,
        value: string
    ): void {
        setItems((previous) =>
            previous.map((item, i) =>
                i === index ? { ...item, [field]: value } : item
            )
        );
    }

    async function handleSubmit(event: SubmitEvent<HTMLFormElement>): Promise<void> {
        event.preventDefault();

        if (isSubmitting) return;

        setIsSubmitting(true);
        setError(null);
        setCreatedId(null);

        try {
            const quote = await createQuote({ items });
            setCreatedId(quote.id);
            void navigate(`/quotes/${encodeURIComponent(quote.id)}`);
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

    return (
        <form onSubmit={handleSubmit}>
            <h1>Créer un devis</h1>
            {items.map((item, index) => (
                <div key={index}>
                    <input
                        aria-label={`Description ${index +1}`}
                        value={item.description}
                        onChange={(event) =>
                         updateItem(index, "description", event.target.value)
                        }
                    />
                    <input
                        aria-label={`Quantité ${index + 1}`}
                        type="number"
                        min="0.001"
                        step="any"
                        value={item.quantity}
                        onChange={(event) =>
                        updateItem(index, "quantity", event.target.value)
                        }
                    />

                    <input
                        aria-label={`Prix unitaire ${index + 1}`}
                        type="number"
                        min="0"
                        step="any"
                        value={item.unit_price}
                        onChange={(event) =>
                        updateItem(index, "unit_price", event.target.value)
                        }
                    />
                </div>
            ))}

            <button type="submit" disabled={isSubmitting}>
                {isSubmitting ? "Création..." : "Créee le devis"}
            </button>

            {error && <p role="alert">{error}</p>}

            {createdId && (
                <output>
                    Devis créé avec succès : {createdId}
                </output>
            )}
        </form>
    );
}
