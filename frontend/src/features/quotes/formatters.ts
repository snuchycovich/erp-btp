const currencyFormatter = new Intl.NumberFormat("fr-FR", {
    style: "currency",
    currency: "EUR",
});

const dateFormatter = new Intl.DateTimeFormat("fr-FR", {
    dateStyle: "medium",
    timeStyle: "short",
});

const statusLabels: Record<string, string> = {
    draft: "Brouillon",
    pending_approval: "En attente",
    accepted: "Accepté",
    rejected: "Refusé",
};

export function formatCurrency(value: string): string {
    return currencyFormatter.format(Number(value));
}

export function formatStatus(status: string): string {
    return statusLabels[status] ?? status.replaceAll("_", " ");
}

export function formatDate(value: string): string {
    return dateFormatter.format(new Date(value));
}
