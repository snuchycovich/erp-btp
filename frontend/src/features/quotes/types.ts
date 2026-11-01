export type QuoteItemInput = {
    description: string;
    quantity: string;
    unit_price: string;
}

export type CreateQuoteRequest = {
    items: QuoteItemInput[];
}

export type CreateQuoteResponse = {
    id: string;
    revision: number;
    status: string;
    total_ht: string;
}
