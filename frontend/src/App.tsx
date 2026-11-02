import {
    BrowserRouter,
    Navigate,
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
            <Routes>
                <Route path="/" element={<Navigate to="/quotes" replace/>}/>
                <Route path="/quotes" element={<QuotesList />}/>
                <Route path="/quotes/new" element={<QuoteForm />}/>
                <Route
                    path="/quotes/:quoteId"
                    element={<QuoteDetailRoute/>}/>
                <Route path="*" element={<NotFound/>}/>
            </Routes>
        </BrowserRouter>
    );
}
