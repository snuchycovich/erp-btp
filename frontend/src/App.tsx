import {
    BrowserRouter,
    Navigate,
    NavLink,
    Route,
    Routes,
    useParams,
} from "react-router-dom"

import { QuoteForm } from "./features/quotes/QuoteForm";
import { QuotesList } from "./features/quotes/QuotesList";
import { QuoteDetail } from "./features/quotes/QuoteDetail";

function QuoteDetailRoute() {
    const { quoteId } = useParams<{ quoteId: string}>();

    if (!quoteId) {
        return <Navigate to="/quotes" replace />;
    }

    return <QuoteDetail quoteId={quoteId} />;

}

function EditQuoteRoute() {
    const { quoteId } = useParams<{ quoteId: string }>();

    if (!quoteId) {
        return <Navigate to="/quotes" replace />;
    }

    return <QuoteForm quoteId={quoteId} />;
}

function NotFound() {
    return (
        <main>
            <h1>Page introuvable</h1>
            <a href="/quotes">Retur à la liste de devis</a>
        </main>
    );
}

export default function App() {
    return (
        <BrowserRouter>
            <div className="min-h-screen bg-paper text-ink">
                <header className="border-b border-line bg-surface">
                    <div className="mx-auto flex max-w-7xl items-center justify-between gap-5 px-4 py-4 sm:px-6 lg:px-8">
                        <NavLink to="/quotes" className="group flex min-w-0 items-center gap-3">
                            <span className="grid size-11 shrink-0 place-items-center rounded-sm bg-ink font-display text-3xl italic leading-none text-paper transition-colors group-hover:bg-copper">
                                A
                            </span>
                            <span className="min-w-0">
                                <span className="block truncate text-sm font-semibold tracking-[0.12em] text-ink">ATELIER BTP</span>
                                <span className="mt-0.5 block text-[10px] font-medium uppercase tracking-[0.18em] text-muted">Gestion des devis</span>
                            </span>
                        </NavLink>
                        <nav aria-label="Navigation principale" className="flex shrink-0 items-center gap-2 sm:gap-4">
                            <NavLink
                                to="/quotes"
                                end
                                className={({ isActive }) => `hidden rounded-sm px-3 py-2 text-sm font-medium transition-colors sm:inline-flex ${isActive ? "text-copper" : "text-muted hover:text-ink"}`}
                            >
                                Devis
                            </NavLink>
                            <NavLink
                                to="/quotes/new"
                                className="inline-flex min-h-10 items-center justify-center rounded-sm bg-ink px-3 text-xs font-semibold text-surface transition-colors hover:bg-copper sm:px-4 sm:text-sm"
                            >
                                Nouveau devis <span className="ml-2 text-base leading-none" aria-hidden="true">+</span>
                            </NavLink>
                        </nav>
                    </div>
                </header>
                <div className="mx-auto w-full max-w-7xl px-4 py-8 sm:px-6 sm:py-10 lg:px-8 lg:py-14">
                    <Routes>
                        <Route path="/" element={<Navigate to="/quotes" replace/>}/>
                        <Route path="/quotes" element={<QuotesList />}/>
                        <Route path="/quotes/new" element={<QuoteForm />}/>
                        <Route path="/quotes/:quoteId/edit" element={<EditQuoteRoute />}/>
                        <Route path="/quotes/:quoteId" element={<QuoteDetailRoute/>}/>
                        <Route path="*" element={<NotFound/>}/>
                    </Routes>
                </div>
            </div>
        </BrowserRouter>
    );
}
