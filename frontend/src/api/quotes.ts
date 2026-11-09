import { apiClient } from "./client";

import type {
    CreateQuoteRequest,
    CreateQuoteResponse,
    QuoteDetailResponse,
    QuoteSummary,
    UpdateQuoteRequest,
    UpdateQuoteResponse,
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

export async function updateQuote(
    quoteId: string,
    payload: UpdateQuoteRequest,
): Promise<UpdateQuoteResponse> {
    try {
        const response = await apiClient.patch<UpdateQuoteResponse>(
            `/quotes/${encodeURIComponent(quoteId)}`,
            payload,
        );
        return response.data;
    } catch (error) {
        const status = getHttpStatus(error);

        if (status === 404) {
            throw new Error("Ce devis n'existe plus.");
        }
        if (status === 409) {
            throw new Error("Le devis a été modifié ailleurs. Rechargez-le avant de réessayer.");
        }

        throw new Error(
            status
                ? `La mise à jour du devis a échoué (HTTP ${status})`
                : "La mise à jour du devis a échoué",
        );
    }
}
