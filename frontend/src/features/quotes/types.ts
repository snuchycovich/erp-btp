export type QuoteItemInput = {
    description: string;
    quantity: string;
    unit_price: string;
}

export type CreateQuoteRequest = {
    items: QuoteItemInput[];
}

export type UpdateQuoteRequest = {
    items: QuoteItemInput[];
}

export type CreateQuoteResponse = {
    id: string;
    revision: number;
    status: string;
    total_ht: string;
}

export type UpdateQuoteResponse = CreateQuoteResponse;

export type QuoteSummary = {
    id: string;
    status: string;
    total_ht: string;
}

export type QuoteItemDetail = {
    description: string,
    quantity: string,
    unit_price: string,
}

export type QuoteRevisionDetail = {
    version: number;
    status: string;
    total_ht: string;
    created_at: string;
    items: QuoteItemDetail[];
};

export type QuoteDetailResponse = {
    id: string;
    created_at: string;
    revisions: QuoteRevisionDetail[];
};
