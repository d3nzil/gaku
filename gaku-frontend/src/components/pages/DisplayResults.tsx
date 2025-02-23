import { useState, useEffect } from 'react';
import api from "../../services/api";
import { TestResults } from '../../types/CardTypes';
import { useNavigate } from 'react-router-dom';

const DisplayResults = () => {
    const [results, setResults] = useState<TestResults | null>(null);
    const navigate = useNavigate();

    useEffect(() => {
        document.title = "Gaku - Test Results";
        api.getTestResults().then(setResults);
    }, []);

    const practiceFailedCards = () => {
        api.practiceFailedCards().then(() => {
            navigate('/test');
        });
    }

    const practiceAllCards = () => {
        api.practiceAllCards().then(() => {
            navigate('/test');
        });
    }


    return (
        <div style={{ display: "flex", justifyContent: 'center', width: "100%" }}>
            <div style={{ display: "flex", width: "100%", maxWidth: "30em" }}>
                <div style={{ flex: "1", border: "1px solid grey", padding: "0.5em", borderRadius: "0.5em" }} >
                    <h1>Test Results</h1>
                    {results === null ? (
                        <p>Loading...</p>
                    ) : (
                        <>
                            <p>Number of cards: {results.total_cards}</p>
                            <p>Number of correct answers: {results.correct_responses}</p>
                            <p>Number of incorrect answers: {results.incorrect_responses}</p>
                            {results.stats.map((stat, index) => (
                                <p key={index}>{stat}</p>
                            ))}
                            <br />
                            <div style={{ display: "flex", flexDirection: "row", gap: "1em" }}>
                                <input type="button" value="Practice failed cards" onClick={practiceFailedCards} />
                                <input type="button" value="Practice all cards" onClick={practiceAllCards} />
                            </div>
                        </>
                    )}
                </div>
            </div>
        </div >
    );
}

export default DisplayResults;