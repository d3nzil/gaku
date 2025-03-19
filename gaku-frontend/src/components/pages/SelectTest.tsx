// component to select what to study

import { useState, useEffect, useRef } from 'react';
import api from "../../services/api";
import Select from 'react-select';
import { useCommonState } from '../CommonState';
import { CardSource } from '../../types/CardTypes';
import { useNavigate } from 'react-router-dom';
import { TestStatusMessage, CardType } from '../../types/CardTypes';

type CardTypeOption = { value: CardType, label: string };

const SelectTest = () => {
    const context = useCommonState();
    if (!context)
    {
        throw new Error('CommonStateProvider not found');
    }

    // server test state
    const [numDueCards, setNumDueCards] = useState<number>(0);
    const [numAnyStateCards, setNumAnyStateCards] = useState<number>(0);
    const [numNewCards, setNumNewCards] = useState<number>(0);
    const [numStudiedCards, setNumStudiedCards] = useState<number>(0);
    const [testSessionStatus, setTestSessionStatus] = useState<TestStatusMessage | null>(null);
    const [availableSources, setAvailableSources] = useState<CardSource[]>([]);

    // internal state
    const [markAnswers, setMarkAnswers] = useState(true);
    const [selectedSources, setSelectedSources] = useState<CardSource[]>([]);
    const [numCardsToStudy, setNumCardsToStudy] = useState(10);
    const [numDueStats, setNumDueStats] = useState<{ [key: string]: number }>({});
    const [numRecentMistakesStats, setNumRecentMistakesStats] = useState<{ [key: string]: number }>({});
    const [numMistakesSinceTime, setNumMistakesSinceTime] = useState<number | null>(null);
    const [selectedCardTypes, setSelectedCardTypes] = useState<CardType[]>([]);
    const [generateExtraQuestions, setGenerateExtraQuestions] = useState(true);

    // inputs
    const [numHoursSince, setNumHoursSince] = useState(12);
    const [numDaysSince, setNumDaysSince] = useState(0);

    // other hooks
    const navigate = useNavigate();

    // header
    const headerRef = useRef<HTMLHeadingElement | null>(null);


    const createFilter = () => {
        return {
            card_sources: selectedSources,
            card_types: selectedCardTypes,
            search_text: '',
            start_index: null,
            num_cards: numCardsToStudy,
        };
    }
    const createStartRequest = () => {
        return {
            card_sources: selectedSources,
            card_types: selectedCardTypes,
            search_text: '',
            start_index: null,
            num_cards: numCardsToStudy,
            mark_answers: markAnswers,
            generate_extra_questions: generateExtraQuestions,
        };
    }

    const updateMistakesSince = () => {
        // create filter object
        const filter = createFilter();
        // need to convert to seconds
        const numSecondsSince = numHoursSince * 3600 + numDaysSince * 86400;
        api.getNumRecentMistakesSince(filter, numSecondsSince).then((mistakes) => {
            setNumMistakesSinceTime(mistakes);
        });
    }


    const updateStats = () => {
        const filter = createFilter();
        api.getNumDueCards(filter).then((dueCards) => {
            setNumDueCards(dueCards);
        });
        api.getNumRecentMistakes().then((recentMistakes) => {
            setNumRecentMistakesStats(recentMistakes);
        });
        // get the upcoming cards numbers
        api.getNumDueStats().then((upcoming) => {
            setNumDueStats(upcoming);
        });
        // get the number of new cards
        api.getNumNewCards(filter).then((newCards) => {
            setNumNewCards(newCards);
        });
        // update number of any state cards
        api.getNumAnyStateCards(filter).then((anyStateCards) => {
            setNumAnyStateCards(anyStateCards);
        });
        // update number of studied cards
        api.getNumStudiedCards(filter).then((numStudiedCards) => {
            setNumStudiedCards(numStudiedCards)
        })
        updateMistakesSince();
    }


    // initialize the page
    useEffect(() => {
        document.title = "Gaku - Select Test";
        updateStats();
        if (headerRef.current)
        {
            headerRef.current.scrollIntoView();
        }
    }, []);


    // get the number of recent mistakes since specified time
    useEffect(() => {
        updateMistakesSince();
    }, [numHoursSince, numDaysSince]);

    // update the stats when the selected sources change
    useEffect(() => {
        updateStats();
    }, [selectedSources, selectedCardTypes]);

    // update the test session status
    useEffect(() => {
        context.updateTestSessionStatus();

        // if sessions is active, get the status
        if (context.testSessionActive)
        {
            api.getTestStatus().then((status) => {
                setTestSessionStatus(status);
            });
        }
    }, [context.testSessionActive]);

    // get the available sources
    useEffect(() => {
        api.getSources().then((sources) => {
            setAvailableSources(sources);
        });
    }, []);

    const startTestDue = () => {
        const start_request = createStartRequest();
        api.startTestDue(start_request).then(() => {
            navigate('/test');
        });
    }

    const startTestNew = () => {
        const start_request = createStartRequest();
        api.startTestNew(start_request).then(() => {
            navigate('/test');
        });
    }

    const startTestStudied = () => {
        const start_request = createStartRequest();
        api.startTestStudied(start_request).then(() => {
            navigate('/test');
        });
    }

    const startTestAnyState = () => {
        const start_request = createStartRequest();
        api.startTestAll(start_request).then(() => {
            navigate('/test');
        });
    }

    const startTestRecentMistakes = () => {
        // create start request
        const start_request = createStartRequest();
        // need to convert to seconds
        const numSecondsSince = numHoursSince * 3600 + numDaysSince * 86400;
        api.startTestRecentMistakes(start_request, numSecondsSince).then(() => {
            navigate('/test');
        });
    }

    const continueTest = () => {
        navigate('/test');
    }

    const getDueStatText = (key: string): string => {
        // mapping to prettier due text
        if (key === "0")
        {
            return "Due by end of day";
        }
        else if (key === "1")
        {
            return "Due tomorrow";
        }
        else
        {
            return `Due in ${key} days`;
        }
    }

    const getSourceLabel = (source_id: string) => {
        const source = availableSources.find((source) => source.source_id === source_id);
        // label should be source_name + source_section, separated by a dash
        return source ? `${source.source_name} - ${source.source_section}` : source_id;
    }


    return (
        <div style={{ display: "flex", justifyContent: "center", width: "100%" }}>
            <div style={{ width: "100%", maxWidth: "40em" }}>
                <h2 ref={headerRef}>Study Selection</h2>
                <div style={{ display: 'flex', gap: "1em", border: "1px solid grey", padding: "0.5em", borderRadius: "0.5em", marginBottom: "0.5em" }}>
                    <div style={{ flex: 1 }}>
                        <h3 style={{ margin: "0 0", padding: "0.5em 0" }} >Test status</h3>
                        Due cards: {numDueCards}<br />
                        New cards: {numNewCards}<br />
                        Studied cards: {numStudiedCards}<br />
                        Any state cards: {numAnyStateCards}<br />
                    </div>
                    {numDueStats ? (
                        <div style={{ flex: 1 }}>
                            <h3 style={{ margin: "0 0", padding: "0.5em 0" }} >Due card forecast</h3>
                            <table>
                                <tbody>
                                    {Object.keys(numDueStats).map((key) => (
                                        <tr key={key}>
                                            <td>{getDueStatText(key)}</td>
                                            <td style={{ textAlign: "right" }}>+{numDueStats[key]}</td>
                                        </tr>
                                    ))}
                                </tbody>
                            </table>
                        </div>
                    ) : (<></>)}

                </div>


                {context.testSessionActive ? (
                    <div style={{ flex: 1, border: "1px solid grey", padding: "0.5em", borderRadius: "0.5em", marginBottom: "0.5em" }}>
                        <h3 style={{ margin: "0 0", padding: "0.5em 0" }} >Current test session</h3>
                        <div style={{ display: 'flex', flexDirection: "row", gap: "0.5em" }}>
                            <div style={{ flex: 1 }}>
                                {testSessionStatus?.cards_completed}/{testSessionStatus?.cards_total} cards completed ({testSessionStatus?.questions_completed}/{testSessionStatus?.questions_total} questions)
                            </div>
                            <div style={{ flex: 1 }}>
                                <button onClick={continueTest}>Continue Test</button>
                            </div>
                        </div>
                    </div>
                ) : (<></>)
                }

                <div style={{ display: 'flex', flexDirection: "column", gap: "0.5em", border: "1px solid grey", padding: "0.5em", borderRadius: "0.5em", marginBottom: "0.5em" }}>
                    <h3 style={{ margin: "0em" }}>New Test Settings</h3>
                    <div style={{ display: 'flex', gap: "1em" }}>
                        {/* radio button to select if questions should be marked */}
                        <div style={{ flex: 1 }}>
                            <h4 style={{ margin: "0.25em 0" }}>Test type</h4>
                            <input type="radio" id="markAnswers" name="markAnswers" value="true" checked={markAnswers} onChange={() => setMarkAnswers(true)} />
                            <label htmlFor="markAnswers">Standard test</label>
                            <br />
                            <input type="radio" id="dontMarkAnswers" name="markAnswers" value="false" checked={!markAnswers} onChange={() => setMarkAnswers(false)} />
                            <label htmlFor="dontMarkAnswers">Practice test (not marked)</label>
                        </div>
                        <div style={{ flex: 1 }}>
                            <div style={{ flex: 1 }}>
                                Number of cards to study (0 for all):<br />
                                <input type="number" min={0} value={numCardsToStudy} onChange={(e) => setNumCardsToStudy(parseInt(e.target.value))} />
                                <br /><br />
                                Generate extra questions&nbsp;
                                <input type="checkbox" checked={generateExtraQuestions} onChange={() => setGenerateExtraQuestions(!generateExtraQuestions)} />
                                <br />
                                <i>Tests kanji for vocab and radicals for kanji</i>
                            </div>
                        </div>
                    </div>
                    <div style={{ display: 'flex', gap: "0.5em" }}>
                        <div style={{ flex: 1.5 }}>
                            {/* select sources to study */}
                            <b>Select sources</b>
                            <Select
                                isMulti
                                options={availableSources.map((source) => ({ value: source, label: getSourceLabel(source.source_id) }))}
                                value={selectedSources.map((source) => ({ value: source, label: getSourceLabel(source.source_id) }))}
                                onChange={(selected) => setSelectedSources(selected.map((source) => source.value))}
                                className='react-select'
                            />
                        </div>
                    </div>
                    <div style={{ flex: 1 }}>
                        <b>Select card types</b>
                        <Select<CardTypeOption, true>
                            isMulti
                            options={[
                                { value: CardType.KANJI, label: 'Kanji' },
                                { value: CardType.VOCABULARY, label: 'Vocabulary' },
                                { value: CardType.RADICAL, label: 'Radical' },
                                { value: CardType.ONOMATOPOEIA, label: "Onomatopoeia" },
                                { value: CardType.MULTI_CARD, label: 'Multi Card' },
                                { value: CardType.QUESTION, label: 'Custom Question' },
                            ]}
                            value={selectedCardTypes.map((type) => ({ value: type, label: type }))}
                            onChange={(selected) => setSelectedCardTypes(selected.map((type) => type.value))}
                            className='react-select'
                        />
                    </div>

                </div>
                <div style={{ display: 'flex', flexDirection: "column", gap: "0.5em", border: "1px solid grey", padding: "0.5em", borderRadius: "0.5em", marginBottom: "0.5em" }}>

                    <div style={{ display: 'flex', gap: "1em", flexDirection: "row", flexWrap: "wrap" }}>
                        {/* start test buttons */}
                        <button onClick={startTestDue} disabled={numDueCards === 0}>Study Due Cards</button>
                        <button onClick={startTestNew} disabled={numNewCards == 0}>Study New Cards</button>
                        <button onClick={startTestStudied} disabled={numStudiedCards == 0}>Study Studied Cards</button>
                        <button onClick={startTestAnyState}>Study Any State Cards</button>
                    </div>
                </div>

                <div style={{ display: 'flex', flexDirection: "row", gap: "0.5em", border: "1px solid grey", padding: "0.5em", borderRadius: "0.5em", marginBottom: "0.5em" }}>
                    <div style={{ flex: 1 }}>
                        <h3 style={{ margin: "0.25em 0" }}>Recent mistakes</h3>
                        <table>
                            <tbody>
                                {Object.keys(numRecentMistakesStats).map((key) => (
                                    <tr key={key}>
                                        <td><a href="#" onClick={(e) => { e.preventDefault(); setNumDaysSince(parseInt(key)); setNumHoursSince(0); }}>{key} day(s) ago</a></td>
                                        <td style={{ textAlign: "right" }}>+{numRecentMistakesStats[key]}</td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>
                    <div style={{ flex: 1 }}>
                        <h3 style={{ margin: "0.25em 0" }}>Mistakes since</h3>
                        <div style={{ display: 'flex', gap: "0.5em" }}>
                            <input type="number" value={numDaysSince} min={0} max={7} onChange={(e) => setNumDaysSince(parseInt(e.target.value))} style={{ width: "3em" }} />
                            <label>Days</label>
                            <input type="number" value={numHoursSince} min={0} max={23} onChange={(e) => setNumHoursSince(parseInt(e.target.value))} style={{ width: "3em" }} />
                            <label>Hours</label>
                        </div>
                        <br />
                        {numMistakesSinceTime !== null ? (
                            <div>
                                {numMistakesSinceTime} mistakes since {numDaysSince} days and {numHoursSince} hours ago
                                <br />
                                {numCardsToStudy !== 0 ? (
                                    <><i>Limited to {numCardsToStudy} cards (as set above)</i></>
                                ) : (<></>)}
                            </div>
                        ) : (<></>)}

                        <br />
                        <div>
                            <button onClick={startTestRecentMistakes}>Practice recent mistakes</button>
                        </div>
                    </div >
                </div>
            </div>
        </div >
    );
}

export default SelectTest;
