import type {
    CreateQuoteRequest,
    CreateQuoteResponse,
    QuoteSummary,
} from "../features/quotes/types";

const API_URL = import.meta.env.VITE_API_URL ?? "http://localhost:8000";

export async function listQuotes(): Promise<QuoteSummary[]> {
    const response = await fetch(`${API_URL}/quotes`);

    if (!response.ok) {
        throw new Error(`Unable to load quotes (HTTP ${response.status})`);
    }

    return (await response.json()) as QuoteSummary[];
}

export async function createQuote(
    payload: CreateQuoteRequest,
): Promise<CreateQuoteResponse> {
    const response = await fetch(`${API_URL}/quotes`, {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify(payload),
    });

    if (!response.ok) {
        const body: unknown = await response.json().catch(() => null);
        console.error("API error:", body);
        throw new Error(`Quote creation failed (HTTP ${response.status})`);
    }

    return (await response.json()) as CreateQuoteResponse
}
