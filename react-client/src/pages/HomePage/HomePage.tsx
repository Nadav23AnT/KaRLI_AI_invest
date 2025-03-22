import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { API_BASE_URL } from '../../enums';
import "./homePage.css";

interface SummaryData {
    balance: number;
    overallProfit: number;
    lastTrades: { id: number; amount: number; profitLoss: number }[];
    availableCash: number;
    tradingStatus: string;
}

export default function HomePage() {
    const navigate = useNavigate();
    const [data, setData] = useState<SummaryData | null>(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    
    const username = localStorage.getItem("username");
    const isAuthenticated = localStorage.getItem("isAuthenticated") === "true";

    // Redirect to login if not authenticated
    useEffect(() => {
        if (!isAuthenticated || !username) {
            navigate("/");
        }
    }, [isAuthenticated, username, navigate]);

    // Fetch summary data for the logged-in user
    useEffect(() => {
        if (isAuthenticated && username) {
            fetch(`${API_BASE_URL}/summary`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ username })
            })
                .then((res) => res.json())
                .then((data) => {
                    setData(data);
                    setLoading(false);
                })
                .catch(() => {
                    setError("Failed to load data.");
                    setLoading(false);
                });
        }
    }, [isAuthenticated, username]);

    const handleStopTrading = () => {
        fetch(`${API_BASE_URL}/stop-trading`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ username })
        })
            .then((res) => res.json())
            .then((updatedData) => {
                if (data) {
                    setData({ ...data, tradingStatus: updatedData.tradingStatus });
                }
            });
    };

    if (!isAuthenticated) return null; // Prevent rendering before redirect

    if (loading) return <p>Loading...</p>;
    if (error) return <p>{error}</p>;

    return (
        <div className="container">
            <h1>Welcome, {username}!</h1>

            <div className="section">
                <h2>Activity Status</h2>
                <p className={`status ${data?.tradingStatus === "Active" ? "active" : "stopped"}`}>
                    {data?.tradingStatus}
                </p>
            </div>

            <div className="section">
                <h2>User Balance</h2>
                <p className="balance">${data?.balance.toFixed(2)}</p>
            </div>

            <div className="section">
                <h2>Overall Profit</h2>
                <p className={`profit ${data?.overallProfit! >= 0 ? "positive" : "negative"}`}>
                    {data?.overallProfit.toFixed(2)}%
                </p>
            </div>

            <div className="section">
                <h2>Last Trades</h2>
                <ul className="last-trades">
                    {data?.lastTrades.map((trade) => (
                        <li key={trade.id} className={`trade-item ${trade.profitLoss >= 0 ? "trade-profit" : "trade-loss"}`}>
                            Trade #{trade.id}: ${trade.amount.toFixed(2)} | 
                            {trade.profitLoss >= 0 ? " Profit " : " Loss "} 
                            {trade.profitLoss.toFixed(2)}%
                        </li>
                    ))}
                </ul>
            </div>

            <div className="section">
                <h2>Available Cash</h2>
                <p className="cash">${data?.availableCash.toFixed(2)}</p>
            </div>

            <button onClick={handleStopTrading} className="stop-button">
                STOP Trading
            </button>
        </div>
    );
}