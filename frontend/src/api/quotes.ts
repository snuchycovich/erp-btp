import { apiClient } from "./client";

import type {
    CreateQuoteRequest,
    CreateQuoteResponse,
    QuoteDetailResponse,
    QuoteSummary,
} from "../features/quotes/types";
import axios from "axios";

function getHttpStatus(error: unknown) : number | undefined {
    return axios.isAxiosError(error) ? error.response?.status : undefined
}

export async function listQuotes(): Promise<QuoteSummary[]> {
    try {
        const response = await apiClient.get<QuoteSummary[]>("/quotes");
        return response.data
    } catch (error) {
        const status = getHttpStatus(error);
        throw new Error(
            status
                ? `Unable to load quotes (HTTP ${status})`
                : "Unabled to load quote"
        )
    }
}

export async function getQuoteById(
    quoteId: string,
): Promise<QuoteDetailResponse> {
    try {
        const response = await apiClient.get<QuoteDetailResponse>(
            `/quotes/${encodeURIComponent(quoteId)}`
        );
        return response.data;
    } catch (error) {
        const status = getHttpStatus(error);

        if (status === 404) {
            throw new Error("This quote doesn't exist.");
        }

        throw new Error(
            status
                ? `Unable to load quote (HTTP ${status})`
                : "Unable to load quote",
        );
    }
}

export async function createQuote(
    payload: CreateQuoteRequest,
): Promise<CreateQuoteResponse> {
    try {
        const response = await apiClient.post<CreateQuoteResponse>(
            "/quotes",
            payload,
        );
        return response.data
    } catch (error) {
        if (axios.isAxiosError(error)) {
            console.error("API error:", error.response?.data);
        }

        const status = getHttpStatus(error);
        throw new Error(
            status
                ? `Quote creation failed (HTTP ${status})`
                : "Quote creation failed",
        );
    }
}
